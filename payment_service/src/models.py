from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from payment_service.src.enums import Currency, PaymentStatus


class CurrencyType(TypeDecorator[Currency]):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Currency | None, dialect: object) -> str | None:
        return value.value if value is not None else None

    def process_result_value(
        self, value: str | None, dialect: object
    ) -> Currency | None:
        return Currency(value) if value is not None else None


class PaymentStatusType(TypeDecorator[PaymentStatus]):
    impl = Text
    cache_ok = True

    def process_bind_param(
        self, value: PaymentStatus | None, dialect: object
    ) -> str | None:
        return value.value if value is not None else None

    def process_result_value(
        self, value: str | None, dialect: object
    ) -> PaymentStatus | None:
        return PaymentStatus(value) if value is not None else None


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_payments_idempotency_key"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric())
    currency: Mapped[Currency] = mapped_column(CurrencyType())
    description: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB)
    status: Mapped[PaymentStatus] = mapped_column(PaymentStatusType())
    idempotency_key: Mapped[str] = mapped_column(Text)
    webhook_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OutboxEvent(Base):
    __tablename__ = "payment_outbox"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    payment_id: Mapped[UUID] = mapped_column(ForeignKey("payments.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
