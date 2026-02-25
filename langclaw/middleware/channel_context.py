"""
ChannelContextMiddleware — injects channel/user metadata into agent state
before the agent runs, so tools and system prompts can reference it.
"""

from __future__ import annotations

from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState
from langgraph.runtime import Runtime


class ChannelContextMiddleware(AgentMiddleware):
    """
    Injects channel metadata (channel name, user_id, context_id) into
    the agent state before each invocation.

    The metadata is stored under ``state["channel_context"]`` and is
    available to all downstream middleware and tools via the configurable
    RunnableConfig or state extensions.
    """

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        ctx = getattr(runtime, "context", None)
        if ctx is None:
            return None

        return {"channel_context": {
            "channel": ctx.channel,
            "user_id": ctx.user_id,
            "context_id": ctx.context_id,
            "chat_id": ctx.chat_id,
            "metadata": ctx.metadata,
        }}
