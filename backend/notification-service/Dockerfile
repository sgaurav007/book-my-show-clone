# Multi-stage build for Python/FastAPI Notification Service

FROM python:3.11-slim AS builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy shared common module
COPY backend/shared/common /app/shared/common

# Install shared common module
WORKDIR /app/shared/common
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy notification service dependencies
WORKDIR /app/notification-service
COPY backend/notification-service/pyproject.toml backend/notification-service/poetry.lock* ./

# Export requirements
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install wget for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY --from=builder /app/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared common module
COPY backend/shared/common/bookmyshow_common /app/bookmyshow_common

# Copy application code
COPY backend/notification-service/app /app/app
COPY backend/notification-service/alembic /app/alembic
COPY backend/notification-service/alembic.ini /app/alembic.ini

# Expose port
EXPOSE 8085

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8085 --workers 4
