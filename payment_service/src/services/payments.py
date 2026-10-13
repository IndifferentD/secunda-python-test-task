from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from payment_service.src.enums import Currency, PaymentStatus
from payment_service.src.models import Payment
from payment_service.src.repositories.payments import PaymentRepository


@dataclass(frozen=True)
class PaymentData:
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    webhook_url: str


class IdempotencyConflict(Exception):
    pass


class PaymentService:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        repository: PaymentRepository,
    ) -> None:
        self.sessions = sessions
        self.repository = repository

    async def create(self, idempotency_key: str, data: PaymentData) -> Payment:
        try:
            async with self.sessions.begin() as session:
                existing = await self.repository.get_by_key(session, idempotency_key)
                if existing is not None:
                    self._ensure_same_request(existing, data)
                    return existing

                payment = Payment(
                    id=uuid4(),
                    amount=data.amount,
                    currency=data.currency,
                    description=data.description,
                    metadata_=data.metadata,
                    status=PaymentStatus.PENDING,
                    idempotency_key=idempotency_key,
                    webhook_url=data.webhook_url,
                )
                self.repository.insert_with_outbox(session, payment)
                return payment
        except IntegrityError:
            async with self.sessions.begin() as session:
                existing = await self.repository.get_by_key(session, idempotency_key)
                if existing is None:
                    raise
                self._ensure_same_request(existing, data)
                return existing

    async def get(self, payment_id: UUID) -> Payment | None:
        async with self.sessions.begin() as session:
            return await self.repository.get_by_id(session, payment_id)

    @staticmethod
    def _ensure_same_request(payment: Payment, data: PaymentData) -> None:
        if (
            payment.amount != data.amount
            or payment.currency != data.currency
            or payment.description != data.description
            or payment.metadata_ != data.metadata
            or payment.webhook_url != data.webhook_url
        ):
            raise IdempotencyConflict
