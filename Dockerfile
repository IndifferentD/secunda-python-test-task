FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.22 /uv /uvx /bin/

WORKDIR /app

ENV UV_PYTHON_DOWNLOADS=never \
    UV_NO_DEV=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock .python-version README.md ./
COPY alembic.ini ./
COPY migrations ./migrations
COPY payment_service ./payment_service

RUN uv sync --locked
