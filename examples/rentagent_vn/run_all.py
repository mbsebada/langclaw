"""Start both the Langclaw agent (WS gateway) and FastAPI REST API.

Usage:
    python -m examples.rentagent_vn.run_all
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import uvicorn
from loguru import logger

from examples.rentagent_vn.api.scan_broker import ScanEvent, scan_broker
from examples.rentagent_vn.api.server import create_api_app, set_scan_trigger
from examples.rentagent_vn.db import queries
from examples.rentagent_vn.db.connection import init_db


async def _build_scan_trigger(app_module: Any) -> Any:
    """Create a scan trigger function that bridges the API to the agent's scrape runner."""

    async def trigger_scan(campaign_id: str, query_override: str | None = None) -> dict[str, Any]:
        campaign = await queries.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        prefs = campaign.get("preferences", {})
        sources = campaign.get("sources", [])

        if not sources:
            sources = ["https://www.facebook.com/groups/1930421007111976/"]

        # Build query from preferences if not overridden
        query = query_override
        if not query:
            parts: list[str] = []
            if prefs.get("district"):
                parts.append(prefs["district"])
            if prefs.get("bedrooms"):
                parts.append(f"{prefs['bedrooms']} phòng ngủ")
            if prefs.get("max_price"):
                parts.append(f"dưới {prefs['max_price']}")
            if prefs.get("property_type"):
                parts.append(prefs["property_type"])
            query = ", ".join(parts) if parts else "phòng trọ cho thuê"

        # Create scan record in DB
        runner = app_module.scrape_runner
        job_id_placeholder = "pending"
        scan = await queries.create_scan(campaign_id, job_id_placeholder)
        scan_id = scan["id"]

        # Add to activity log
        await queries.add_activity(
            campaign_id,
            "scan_start",
            f"Bắt đầu quét {len(sources)} nguồn...",
            scan_id=scan_id,
        )

        # Channel context for the background runner to deliver results
        channel_context: dict[str, Any] = {
            "channel": "websocket",
            "user_id": "tisu1902",
            "context_id": campaign_id,
            "chat_id": f"web-user:{campaign_id}",
            "metadata": {
                "campaign_id": campaign_id,
                "scan_id": scan_id,
            },
        }

        job_id = await runner.start(
            urls=sources,
            query=query,
            channel_context=channel_context,
            user_preference=str(prefs) if prefs else None,
        )

        # Publish 'started' event to scan broker for SSE streaming
        scan_broker.publish(
            scan_id,
            ScanEvent(
                type="started",
                url=None,
                data={"job_id": job_id, "urls": sources, "total_urls": len(sources)},
                timestamp=time.monotonic(),
            ),
        )

        # Update scan with actual job_id
        db = await queries.get_db()
        await db.execute("UPDATE scans SET job_id = ? WHERE id = ?", (job_id, scan_id))
        await db.commit()

        logger.info("Triggered scan {} (job {}) for campaign {}", scan_id, job_id, campaign_id)
        return {
            "id": scan_id,
            "campaign_id": campaign_id,
            "job_id": job_id,
            "status": "running",
            "started_at": scan["started_at"],
        }

    return trigger_scan


async def main() -> None:
    """Start both servers."""
    # Initialize database first
    await init_db()

    # Import the app module to access its components
    from examples.rentagent_vn import appx as app_module

    # Build and register the scan trigger
    trigger = await _build_scan_trigger(app_module)
    set_scan_trigger(trigger)

    # Create FastAPI app (skip lifespan DB init since we already did it)
    api_app = create_api_app()

    # Configure uvicorn for the REST API
    config = uvicorn.Config(
        api_app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    api_server = uvicorn.Server(config)

    logger.info("Starting RentAgent VN — REST API on :8000, WS gateway on :18789")

    # Run both servers concurrently
    await asyncio.gather(
        api_server.serve(),
        app_module.app._run_async(),
    )


if __name__ == "__main__":
    asyncio.run(main())
