from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from payment_service.src.enums import PaymentStatus
from payment_service.src.worker.gateway import PaymentGateway
from payment_service.src.worker.repository import WorkerPaymentRepository
from payment_service.src.worker.webhook import WebhookSender


class PaymentNotFound(Exception):
    pass


class PaymentProcessor:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        repository: WorkerPaymentRepository,
        gateway: PaymentGateway,
        webhook: WebhookSender,
    ) -> None:
        self.sessions = sessions
        self.repository = repository
        self.gateway = gateway
        self.webhook = webhook

    async def process(self, payment_id: UUID) -> None:
        async with self.sessions.begin() as session:
            payment = await self.repository.get_for_update(session, payment_id)
            if payment is None:
                raise PaymentNotFound(payment_id)

            if payment.status == PaymentStatus.PENDING:
                payment.status = await self.gateway.process(payment)

            status = payment.status
            webhook_url = payment.webhook_url

        await self.webhook.send(webhook_url, payment_id, status)
