from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str


class ApiSettings(CommonSettings):
    api_key: SecretStr


class OutboxSettings(CommonSettings):
    rabbitmq_url: str
    outbox_poll_seconds: float = Field(default=1.0, gt=0)


class WorkerSettings(CommonSettings):
    rabbitmq_url: str
    gateway_attempts: int = Field(default=3, ge=1)
    webhook_attempts: int = Field(default=3, ge=1)
    retry_base_seconds: float = Field(default=1.0, gt=0)
    webhook_timeout_seconds: float = Field(default=5.0, gt=0)
