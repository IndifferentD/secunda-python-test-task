from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.src.models import OutboxEvent


class OutboxRepository:
    async def get_unpublished_batch(
        self, session: AsyncSession, limit: int
    ) -> list[OutboxEvent]:
        events = await session.scalars(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at, OutboxEvent.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(events)
