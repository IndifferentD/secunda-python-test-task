from uuid import UUID

from fastapi import APIRouter, Header, HTTPException

from payment_service.src.services.payments import (
    IdempotencyConflict,
    PaymentData,
    PaymentService,
)
from payment_service.src.web.schemas import (
    PaymentCreate,
    PaymentCreated,
    PaymentDetails,
)


def create_router(service: PaymentService) -> APIRouter:
    router = APIRouter()

    @router.post("/payments", response_model=PaymentCreated, status_code=202)
    async def create_payment(
        body: PaymentCreate,
        idempotency_key: str = Header(alias="Idempotency-Key"),
    ) -> PaymentCreated:
        data = PaymentData(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            metadata=body.metadata,
            webhook_url=str(body.webhook_url),
        )
        try:
            payment = await service.create(idempotency_key, data)
        except IdempotencyConflict:
            raise HTTPException(
                status_code=409,
                detail="Idempotency key was used with a different request",
            ) from None
        return PaymentCreated(
            payment_id=payment.id,
            status=payment.status,
            created_at=payment.created_at,
        )

    @router.get("/payments/{payment_id}", response_model=PaymentDetails)
    async def get_payment(payment_id: UUID) -> PaymentDetails:
        payment = await service.get(payment_id)
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return PaymentDetails(
            payment_id=payment.id,
            status=payment.status,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            metadata=payment.metadata_,
            idempotency_key=payment.idempotency_key,
            webhook_url=payment.webhook_url,
        )

    return router
