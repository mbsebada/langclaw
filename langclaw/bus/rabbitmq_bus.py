"""
RabbitMQMessageBus — production bus backed by aio-pika / RabbitMQ.

Suitable for multi-process / multi-instance deployments.
Requires: langclaw[rabbitmq]  →  uv add "langclaw[rabbitmq]"

Usage::

    bus = RabbitMQMessageBus(amqp_url="amqp://guest:guest@localhost/")
    async with bus:
        await bus.publish(msg)
        async for inbound in bus.subscribe():
            ...
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from dataclasses import asdict
from typing import TYPE_CHECKING

from langclaw.bus.base import BaseMessageBus, InboundMessage

if TYPE_CHECKING:
    import aio_pika


class RabbitMQMessageBus(BaseMessageBus):
    """
    AMQP message bus via aio-pika.

    Args:
        amqp_url:      RabbitMQ connection URL.
        queue_name:    Queue to consume/publish from.
        exchange_name: Exchange used for publishing. Empty string = default exchange.
        prefetch_count: AMQP QoS prefetch. Keep at 1 for at-most-once per consumer.
    """

    def __init__(
        self,
        amqp_url: str = "amqp://guest:guest@localhost/",
        queue_name: str = "langclaw.inbound",
        exchange_name: str = "",
        prefetch_count: int = 1,
    ) -> None:
        self._amqp_url = amqp_url
        self._queue_name = queue_name
        self._exchange_name = exchange_name
        self._prefetch_count = prefetch_count

        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.Channel | None = None
        self._queue: aio_pika.Queue | None = None

    async def start(self) -> None:
        try:
            import aio_pika
        except ImportError as exc:
            raise ImportError(
                "RabbitMQMessageBus requires 'langclaw[rabbitmq]'. "
                "Install with: uv add 'langclaw[rabbitmq]'"
            ) from exc

        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._prefetch_count)
        self._queue = await self._channel.declare_queue(self._queue_name, durable=True)

    async def stop(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._queue = None

    async def publish(self, msg: InboundMessage) -> None:
        import aio_pika

        if self._channel is None:
            raise RuntimeError("Bus not started.")

        body = json.dumps(asdict(msg)).encode()
        exchange = (
            self._channel.default_exchange
            if not self._exchange_name
            else await self._channel.get_exchange(self._exchange_name)
        )
        await exchange.publish(
            aio_pika.Message(
                body=body,
                message_id=str(uuid.uuid4()),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=self._queue_name,
        )

    async def subscribe(self) -> AsyncIterator[InboundMessage]:  # type: ignore[override]
        if self._queue is None:
            raise RuntimeError("Bus not started.")

        async with self._queue.iterator() as queue_iter:
            async for raw_msg in queue_iter:
                async with raw_msg.process():
                    data = json.loads(raw_msg.body.decode())
                    try:
                        yield InboundMessage(**data)
                    except (TypeError, ValueError) as exc:
                        import logging

                        logging.getLogger(__name__).warning(
                            "Invalid message from RabbitMQ: %s", exc
                        )
                        continue
