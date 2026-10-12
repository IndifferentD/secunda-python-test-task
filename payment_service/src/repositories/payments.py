from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.src.models import OutboxEvent, Payment


class PaymentRepository:
    async def get_by_id(self, session: AsyncSession, payment_id: UUID) -> Payment | None:
        return await session.get(Payment, payment_id)

    async def get_by_key(self, session: AsyncSession, idempotency_key: str) -> Payment | None:
        return await session.scalar(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )

    async def insert_with_outbox(self, session: AsyncSession, payment: Payment) -> None:
        session.add_all([payment, OutboxEvent(payment_id=payment.id)])
        await session.flush()
