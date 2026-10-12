from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.src.models import Payment


class WorkerPaymentRepository:
    async def get_for_update(
        self, session: AsyncSession, payment_id: UUID
    ) -> Payment | None:
        return await session.scalar(
            select(Payment).where(Payment.id == payment_id).with_for_update()
        )
