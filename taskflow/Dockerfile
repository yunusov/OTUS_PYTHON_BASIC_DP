FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY taskflow/ /app/taskflow/

# КОПИРУЕМ .env.docker КАК .env ВНУТРЬ КОНТЕЙНЕРА
COPY taskflow/.env.docker /app/taskflow/.env

ENV PYTHONPATH=/app/taskflow

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

WORKDIR /app/taskflow

CMD ["uv", "run", "main.py"]