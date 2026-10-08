FROM ghcr.io/astral-sh/uv:0.12.3 AS uv
FROM python:3.12.12-slim-bookworm

COPY --from=uv /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY alembic.ini ./
COPY migrations migrations
COPY src src

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "file2formai.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
