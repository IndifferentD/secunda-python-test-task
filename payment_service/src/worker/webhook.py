import asyncio
import logging
from uuid import UUID

import httpx

from payment_service.src.enums import PaymentStatus

logger = logging.getLogger(__name__)


class WebhookSender:
    def __init__(
        self, client: httpx.AsyncClient, max_attempts: int, retry_base_seconds: float
    ) -> None:
        self.client = client
        self.max_attempts = max_attempts
        self.retry_base_seconds = retry_base_seconds

    async def send(self, url: str, payment_id: UUID, status: PaymentStatus) -> None:
        for attempt in range(self.max_attempts):
            try:
                response = await self.client.post(
                    url,
                    json={"payment_id": str(payment_id), "status": status.value},
                )
                response.raise_for_status()
                return
            except httpx.HTTPError as exc:
                if attempt == self.max_attempts - 1:
                    raise
                logger.warning(
                    "Webhook attempt %d/%d failed for payment %s: %s: %s",
                    attempt + 1,
                    self.max_attempts,
                    payment_id,
                    type(exc).__name__,
                    exc,
                )
                await asyncio.sleep(self.retry_base_seconds * 2**attempt)
