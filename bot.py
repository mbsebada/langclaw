"""
Custom langclaw bot with commands and tools.
Run with: .venv/bin/python bot.py
"""

from __future__ import annotations

import platform
import time

from langclaw import Langclaw
from langclaw.gateway.commands import CommandContext

app = Langclaw(
    system_prompt=(
        "You are a helpful assistant running on Miguel's Mac mini. "
        "Keep answers concise. You have access to web search and Python tools."
    ),
)

# ─── Commands (instant, no LLM, no cost) ─────────────────────────

_start_time = time.time()


@app.command("status", description="Show bot health and uptime")
async def status_cmd(ctx: CommandContext) -> str:
    uptime_s = int(time.time() - _start_time)
    hours, remainder = divmod(uptime_s, 3600)
    minutes, seconds = divmod(remainder, 60)

    lines = [
        "🟢 Bot Status",
        f"  Model: {app._config.agents.model if app._config else 'unknown'}",
        f"  Uptime: {hours}h {minutes}m {seconds}s",
        f"  Python: {platform.python_version()}",
        f"  Host: {platform.node()}",
    ]
    return "\n".join(lines)


@app.command("ping", description="Check if bot is alive")
async def ping_cmd(ctx: CommandContext) -> str:
    return "🏓 Pong!"


@app.command("model", description="Show current model info")
async def model_cmd(ctx: CommandContext) -> str:
    model = app._config.agents.model if app._config else "unknown"
    return f"🤖 Running: {model}"


# ─── Run ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run()
