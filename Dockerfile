# syntax=docker/dockerfile:latest
ARG IMAGE_VERSION=3.11-slim
FROM python:${IMAGE_VERSION}

LABEL maintainer="Valeriu Stinca <ts@strat.zone>" \
      version="1.0" \
      vendor="Strategic Zone" \
      release-date="2024-11-29" \
      org.opencontainers.image.description="A Python application for tracking Apple orders via a Telegram bot."

WORKDIR /app

COPY pyproject.toml apple_order_tracker.py ./
RUN <<eot
   pip install poetry
   poetry config virtualenvs.create false
   poetry install --only main --no-interaction --no-ansi
eot

ENTRYPOINT ["python", "/app/apple_order_tracker.py"]