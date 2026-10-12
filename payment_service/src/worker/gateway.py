import asyncio
import random
from typing import Protocol

from payment_service.src.enums import PaymentStatus
from payment_service.src.models import Payment


class PaymentGateway(Protocol):
    async def process(self, payment: Payment) -> PaymentStatus: ...


class SimulatedPaymentGateway:
    async def process(self, payment: Payment) -> PaymentStatus:
        await asyncio.sleep(random.uniform(2, 5))
        if random.random() < 0.9:
            return PaymentStatus.SUCCEEDED
        return PaymentStatus.FAILED
