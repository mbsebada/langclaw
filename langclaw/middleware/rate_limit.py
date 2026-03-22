"""
RateLimitMiddleware — token-bucket per-user rate limiter.

Uses an in-process dict of (user_id → token_count, last_refill_time).
For multi-process deployments, swap the storage for Redis or a shared DB.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime


@dataclass
class _Bucket:
    tokens: float
    last_refill: float = field(default_factory=time.monotonic)


class RateLimitMiddleware(AgentMiddleware):
    """
    Token-bucket rate limiter per ``user_id`` (read from channel_context).

    Args:
        rpm: Requests per minute allowed per user. Default 60.
        burst: Maximum burst size (tokens above rpm). Default = rpm.
    """

    def __init__(self, rpm: int = 60, burst: int | None = None) -> None:
        super().__init__()
        self._rpm = rpm
        self._burst = burst if burst is not None else rpm
        self._buckets: dict[str, _Bucket] = defaultdict(lambda: _Bucket(tokens=float(self._burst)))

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        ctx = getattr(runtime, "context", None)
        user_id = ctx.user_id if ctx else None
        if not user_id:
            return None

        bucket = self._buckets[user_id]
        now = time.monotonic()
        elapsed = now - bucket.last_refill
        # Refill at rpm tokens/minute = rpm/60 tokens/second
        bucket.tokens = min(
            self._burst,
            bucket.tokens + elapsed * (self._rpm / 60.0),
        )
        bucket.last_refill = now

        # Evict oldest buckets to prevent unbounded memory growth
        _MAX_BUCKETS = 10_000
        if len(self._buckets) > _MAX_BUCKETS:
            sorted_keys = sorted(self._buckets, key=lambda k: self._buckets[k].last_refill)
            for k in sorted_keys[:len(self._buckets) - _MAX_BUCKETS]:
                del self._buckets[k]

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return None

        # Rate limit exceeded — short-circuit the agent
        return {
            "messages": [
                AIMessage(
                    content=(
                        "You are sending messages too fast. "
                        "Please wait a moment before trying again."
                    )
                )
            ],
            "jump_to": "end",
        }
