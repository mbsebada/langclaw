import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from loguru import logger

from examples.rentagent_vn.models import ListingSummary, ScrapeResult, TinyFishListingResponse
from examples.rentagent_vn.prompts import build_goal
from examples.rentagent_vn.tinyfish.client import TinyFishClient
from langclaw import Langclaw

ResultCallback = Callable[[Langclaw, str, ScrapeResult, dict[str, Any]], Awaitable[None]]
ProgressCallback = Callable[
    [Langclaw, str, str, str, str, str, dict[str, Any]],
    Awaitable[None],
]
StreamingUrlCallback = Callable[
    [Langclaw, str, str, str, str, dict[str, Any]],
    Awaitable[None],
]
ErrorCallback = Callable[[Langclaw, str, str, str, str, dict[str, Any]], Awaitable[None]]


class BackgroundScrapeRunner:
    def __init__(
        self,
        app: Langclaw,
        result_callback: ResultCallback,
        tinyfish_client: TinyFishClient,
        *,
        progress_callback: ProgressCallback | None = None,
        streaming_url_callback: StreamingUrlCallback | None = None,
        error_callback: ErrorCallback | None = None,
    ) -> None:
        self._app = app
        self._result_callback = result_callback
        self._progress_callback = progress_callback
        self._streaming_url_callback = streaming_url_callback
        self._error_callback = error_callback
        self._tinyfish_client = tinyfish_client
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def start(
        self,
        urls: list[str],
        query: str,
        channel_context: dict[str, Any],
        user_preference: str | None = None,
    ) -> str:
        job_id = uuid4().hex[:12]
        task = asyncio.create_task(
            self._run(job_id, urls, query, user_preference, channel_context),
            name=f"scrape-{job_id}",
        )
        self._tasks[job_id] = task
        logger.info(f"Background scrape {job_id} started — {len(urls)} URLs")
        return job_id

    async def _run(
        self,
        job_id: str,
        urls: list[str],
        query: str,
        user_preference: str | None,
        channel_context: dict[str, Any],
    ) -> None:
        all_listings: list[ListingSummary] = []
        all_errors: list[dict[str, Any]] = []

        try:

            async def _stream_run(url: str) -> None:
                goal = build_goal(url, query, user_preference)
                logger.debug("TinyFish goal for {}: {}", url, goal[:200])

                async for event in self._tinyfish_client.stream_run(url, goal):
                    logger.debug(f"TinyFish event: {event.type}")
                    if event.type == "PROGRESS" and self._progress_callback:
                        await self._progress_callback(
                            self._app,
                            job_id,
                            event.run_id,
                            url,
                            event.type,
                            event.purpose,
                            channel_context,
                        )
                    elif event.type == "STREAMING_URL" and event.streaming_url:
                        if self._streaming_url_callback:
                            await self._streaming_url_callback(
                                self._app,
                                job_id,
                                event.run_id,
                                url,
                                event.streaming_url,
                                channel_context,
                            )
                    elif event.type == "COMPLETE":
                        validated = TinyFishListingResponse.from_raw(event.result_json or {})
                        all_listings.extend(validated.listings)
                        logger.info(
                            "URL {} returned {} listings",
                            url,
                            len(validated.listings),
                        )
                    elif event.type == "ERROR":
                        all_errors.append({"url": url, "error": event.message or "Unknown error"})
                        if self._error_callback:
                            await self._error_callback(
                                self._app,
                                job_id,
                                event.run_id,
                                url,
                                event.message,
                                channel_context,
                            )

            tasks = [_stream_run(url) for url in urls]
            await asyncio.gather(*tasks)

        except Exception:
            logger.exception(f"Background scrape {job_id} failed")
            all_errors.append({"error": f"Background scrape {job_id} failed"})

        # Deliver aggregated results in a single callback.
        combined = ScrapeResult(
            listings=all_listings,
            errors=all_errors,
            urls_scanned=len(urls),
        )
        logger.info(
            "Background scrape {} finished — {} listings, {} errors",
            job_id,
            len(combined.listings),
            len(combined.errors),
        )
        try:
            await self._result_callback(self._app, job_id, combined, channel_context)
        except Exception:
            logger.exception("Failed to deliver result callback for {}", job_id)
        finally:
            self._tasks.pop(job_id, None)
