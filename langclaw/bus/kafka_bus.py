"""
KafkaMessageBus — high-throughput bus backed by aiokafka.

Suitable for large-scale / event-driven deployments.
Requires: langclaw[kafka]  →  uv add "langclaw[kafka]"

Usage::

    bus = KafkaMessageBus(
        bootstrap_servers="localhost:9092",
        topic="langclaw.inbound",
        group_id="langclaw-workers",
    )
    async with bus:
        await bus.publish(msg)
        async for inbound in bus.subscribe():
            ...
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from typing import TYPE_CHECKING

from langclaw.bus.base import BaseMessageBus, InboundMessage

if TYPE_CHECKING:
    import aiokafka


class KafkaMessageBus(BaseMessageBus):
    """
    Kafka message bus via aiokafka.

    Args:
        bootstrap_servers: Comma-separated Kafka broker addresses.
        topic:             Topic to produce/consume from.
        group_id:          Consumer group ID (affects offset management).
        auto_offset_reset: ``"earliest"`` or ``"latest"``.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "langclaw.inbound",
        group_id: str = "langclaw",
        auto_offset_reset: str = "latest",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._group_id = group_id
        self._auto_offset_reset = auto_offset_reset

        self._producer: aiokafka.AIOKafkaProducer | None = None
        self._consumer: aiokafka.AIOKafkaConsumer | None = None

    async def start(self) -> None:
        try:
            import aiokafka
        except ImportError as exc:
            raise ImportError(
                "KafkaMessageBus requires 'langclaw[kafka]'. Install with: uv add 'langclaw[kafka]'"
            ) from exc

        self._producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await self._producer.start()

        self._consumer = aiokafka.AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset=self._auto_offset_reset,
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await self._consumer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            self._producer = None
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None

    async def publish(self, msg: InboundMessage) -> None:
        if self._producer is None:
            raise RuntimeError("Bus not started.")
        await self._producer.send_and_wait(self._topic, asdict(msg))

    async def subscribe(self) -> AsyncIterator[InboundMessage]:  # type: ignore[override]
        if self._consumer is None:
            raise RuntimeError("Bus not started.")
        async for record in self._consumer:
            try:
                yield InboundMessage(**record.value)
            except (TypeError, ValueError) as exc:
                import logging
                logging.getLogger(__name__).warning("Invalid message from Kafka: %s", exc)
                continue
