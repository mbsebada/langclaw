"""Async TinyFish Web Agent API client.

Wraps the batch and SSE endpoints with proper error handling, exponential
backoff polling, and the ``{"error": ...}`` return convention used by langclaw
tools.

Reference:
    https://docs.tinyfish.ai/api-reference
    https://docs.tinyfish.ai/key-concepts/endpoints
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Callable
from typing import Any

import httpx
from loguru import logger

TINYFISH_BASE = "https://agent.tinyfish.ai"
_BATCH_SUBMIT = f"{TINYFISH_BASE}/v1/automation/run-batch"
_BATCH_GET = f"{TINYFISH_BASE}/v1/runs/batch"
_RUN_SSE = f"{TINYFISH_BASE}/v1/automation/run-sse"

TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "CANCELLED"})


def _api_key() -> str:
    key = os.environ.get("TINYFISH_API_KEY", "")
    if not key:
        raise RuntimeError("TINYFISH_API_KEY environment variable is not set")
    return key


def _headers() -> dict[str, str]:
    return {
        "X-API-Key": _api_key(),
        "Content-Type": "application/json",
    }


class TinyFishClient:
    """Async client for the TinyFish Web Agent API."""

    def __init__(self, timeout: float = 330.0) -> None:
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout

    async def open(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout, connect=30.0),
                headers=_headers(),
            )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _ensure_open(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("TinyFishClient is not open — call .open() first")
        return self._client

    # ------------------------------------------------------------------
    # Batch API — primary path for multi-URL scraping
    # ------------------------------------------------------------------

    async def submit_batch(
        self,
        runs: list[dict[str, Any]],
    ) -> list[str]:
        """Submit up to 100 automation runs in a single request.

        Args:
            runs: List of ``{"url": ..., "goal": ..., "browser_profile": ...}``
                  dicts.  ``browser_profile`` defaults to ``"stealth"``.

        Returns:
            List of ``run_id`` strings.

        Raises:
            RuntimeError: On HTTP or API error.
        """
        client = self._ensure_open()

        for run in runs:
            run.setdefault("browser_profile", "stealth")

        logger.info("Submitting batch of {} TinyFish runs", len(runs))
        resp = await client.post(_BATCH_SUBMIT, json={"runs": runs})

        if resp.status_code != 200:
            raise RuntimeError(f"TinyFish batch submit failed ({resp.status_code}): {resp.text}")

        body = resp.json()
        if body.get("error"):
            raise RuntimeError(f"TinyFish batch error: {body['error']}")

        run_ids: list[str] = body["run_ids"]
        logger.info("Batch submitted — {} run IDs received", len(run_ids))
        return run_ids

    async def poll_batch(
        self,
        run_ids: list[str],
        *,
        initial_delay: float = 3.0,
        max_delay: float = 30.0,
        timeout: float = 300.0,
    ) -> list[dict[str, Any]]:
        """Poll until all runs reach a terminal state.

        Uses exponential backoff starting at *initial_delay* seconds, capped
        at *max_delay*.  Gives up after *timeout* seconds total.

        Returns:
            List of run dicts with ``run_id``, ``status``, ``result``, etc.
        """
        client = self._ensure_open()
        delay = initial_delay
        elapsed = 0.0

        while elapsed < timeout:
            resp = await client.post(_BATCH_GET, json={"run_ids": run_ids})
            if resp.status_code != 200:
                logger.warning("Poll returned {}: {}", resp.status_code, resp.text)
                await asyncio.sleep(delay)
                elapsed += delay
                delay = min(delay * 2, max_delay)
                continue

            body = resp.json()
            data: list[dict[str, Any]] = body.get("data", [])

            pending = [r for r in data if r.get("status") not in TERMINAL_STATUSES]
            if not pending:
                logger.info("All {} runs complete (elapsed {:.1f}s)", len(data), elapsed)
                return data

            logger.debug(
                "{}/{} runs still pending — sleeping {:.1f}s",
                len(pending),
                len(data),
                delay,
            )
            await asyncio.sleep(delay)
            elapsed += delay
            delay = min(delay * 2, max_delay)

        logger.warning("Poll timed out after {:.0f}s", timeout)
        resp = await client.post(_BATCH_GET, json={"run_ids": run_ids})
        return resp.json().get("data", []) if resp.status_code == 200 else []

    # ------------------------------------------------------------------
    # SSE streaming — fallback for single-URL requests
    # ------------------------------------------------------------------

    async def run_sse(
        self,
        url: str,
        goal: str,
        *,
        browser_profile: str = "stealth",
        event_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Run a single automation via SSE and return the result.

        Returns:
            The ``resultJson`` dict on success, or ``{"error": "..."}`` on failure.

        Args:
            url: The URL to scrape.
            goal: The goal to achieve.
            browser_profile: The browser profile to use.
            event_callback: A callback function to call with each event.
        """
        client = self._ensure_open()
        payload = {
            "url": url,
            "goal": goal,
            "browser_profile": browser_profile,
        }

        logger.info("Starting SSE run on {}", url)
        try:
            async with client.stream("POST", _RUN_SSE, json=payload) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    return {
                        "error": f"TinyFish SSE failed ({response.status_code}): {text.decode()}"
                    }

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        event = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

                    etype = event.get("type", "")

                    if etype == "PROGRESS":
                        logger.debug("SSE progress: {}", event.get("purpose", ""))

                    if etype == "COMPLETE" or event.get("status") == "COMPLETED":
                        result = event.get("resultJson") or event.get("result")
                        logger.info("SSE run completed for {}", url)
                        return result if result else {"error": "Empty result from TinyFish"}

                    if etype == "ERROR" or event.get("status") == "FAILED":
                        msg = event.get("message") or event.get("error", "Unknown error")
                        return {"error": f"TinyFish agent failed: {msg}"}

        except httpx.ReadTimeout:
            return {"error": "TinyFish SSE timed out"}
        except Exception as exc:
            return {"error": f"TinyFish SSE error: {exc}"}

        return {"error": "TinyFish SSE stream ended without a result"}
