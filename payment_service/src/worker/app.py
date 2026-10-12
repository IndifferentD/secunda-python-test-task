import logging

import httpx
from faststream import AckPolicy, FastStream
from faststream.rabbit import Channel, RabbitBroker
from faststream.rabbit.annotations import RabbitMessage

from payment_service.src.config import WorkerSettings
from payment_service.src.db import create_session_factory
from payment_service.src.messaging import (
    PAYMENTS_NEW_QUEUE,
    PaymentMessage,
    declare_payment_queues,
)
from payment_service.src.worker.gateway import SimulatedPaymentGateway
from payment_service.src.worker.processor import PaymentProcessor
from payment_service.src.worker.repository import WorkerPaymentRepository
from payment_service.src.worker.webhook import WebhookSender

logger = logging.getLogger(__name__)


async def run(settings: WorkerSettings) -> None:
    broker = RabbitBroker(
        settings.rabbitmq_url,
        default_channel=Channel(prefetch_count=10),
        logger=logger,
    )

    sessions = create_session_factory(settings.database_url)
    http_client = httpx.AsyncClient(timeout=settings.webhook_timeout_seconds)
    processor = PaymentProcessor(
        sessions,
        WorkerPaymentRepository(),
        SimulatedPaymentGateway(),
        WebhookSender(
            http_client, settings.webhook_attempts, settings.retry_base_seconds
        ),
    )
    app = FastStream(broker)
    app.after_shutdown(http_client.aclose)

    @broker.subscriber(PAYMENTS_NEW_QUEUE, ack_policy=AckPolicy.MANUAL)
    async def handle_new_payment(
        message: PaymentMessage, raw_message: RabbitMessage
    ) -> None:
        try:
            await processor.process(message.payment_id)
        except Exception:
            logger.exception("Failed to process payment message")
            # RabbitMQ 4.3 считает reject неудачной доставкой, а nack — нет.
            await raw_message.reject(requeue=True)
        else:
            await raw_message.ack()

    await broker.connect()
    await declare_payment_queues(broker)
    await app.run()
