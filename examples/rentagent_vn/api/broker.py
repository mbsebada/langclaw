"""Generic in-memory event broker with buffered pub/sub and replay.

Parameterized on event type E. Supports multiple concurrent subscribers
per stream key, late-joining replay, and auto-cleanup after TTL.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, TypeVar

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

E = TypeVar("E")


@dataclass
class _StreamState(Generic[E]):
    """Internal state for a single event stream."""

    events: list[E] = field(default_factory=list)
    subscribers: list[asyncio.Queue[E | None]] = field(default_factory=list)
    done: bool = False
    active_count: int = 0


class EventBroker(Generic[E]):
    """In-memory event broker with buffered pub/sub.

    Args:
        done_event_type: The event type string that signals stream completion.
        event_type_attr: Attribute name to extract the type string from events.
        track_active: If True, enables increment_active/decrement_active
            for multi-job stream tracking.
        cleanup_ttl_seconds: Seconds before cleaning up after completion.
    """

    def __init__(
        self,
        *,
        done_event_type: str = "done",
        event_type_attr: str = "type",
        track_active: bool = False,
        cleanup_ttl_seconds: float = 300.0,
    ) -> None:
        self._streams: dict[str, _StreamState[E]] = {}
        self._done_event_type = done_event_type
        self._event_type_attr = event_type_attr
        self._track_active = track_active
        self._cleanup_ttl = cleanup_ttl_seconds

    def _get_type(self, event: E) -> str:
        return getattr(event, self._event_type_attr)

    def publish(self, stream_id: str, event: E) -> None:
        """Publish an event to all subscribers of a stream.

        Synchronous (non-blocking) so it can be called from async callbacks.

        Args:
            stream_id: The stream identifier (scan_id or campaign_id).
            event: The event to publish.
        """
        state = self._streams.setdefault(stream_id, _StreamState())
        state.events.append(event)

        for queue in state.subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    "Subscriber queue full for stream {}, dropping event",
                    stream_id,
                )

        if self._get_type(event) == self._done_event_type:
            state.done = True
            for queue in state.subscribers:
                try:
                    queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            self._schedule_cleanup(stream_id)

    def increment_active(self, stream_id: str) -> None:
        """Track that a new job started for this stream."""
        state = self._streams.setdefault(stream_id, _StreamState())
        state.active_count += 1

    def decrement_active(self, stream_id: str) -> None:
        """Track that a job finished. Publishes done event when all complete."""
        state = self._streams.get(stream_id)
        if state is None:
            return
        state.active_count = max(0, state.active_count - 1)
        if state.active_count == 0:
            done_event = self._make_done_event(stream_id)
            if done_event is not None:
                self.publish(stream_id, done_event)

    def _make_done_event(self, stream_id: str) -> E | None:
        """Override in subclass to produce a done event when active_count hits 0."""
        return None

    async def subscribe(self, stream_id: str) -> AsyncIterator[E]:
        """Subscribe to events for a stream.

        Yields all buffered events first (replay), then waits for new ones.
        Iteration ends when the stream completes.

        Args:
            stream_id: The stream identifier.

        Yields:
            Events in chronological order.
        """
        state = self._streams.setdefault(stream_id, _StreamState())
        queue: asyncio.Queue[E | None] = asyncio.Queue(maxsize=1000)
        state.subscribers.append(queue)

        try:
            for event in list(state.events):
                yield event

            if state.done:
                return

            if self._track_active and state.active_count == 0 and state.events:
                return

            while True:
                event = await queue.get()
                if event is None:
                    return
                yield event
        finally:
            if queue in state.subscribers:
                state.subscribers.remove(queue)

    def _schedule_cleanup(self, stream_id: str) -> None:
        """Schedule cleanup of stream state after TTL."""

        async def _cleanup() -> None:
            await asyncio.sleep(self._cleanup_ttl)
            self.cleanup(stream_id)

        try:
            asyncio.create_task(_cleanup(), name=f"broker-cleanup-{stream_id}")
        except RuntimeError:
            pass  # No running event loop (e.g., during testing)

    def cleanup(self, stream_id: str) -> None:
        """Remove state for a completed stream."""
        removed = self._streams.pop(stream_id, None)
        if removed:
            logger.debug("Cleaned up stream state for {}", stream_id)

    def get_state(self, stream_id: str) -> _StreamState[E] | None:
        """Get current state for a stream (for debugging/testing)."""
        return self._streams.get(stream_id)
