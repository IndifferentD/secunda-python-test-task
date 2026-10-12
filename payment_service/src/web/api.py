from secrets import compare_digest

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

from payment_service.src.config import ApiSettings
from payment_service.src.db import create_session_factory
from payment_service.src.repositories.payments import PaymentRepository
from payment_service.src.services.payments import PaymentService
from payment_service.src.web.handlers import create_router


def create_app(settings: ApiSettings) -> FastAPI:
    api_key = settings.api_key.get_secret_value()
    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def check_api_key(supplied_key: str | None = Depends(api_key_header)) -> None:
        if supplied_key is None or not compare_digest(supplied_key, api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

    app = FastAPI(title="Сервис обработки платежей", dependencies=[Depends(check_api_key)])
    sessions = create_session_factory(settings.database_url)
    app.include_router(create_router(PaymentService(sessions, PaymentRepository())), prefix="/api/v1")
    return app
