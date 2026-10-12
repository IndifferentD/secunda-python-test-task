import asyncio
import logging

from faststream.rabbit import Channel, RabbitBroker

from payment_service.src.config import OutboxSettings
from payment_service.src.db import create_session_factory
from payment_service.src.messaging import declare_payment_queues
from payment_service.src.outbox.publisher import OUTBOX_BATCH_SIZE, OutboxPublisher
from payment_service.src.outbox.repository import OutboxRepository

logger = logging.getLogger(__name__)


async def run(settings: OutboxSettings) -> None:
    sessions = create_session_factory(settings.database_url)
    async with RabbitBroker(
        settings.rabbitmq_url,
        default_channel=Channel(on_return_raises=True),
        logger=logger,
    ) as broker:
        await declare_payment_queues(broker)
        publisher = OutboxPublisher(sessions, OutboxRepository(), broker)

        while True:
            try:
                count = await publisher.publish_batch()
            except Exception:
                logger.exception("Failed to publish outbox batch")
                await asyncio.sleep(settings.outbox_poll_seconds)
            else:
                if count > 0:
                    logger.info("Published %s outbox events", count)
                if count < OUTBOX_BATCH_SIZE:
                    await asyncio.sleep(settings.outbox_poll_seconds)
