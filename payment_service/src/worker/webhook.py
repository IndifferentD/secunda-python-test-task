import asyncio
from uuid import UUID

import httpx

from payment_service.src.enums import PaymentStatus


class WebhookSender:
    def __init__(
        self, client: httpx.AsyncClient, attempts: int, retry_base_seconds: float
    ) -> None:
        self.client = client
        self.attempts = attempts
        self.retry_base_seconds = retry_base_seconds

    async def send(self, url: str, payment_id: UUID, status: PaymentStatus) -> None:
        for attempt in range(self.attempts):
            try:
                response = await self.client.post(
                    url,
                    json={"payment_id": str(payment_id), "status": status.value},
                )
                response.raise_for_status()
                return
            except httpx.HTTPError:
                if attempt == self.attempts - 1:
                    raise
                await asyncio.sleep(self.retry_base_seconds * 2**attempt)
