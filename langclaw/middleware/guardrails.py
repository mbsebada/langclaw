"""
Guardrail middleware for langclaw.

Provides:
- ContentFilterMiddleware  — deterministic keyword/regex block (before_agent)
- PIIMiddleware            — re-exported from langchain for convenience

Reference: https://docs.langchain.com/oss/python/langchain/guardrails
"""

from __future__ import annotations

import re
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

# Re-export langchain's built-in PII middleware so callers only need
# to import from langclaw.middleware
try:
    from langchain.agents.middleware import PIIMiddleware  # noqa: F401
except ImportError:
    # Graceful fallback: define a no-op stub so the import never breaks
    class PIIMiddleware(AgentMiddleware):  # type: ignore[no-redef]
        """Stub: install langchain>=1.0 for full PIIMiddleware support."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()


class ContentFilterMiddleware(AgentMiddleware):
    """
    Deterministic guardrail: blocks requests matching banned keywords or regex patterns.

    Runs once per invocation via ``before_agent``. On a match the agent is
    short-circuited (``jump_to="end"``) — no model call is made.

    Args:
        banned_keywords: Case-insensitive literal strings to block.
        banned_patterns: Compiled regex patterns to block (in addition to keywords).
        block_message:   Reply sent to the user when a request is blocked.
    """

    def __init__(
        self,
        banned_keywords: list[str] | tuple[str, ...] = (),
        banned_patterns: list[re.Pattern[str]] | None = None,
        block_message: str = "I cannot process that request.",
    ) -> None:
        super().__init__()
        self._keywords = [kw.lower() for kw in banned_keywords]
        self._patterns: list[re.Pattern[str]] = banned_patterns or []
        self._block_message = block_message

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        msgs = state.get("messages", [])
        if not msgs:
            return None

        # Only inspect the latest human message
        human_msg = next(
            (m for m in reversed(msgs) if getattr(m, "type", None) == "human"),
            None,
        )
        if human_msg is None:
            return None

        raw_content = human_msg.content
        if isinstance(raw_content, str):
            content = raw_content.lower()
        elif isinstance(raw_content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in raw_content
            ).lower()
        else:
            content = ""

        # Keyword check
        if any(kw in content for kw in self._keywords):
            return self._block(state)

        # Regex check
        if any(p.search(content) for p in self._patterns):
            return self._block(state)

        return None

    def _block(self, state: AgentState) -> dict[str, Any]:
        return {
            "messages": [AIMessage(content=self._block_message)],
            "jump_to": "end",
        }


__all__ = ["ContentFilterMiddleware", "PIIMiddleware"]
