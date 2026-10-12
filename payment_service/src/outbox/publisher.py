from datetime import UTC, datetime

from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from payment_service.src.messaging import PAYMENTS_NEW_QUEUE
from payment_service.src.outbox.repository import OutboxRepository

OUTBOX_BATCH_SIZE = 100


class OutboxPublisher:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        repository: OutboxRepository,
        broker: RabbitBroker,
    ) -> None:
        self.sessions = sessions
        self.repository = repository
        self.publisher = broker.publisher(PAYMENTS_NEW_QUEUE, persist=True)

    async def publish_batch(self) -> int:
        async with self.sessions.begin() as session:
            events = await self.repository.get_unpublished_batch(
                session, OUTBOX_BATCH_SIZE
            )
            for event in events:
                await self.publisher.publish(
                    {"payment_id": str(event.payment_id)},
                    message_id=str(event.id),
                )
                event.published_at = datetime.now(UTC)
            return len(events)
