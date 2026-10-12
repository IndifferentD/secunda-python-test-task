import uvicorn

from payment_service.src.config import ApiSettings
from payment_service.src.web.api import create_app


def main() -> None:
    settings = ApiSettings()
    uvicorn.run(create_app(settings), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
