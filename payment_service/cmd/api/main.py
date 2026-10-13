import uvicorn

from payment_service.src.config import ApiSettings
from payment_service.src.logging import configure_logging
from payment_service.src.web.api import create_app


def main() -> None:
    configure_logging("api")
    settings = ApiSettings()  # pyright: ignore[reportCallIssue]
    uvicorn.run(create_app(settings), host="0.0.0.0", port=8000, log_config=None)


if __name__ == "__main__":
    main()
