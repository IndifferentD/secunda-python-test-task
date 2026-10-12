import asyncio

from payment_service.src.config import OutboxSettings
from payment_service.src.logging import configure_logging
from payment_service.src.outbox.runner import run


def main() -> None:
    configure_logging("outbox")
    asyncio.run(run(OutboxSettings()))


if __name__ == "__main__":
    main()
