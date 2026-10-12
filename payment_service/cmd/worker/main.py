import asyncio

from payment_service.src.config import WorkerSettings
from payment_service.src.logging import configure_logging
from payment_service.src.worker.app import run


def main() -> None:
    configure_logging("worker")
    asyncio.run(run(WorkerSettings()))


if __name__ == "__main__":
    main()
