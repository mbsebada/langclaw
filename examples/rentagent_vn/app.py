"""
RentAgent VN — AI-Powered Rental Assistant for Vietnam.

A langclaw app that searches rental listings across Vietnamese platforms
(nhatot.com, batdongsan.com.vn, Facebook groups) using TinyFish Web Agent
API for browser automation.

Demonstrates
------------
- ``app.register_tools()`` — registering pre-built LangChain tools
- ``@app.on_startup`` / ``@app.on_shutdown`` — lifecycle hooks for the
  TinyFish HTTP client
- ``BackgroundScrapeRunner`` — fire-and-forget scraping that delivers
  results to the user's channel via the message bus
- ``ToolRuntime`` — injecting rental URLs at runtime (hidden from LLM)
- Internal LangGraph workflow — deterministic scrape pipeline inside a tool

Run
---
1. Copy ``.env.example`` to ``.env`` and fill in:
   - Azure OpenAI credentials (or another LLM provider)
   - ``TINYFISH_API_KEY``
   - Optionally ``RENTAGENT_URLS`` (comma-separated platform URLs)
2. ``uv sync --group dev``
3. ``python examples/rentagent_vn/app.py``
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from examples.rentagent_vn.models import ScrapeResult
from examples.rentagent_vn.prompts import SYSTEM_PROMPT
from examples.rentagent_vn.scrape_workflow import BackgroundScrapeRunner, set_tinyfish_client
from examples.rentagent_vn.tinyfish.client import TinyFishClient
from examples.rentagent_vn.tools import (
    contact_landlord,
    research_area,
    search_rentals,
    set_background_runner,
)
from langclaw import Langclaw

app = Langclaw(system_prompt=SYSTEM_PROMPT)

# ---------------------------------------------------------------------------
# Register tools
# ---------------------------------------------------------------------------

app.register_tools([search_rentals, contact_landlord, research_area])

# ---------------------------------------------------------------------------
# TinyFish client + background scrape runner lifecycle
# ---------------------------------------------------------------------------

_tinyfish_client: TinyFishClient | None = None
_scrape_runner: BackgroundScrapeRunner | None = None


def _format_results_message(result: ScrapeResult) -> str:
    """Format a ScrapeResult into a user-facing message for channel delivery."""
    if not result.listings:
        msg = "I searched but couldn't find any matching listings this time."
        if result.errors:
            msg += " Some platforms returned errors — try again later."
        return msg

    lines = [f"Found **{len(result.listings)}** rental listing(s):\n"]
    for i, ls in enumerate(result.listings, 1):
        title = ls.title or "Untitled"
        price = ls.price_display or (f"{ls.price_vnd:,.0f} VND" if ls.price_vnd else "Price TBD")
        district = ls.district or ""
        area = f" · {ls.area_sqm:.0f}m²" if ls.area_sqm else ""
        beds = f" · {ls.bedrooms}BR" if ls.bedrooms else ""

        lines.append(f"**{i}. {title}**")
        if ls.description:
            lines.append(f"   {ls.description}")
        lines.append(f"   {price} — {district}{area}{beds}")

        if ls.address:
            lines.append(f"   📍 {ls.address}")

        contact_parts: list[str] = []
        if ls.landlord_name:
            contact_parts.append(ls.landlord_name)
        if ls.landlord_phone:
            contact_parts.append(f"📞 {ls.landlord_phone}")
            contact_parts.append(f"[Zalo](https://zalo.me/{ls.landlord_phone})")
        if ls.landlord_facebook_url:
            contact_parts.append(f"[Facebook]({ls.landlord_facebook_url})")
        if contact_parts:
            lines.append(f"   👤 {' · '.join(contact_parts)}")

        if ls.listing_url:
            lines.append(f"   🔗 [View post]({ls.listing_url})")
        lines.append("")

    return "\n".join(lines)


async def _streaming_url_callback(
    job_id: str,
    run_index: int,
    url: str,
    streaming_url: str,
    channel_context: dict[str, Any],
) -> None:
    """Called on STREAMING_URL events — extracts streamingUrl for FE.

    The streaming URL is included in the final result via ScrapeResult.
    This callback can publish interim updates for live preview (future FE).
    """
    logger.debug("Scrape {} run {} streaming: {} -> {}", job_id, run_index, url, streaming_url)


async def _deliver_scrape_results(
    job_id: str,
    result: ScrapeResult,
    channel_context: dict[str, Any],
) -> None:
    """Callback invoked by ``BackgroundScrapeRunner`` when a job finishes.

    Publishes the formatted results to the user's channel via the message
    bus using ``to="channel"`` so ``GatewayManager`` sends it straight to
    the channel without re-running the agent.
    Includes streaming_urls in metadata for FE to render live preview iframes.
    """
    from langclaw.bus.base import InboundMessage

    bus = app.get_bus()
    if bus is None:
        logger.error("Cannot deliver scrape {} — message bus unavailable", job_id)
        return

    channel = channel_context.get("channel", "")
    if not channel:
        logger.warning("No channel in context for scrape {} — cannot deliver", job_id)
        return

    content = _format_results_message(result)
    logger.info("Delivering scrape {} results to channel={}", job_id, channel)

    orig_meta = channel_context.get("metadata", {}) or {}
    meta: dict[str, Any] = {
        "job_id": job_id,
    }
    if thread_id := channel_context.get("thread_id"):
        meta["thread_id"] = thread_id
    if reply_to := (orig_meta.get("message_id") or orig_meta.get("reply_to")):
        meta["reply_to"] = reply_to
    if result.streaming_urls:
        meta["streaming_urls"] = result.streaming_urls

    await bus.publish(
        InboundMessage(
            channel=channel,
            user_id=channel_context.get("user_id", ""),
            context_id=channel_context.get("context_id", ""),
            chat_id=channel_context.get("chat_id", ""),
            content=content,
            origin="background_scrape",
            to="channel",
            metadata=meta,
        )
    )


@app.on_startup
async def _open_tinyfish() -> None:
    global _tinyfish_client, _scrape_runner
    _tinyfish_client = TinyFishClient()
    await _tinyfish_client.open()
    set_tinyfish_client(_tinyfish_client)

    _scrape_runner = BackgroundScrapeRunner(
        result_callback=_deliver_scrape_results,
        streaming_url_callback=_streaming_url_callback,
    )
    set_background_runner(_scrape_runner)
    logger.info("TinyFish client + background scrape runner ready")


@app.on_shutdown
async def _close_tinyfish() -> None:
    global _tinyfish_client, _scrape_runner
    if _tinyfish_client:
        await _tinyfish_client.close()
        _tinyfish_client = None
    _scrape_runner = None
    set_background_runner(None)  # type: ignore[arg-type]
    logger.info("TinyFish client closed")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
