# Python/FastAPI Migration Plan

## Overview
Complete migration of BookMyShow backend from Java/Spring Boot to Python/FastAPI while maintaining the same architecture, features, and API contracts.

## Technology Mapping

### Core Framework
- **Spring Boot 3.2.0** → **FastAPI 0.104+**
- **Maven** → **Poetry** (dependency management)
- **JUnit 5** → **pytest** (testing)

### Database & ORM
- **Spring Data JPA** → **SQLAlchemy 2.0+**
- **Flyway** → **Alembic** (database migrations)
- **PostgreSQL 15** → **PostgreSQL 15** (unchanged)

### Messaging & Caching
- **Spring Kafka** → **aiokafka** (async Kafka client)
- **Spring Data Redis** → **redis-py / aioredis** (async Redis)
- **Redisson** → **redis-py distributed locks**

### Security & Authentication
- **Spring Security** → **FastAPI dependencies + middleware**
- **JJWT** → **python-jose[cryptography]** or **PyJWT**
- **BCrypt** → **passlib[bcrypt]**

### API Gateway
- **Spring Cloud Gateway** → **FastAPI-based gateway** or **Kong/Traefik**

### Monitoring & Observability
- **Spring Boot Actuator** → **FastAPI health endpoints**
- **Micrometer** → **Prometheus client**
- **Logback** → **Python logging + structlog**

### Serialization & Validation
- **Jackson** → **Pydantic v2** (data validation & serialization)
- **Bean Validation** → **Pydantic validators**

### Server
- **Embedded Tomcat** → **Uvicorn** (ASGI server with Gunicorn in production)

## Directory Structure

```
backend/
├── shared/
│   └── common/                    # Shared Python package
│       ├── pyproject.toml
│       ├── bookmyshow_common/
│       │   ├── __init__.py
│       │   ├── exceptions.py      # Custom exceptions
│       │   ├── models.py          # Base models
│       │   ├── schemas.py         # Pydantic schemas
│       │   ├── database.py        # Database session management
│       │   ├── redis_client.py    # Redis utilities
│       │   ├── kafka_client.py    # Kafka utilities
│       │   └── middleware.py      # Common middleware
│       └── tests/
│
├── user-service/
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── alembic/                   # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entry
│   │   ├── config.py              # Settings (Pydantic BaseSettings)
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── api/                   # API routes
│   │   │   └── v1/
│   │   ├── services/              # Business logic
│   │   ├── repositories/          # Data access
│   │   ├── security/              # JWT, auth
│   │   └── dependencies.py        # FastAPI dependencies
│   └── tests/
│
├── catalog-service/
│   └── [same structure as user-service]
│
├── booking-service/
│   └── [same structure as user-service]
│
├── payment-service/
│   └── [same structure as user-service]
│
├── notification-service/
│   └── [same structure as user-service]
│
└── gateway-service/
    └── [FastAPI-based API gateway]
```

## Migration Strategy by Service

### Agent 1: Shared Common Module + User Service
**Deliverables:**
1. `shared/common/` - Python package with:
   - Base exception classes (ResourceNotFoundException, etc.)
   - Base SQLAlchemy models
   - Base Pydantic schemas
   - Database session management utilities
   - Redis client wrapper
   - Kafka producer/consumer utilities
   - Common middleware (CORS, auth, logging)
   - JWT token provider

2. `backend/user-service/` - FastAPI service:
   - User authentication (register, login, refresh token)
   - User profile management
   - JWT token generation and validation
   - Password hashing with bcrypt
   - Redis for refresh token storage
   - PostgreSQL with SQLAlchemy
   - Alembic migrations matching existing Flyway migrations
   - Health check endpoints
   - Pytest test suite

**Key Files:**
- `shared/common/bookmyshow_common/exceptions.py`
- `shared/common/bookmyshow_common/security.py` (JWT provider)
- `backend/user-service/app/main.py`
- `backend/user-service/app/api/v1/auth.py`
- `backend/user-service/app/api/v1/users.py`
- `backend/user-service/Dockerfile`

### Agent 2: Catalog Service
**Deliverables:**
1. Movie, theater, show, seat management
2. Search functionality with filters
3. Redis caching for frequently accessed data
4. SQLAlchemy models for: Movie, Theater, Show, Screen, Seat, City
5. Alembic migrations
6. API endpoints matching Java implementation
7. Pytest test suite

**Key Features:**
- GET /api/v1/movies (with search/filter)
- GET /api/v1/movies/{id}
- GET /api/v1/theaters
- GET /api/v1/shows
- Redis caching layer

### Agent 3: Booking Service
**Deliverables:**
1. Seat booking with distributed locking (Redis)
2. Booking creation and management
3. Integration with Kafka for booking events
4. SQLAlchemy models for: Booking, BookingSeat
5. Distributed lock mechanism using Redis
6. Alembic migrations
7. Pytest test suite with Redis/Kafka mocking

**Key Features:**
- POST /api/v1/bookings (create booking)
- GET /api/v1/bookings/{id}
- GET /api/v1/bookings/user/{userId}
- PUT /api/v1/bookings/{id}/confirm
- Kafka event publishing on booking creation

### Agent 4: Payment Service
**Deliverables:**
1. Payment processing simulation
2. Payment status management
3. Integration with Kafka for payment events
4. SQLAlchemy models for: Payment
5. Webhook handling
6. Alembic migrations
7. Pytest test suite

**Key Features:**
- POST /api/v1/payments (initiate payment)
- GET /api/v1/payments/{id}
- PUT /api/v1/payments/{id}/webhook
- Kafka event publishing on payment completion

### Agent 5: Notification Service
**Deliverables:**
1. Kafka consumer for booking/payment events
2. Email notification simulation
3. SMS notification simulation
4. Notification history storage
5. SQLAlchemy models for: Notification
6. Alembic migrations
7. Pytest test suite with Kafka mocking

**Key Features:**
- Kafka consumer listening to booking and payment events
- Email service integration (mock/SMTP)
- SMS service integration (mock/Twilio)
- GET /api/v1/notifications/user/{userId}

### Agent 6: API Gateway
**Deliverables:**
1. FastAPI-based API gateway OR configuration for Kong/Traefik
2. Route configuration for all backend services
3. Authentication middleware
4. Rate limiting
5. CORS configuration
6. Request/response logging
7. Health check aggregation

**Routes:**
- `/api/v1/auth/*` → user-service
- `/api/v1/users/*` → user-service
- `/api/v1/movies/*` → catalog-service
- `/api/v1/theaters/*` → catalog-service
- `/api/v1/shows/*` → catalog-service
- `/api/v1/bookings/*` → booking-service
- `/api/v1/payments/*` → payment-service
- `/api/v1/notifications/*` → notification-service

### Agent 7: Infrastructure & Documentation
**Deliverables:**
1. Updated `docker-compose.yml` for Python services
2. Dockerfiles for all services (multi-stage with Poetry)
3. Updated `LOCAL_SETUP.md`
4. Updated `README.md`
5. New `PYTHON_DEVELOPMENT.md` guide
6. Requirements: `pyproject.toml` files for all services
7. `.dockerignore` files
8. Remove all Java code (`backend/**/*.java`, `pom.xml`, etc.)

**Docker Strategy:**
```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim
COPY --from=builder requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Common Python Dependencies

### Core (all services)
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
sqlalchemy = "^2.0.23"
alembic = "^1.13.0"
asyncpg = "^0.29.0"  # Async PostgreSQL driver
redis = "^5.0.1"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
aiokafka = "^0.10.0"
prometheus-client = "^0.19.0"
structlog = "^23.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
httpx = "^0.25.2"  # For testing FastAPI
faker = "^20.1.0"
black = "^23.12.0"
ruff = "^0.1.8"
mypy = "^1.7.1"
```

## API Contract Preservation

All endpoints must maintain the same:
- URL paths
- HTTP methods
- Request/response schemas
- Status codes
- Error response format

Example error response format:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Movie not found with id: '123'",
    "timestamp": "2025-11-16T10:30:00Z"
  }
}
```

## Database Migration Strategy

For each service:
1. Analyze existing Flyway migrations (V1__*.sql files)
2. Create equivalent Alembic migrations
3. Ensure table/column names match exactly
4. Preserve all constraints, indexes, and relationships
5. Use SQLAlchemy declarative models

## Testing Strategy

Each service must include:
1. Unit tests for business logic (services layer)
2. Integration tests for API endpoints
3. Database tests with test containers or SQLite
4. Pytest fixtures for common test data
5. Minimum 70% code coverage

## Deployment Considerations

1. Use Gunicorn with Uvicorn workers in production
2. Configure proper logging (JSON format for production)
3. Environment-based configuration (dev/staging/prod)
4. Health check endpoints for all services
5. Graceful shutdown handling

## Timeline & Execution

**Phase 1:** Parallel implementation by 7 agents (estimated 30-45 minutes)
**Phase 2:** Integration testing and fixes
**Phase 3:** Documentation update
**Phase 4:** Remove all Java code
**Phase 5:** Commit and push to `claude/python-fastapi-migration-01AeENKoXJPkwQVT24fjHDKa`

## Success Criteria

- [ ] All Java code removed from repository
- [ ] All 5 backend services running in Python/FastAPI
- [ ] API Gateway routing correctly
- [ ] All services connect to their PostgreSQL databases
- [ ] Redis integration working for caching and locking
- [ ] Kafka integration working for event streaming
- [ ] Docker Compose successfully starts all services
- [ ] Frontend can communicate with Python backend
- [ ] All existing API contracts preserved
- [ ] Tests passing for all services
- [ ] Documentation updated
