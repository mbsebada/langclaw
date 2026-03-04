"""Deterministic LangGraph workflow for multi-URL rental scraping.

This is a pure fan-out/collect/normalize pipeline — no LLM calls inside.
It uses TinyFish's SSE streaming for concurrent scraping per URL, then
normalises and deduplicates the results.

The workflow is invoked by the ``search_rentals`` tool and is NOT an agent.
``BackgroundScrapeRunner`` wraps the workflow in an ``asyncio.Task`` so
the calling tool returns immediately while scraping runs in the background.
"""

from __future__ import annotations

import asyncio
import operator
from collections.abc import Awaitable, Callable
from typing import Annotated, Any
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from loguru import logger
from pydantic import BaseModel, Field

from examples.rentagent_vn.models import (
    ListingSummary,
    ScrapeResult,
    TinyFishListingResponse,
)
from examples.rentagent_vn.prompts import build_goal
from examples.rentagent_vn.tinyfish.client import TinyFishClient

# ---------------------------------------------------------------------------
# Callback context (set by BackgroundScrapeRunner before invoking workflow)
# ---------------------------------------------------------------------------

ScrapeCallbacks = dict[str, Any]  # job_id, progress_cb, streaming_url_cb, channel_ctx

_scrape_callbacks: ScrapeCallbacks | None = None


def set_scrape_callbacks(callbacks: ScrapeCallbacks | None) -> None:
    """Inject callbacks for the running scrape job (internal use)."""
    global _scrape_callbacks
    _scrape_callbacks = callbacks


def _get_callbacks() -> ScrapeCallbacks | None:
    return _scrape_callbacks


# ---------------------------------------------------------------------------
# Workflow state
# ---------------------------------------------------------------------------


class ScrapeState(BaseModel):
    """Internal state flowing through the scrape workflow nodes."""

    urls: list[str] = Field(default_factory=list)
    query: str = ""
    user_preference: str | None = None
    goals: list[dict[str, str]] = Field(default_factory=list)
    run_ids: list[str] = Field(default_factory=list)
    raw_results: list[dict[str, Any]] = Field(default_factory=list)
    listings: Annotated[list[dict[str, Any]], operator.add] = Field(default_factory=list)
    errors: Annotated[list[dict[str, Any]], operator.add] = Field(default_factory=list)
    streaming_urls: dict[str, str] = Field(
        default_factory=dict,
        description="Maps source URL to live browser preview URL for FE.",
    )


# ---------------------------------------------------------------------------
# Shared TinyFish client (set by the tool before invoking the workflow)
# ---------------------------------------------------------------------------

_tinyfish: TinyFishClient | None = None


def set_tinyfish_client(client: TinyFishClient) -> None:
    """Inject the TinyFish client for the workflow to use."""
    global _tinyfish
    _tinyfish = client


def _get_client() -> TinyFishClient:
    if _tinyfish is None:
        raise RuntimeError("TinyFish client not set — call set_tinyfish_client first")
    return _tinyfish


# ---------------------------------------------------------------------------
# Workflow nodes
# ---------------------------------------------------------------------------


def build_goals(state: ScrapeState) -> dict[str, Any]:
    """Build a TinyFish goal for each URL based on domain and query."""
    goals: list[dict[str, str]] = []
    for url in state.urls:
        goal_text = build_goal(url, state.query, state.user_preference)
        goals.append({"url": url, "goal": goal_text})
    logger.info("Built {} TinyFish goals", len(goals))
    return {"goals": goals}


async def _consume_stream(
    client: TinyFishClient,
    run_index: int,
    url: str,
    goal: str,
    raw_results: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    streaming_urls: dict[str, str],
) -> None:
    """Consume one SSE stream, invoking callbacks and collecting results."""
    callbacks = _get_callbacks()
    job_id = callbacks.get("job_id", "") if callbacks else ""
    channel_ctx = callbacks.get("channel_context", {}) if callbacks else {}
    progress_cb = callbacks.get("progress_callback") if callbacks else None
    streaming_url_cb = callbacks.get("streaming_url_callback") if callbacks else None

    async for event in client.stream_run(url, goal):
        if event.type == "PROGRESS" and progress_cb:
            try:
                await progress_cb(
                    job_id=job_id,
                    run_index=run_index,
                    url=url,
                    event_type=event.type,
                    purpose=event.purpose or "",
                    channel_context=channel_ctx,
                )
            except Exception:
                logger.exception("progress_callback failed for {}", url)
        elif event.type == "STREAMING_URL" and event.streamingUrl:
            streaming_urls[url] = event.streamingUrl
            if streaming_url_cb:
                try:
                    await streaming_url_cb(
                        job_id=job_id,
                        run_index=run_index,
                        url=url,
                        streaming_url=event.streamingUrl,
                        channel_context=channel_ctx,
                    )
                except Exception:
                    logger.exception("streaming_url_callback failed for {}", url)
        elif event.type == "COMPLETE":
            raw_results.append(
                {
                    "run_id": event.runId or "sse",
                    "status": "COMPLETED",
                    "result": event.resultJson,
                }
            )
            return
        elif event.type == "ERROR":
            logger.error("SSE error for {}: {}", url, event.message or "Unknown error")
            errors.append({"url": url, "error": event.message or "Unknown error"})
            return

    errors.append({"url": url, "error": "SSE stream ended without result"})


async def run_concurrent_streams(state: ScrapeState) -> dict[str, Any]:
    """Run all goals via concurrent SSE streams; collect raw_results and streaming_urls."""
    client = _get_client()
    runs = [{"url": g["url"], "goal": g["goal"]} for g in state.goals]

    if not runs:
        return {"raw_results": [], "errors": [{"error": "No URLs to scrape"}]}

    raw_results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    streaming_urls: dict[str, str] = {}

    tasks = [
        _consume_stream(
            client=client,
            run_index=i,
            url=r["url"],
            goal=r["goal"],
            raw_results=raw_results,
            errors=errors,
            streaming_urls=streaming_urls,
        )
        for i, r in enumerate(runs)
    ]

    await asyncio.gather(*tasks)

    return {
        "raw_results": raw_results,
        "errors": errors,
        "streaming_urls": streaming_urls,
    }


def normalize(state: ScrapeState) -> dict[str, Any]:
    """Parse raw TinyFish results into ListingSummary dicts."""
    listings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for run in state.raw_results:
        status = run.get("status", "UNKNOWN")
        if status != "COMPLETED":
            err = run.get("error") or {}
            if isinstance(err, dict):
                err_msg = err.get("message", "Run did not complete")
            else:
                err_msg = str(err)
            errors.append(
                {
                    "run_id": run.get("run_id"),
                    "status": status,
                    "error": err_msg,
                }
            )
            continue

        result = run.get("result")
        if not result:
            continue

        try:
            validated = TinyFishListingResponse.from_raw(result)
            for summary in validated.listings:
                listings.append(summary.model_dump(exclude_none=True))
        except Exception as exc:
            logger.debug("Failed to validate TinyFish response: {} — {}", run.get("run_id"), exc)

    logger.info("Normalized {} listings from {} runs", len(listings), len(state.raw_results))
    return {"listings": listings, "errors": errors}


def deduplicate(state: ScrapeState) -> dict[str, Any]:
    """Remove duplicate listings (same address + price + area)."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []

    for listing in state.listings:
        key_parts = [
            str(listing.get("address", "")).lower().strip(),
            str(listing.get("price_vnd", "")),
            str(listing.get("area_sqm", "")),
        ]
        key = "|".join(key_parts)

        if key in seen and key != "||":
            continue
        seen.add(key)
        unique.append(listing)

    logger.info("Deduplicated: {} → {} listings", len(state.listings), len(unique))
    return {"listings": unique}


# ---------------------------------------------------------------------------
# Build and compile the workflow graph
# ---------------------------------------------------------------------------


def build_scrape_graph() -> Any:
    """Construct the scrape workflow as a compiled LangGraph graph."""
    builder = StateGraph(ScrapeState)

    builder.add_node("build_goals", build_goals)
    builder.add_node("run_concurrent_streams", run_concurrent_streams)
    builder.add_node("normalize", normalize)
    builder.add_node("deduplicate", deduplicate)

    builder.add_edge(START, "build_goals")
    builder.add_edge("build_goals", "run_concurrent_streams")
    builder.add_edge("run_concurrent_streams", "normalize")
    builder.add_edge("normalize", "deduplicate")
    builder.add_edge("deduplicate", END)

    return builder.compile()


scrape_graph = build_scrape_graph()


ResultCallback = Callable[[str, ScrapeResult, dict[str, Any]], Awaitable[None]]
ProgressCallback = Callable[
    [str, int, str, str, str, dict[str, Any]],
    Awaitable[None],
]
StreamingUrlCallback = Callable[
    [str, int, str, str, dict[str, Any]],
    Awaitable[None],
]


async def run_scrape(
    urls: list[str],
    query: str,
    user_preference: str | None = None,
    job_id: str = "",
    channel_context: dict[str, Any] | None = None,
    progress_callback: ProgressCallback | None = None,
    streaming_url_callback: StreamingUrlCallback | None = None,
) -> ScrapeResult:
    """Run the scrape workflow and return structured results.

    This is the synchronous entry point — prefer ``BackgroundScrapeRunner``
    for production use to avoid blocking the agent.
    """
    if progress_callback or streaming_url_callback:
        set_scrape_callbacks(
            {
                "job_id": job_id,
                "channel_context": channel_context or {},
                "progress_callback": progress_callback,
                "streaming_url_callback": streaming_url_callback,
            }
        )
    else:
        set_scrape_callbacks(None)

    try:
        state = await scrape_graph.ainvoke(
            {
                "urls": urls,
                "query": query,
                "user_preference": user_preference,
            }
        )

        return ScrapeResult(
            listings=[ListingSummary.model_validate(item) for item in state.get("listings", [])],
            errors=state.get("errors", []),
            urls_scanned=len(urls),
            streaming_urls=state.get("streaming_urls") or {},
        )
    finally:
        set_scrape_callbacks(None)


# ---------------------------------------------------------------------------
# Background scrape runner
# ---------------------------------------------------------------------------


class BackgroundScrapeRunner:
    """Fire-and-forget wrapper around the scrape workflow.

    The ``search_rentals`` tool calls :meth:`start` which launches an
    ``asyncio.Task`` and returns a job ID immediately.  When the task
    finishes, it invokes the registered *result_callback* so the caller
    can deliver results to the user's channel (via the message bus).

    Args:
        result_callback: ``async (job_id, ScrapeResult, channel_ctx) -> None``
            called when a scrape job completes.  ``channel_ctx`` is the
            dict originally passed to :meth:`start` so the callback knows
            which channel/user to deliver to.
        progress_callback: Optional ``async (job_id, run_index, url, event_type,
            purpose, channel_ctx) -> None`` called on PROGRESS events.
        streaming_url_callback: Optional ``async (job_id, run_index, url,
            streaming_url, channel_ctx) -> None`` called on STREAMING_URL events.
            FE can use streaming_url for live browser preview iframes.
    """

    def __init__(
        self,
        result_callback: ResultCallback,
        *,
        progress_callback: ProgressCallback | None = None,
        streaming_url_callback: StreamingUrlCallback | None = None,
    ) -> None:
        self._callback = result_callback
        self._progress_callback = progress_callback
        self._streaming_url_callback = streaming_url_callback
        self._tasks: dict[str, asyncio.Task[None]] = {}

    @property
    def active_jobs(self) -> int:
        return len(self._tasks)

    async def start(
        self,
        urls: list[str],
        query: str,
        user_preference: str | None,
        channel_context: dict[str, Any],
    ) -> str:
        """Launch a background scrape and return the job ID immediately."""
        job_id = uuid4().hex[:12]
        task = asyncio.create_task(
            self._run(job_id, urls, query, user_preference, channel_context),
            name=f"scrape-{job_id}",
        )
        self._tasks[job_id] = task
        logger.info("Background scrape {} started — {} URLs", job_id, len(urls))
        return job_id

    async def _run(
        self,
        job_id: str,
        urls: list[str],
        query: str,
        user_preference: str | None,
        channel_context: dict[str, Any],
    ) -> None:
        try:
            result = await run_scrape(
                urls=urls,
                query=query,
                user_preference=user_preference,
                job_id=job_id,
                channel_context=channel_context,
                progress_callback=self._progress_callback,
                streaming_url_callback=self._streaming_url_callback,
            )
            logger.info(
                "Background scrape {} finished — {} listings, {} errors",
                job_id,
                len(result.listings),
                len(result.errors),
            )
            await self._callback(job_id, result, channel_context)
        except Exception:
            logger.exception("Background scrape {} failed", job_id)
            empty = ScrapeResult(
                listings=[],
                errors=[{"error": f"Background scrape {job_id} failed unexpectedly"}],
                urls_scanned=len(urls),
            )
            try:
                await self._callback(job_id, empty, channel_context)
            except Exception:
                logger.exception("Failed to deliver error callback for {}", job_id)
        finally:
            self._tasks.pop(job_id, None)
