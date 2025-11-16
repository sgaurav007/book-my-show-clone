# Python/FastAPI Development Guide

This guide provides comprehensive instructions for developing the BookMyShow Python/FastAPI backend services.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Poetry Dependency Management](#poetry-dependency-management)
4. [Running Services Locally](#running-services-locally)
5. [Database Migrations with Alembic](#database-migrations-with-alembic)
6. [Testing](#testing)
7. [Code Quality](#code-quality)
8. [Debugging](#debugging)
9. [Common Issues and Solutions](#common-issues-and-solutions)
10. [Best Practices](#best-practices)

## Development Environment Setup

### Prerequisites

Install the following tools:

1. **Python 3.11+**
   ```bash
   # Check Python version
   python --version  # or python3 --version

   # Install Python 3.11 on Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev

   # Install Python 3.11 on macOS (using Homebrew)
   brew install python@3.11
   ```

2. **Poetry 1.7+**
   ```bash
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -

   # Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.local/bin:$PATH"

   # Verify installation
   poetry --version

   # Configure Poetry to create virtual environments in project directory
   poetry config virtualenvs.in-project true
   ```

3. **Docker & Docker Compose**
   - For running infrastructure (PostgreSQL, Redis, Kafka)
   - [Install Docker](https://docs.docker.com/get-docker/)

### IDE Setup

#### VS Code

Install recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Black Formatter (ms-python.black-formatter)
- autoDocstring (njpwerner.autodocstring)

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project
2. Settings → Project → Python Interpreter
3. Add Poetry Environment
4. Enable: Settings → Tools → Black, Ruff
5. Enable: Settings → Tools → Python Integrated Tools → pytest

## Project Structure

```
backend/
├── shared/
│   └── common/                      # Shared Python package
│       ├── bookmyshow_common/
│       │   ├── __init__.py
│       │   ├── exceptions.py        # Custom exception classes
│       │   ├── models.py            # Base SQLAlchemy models
│       │   ├── schemas.py           # Base Pydantic schemas
│       │   ├── database.py          # Database session management
│       │   ├── redis_client.py      # Redis utilities
│       │   ├── kafka_client.py      # Kafka producer/consumer
│       │   ├── security.py          # JWT utilities
│       │   └── middleware.py        # Common middleware
│       ├── pyproject.toml
│       └── tests/
│
├── user-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings (Pydantic BaseSettings)
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── refresh_token.py
│   │   ├── schemas/                 # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── auth.py
│   │   ├── api/                     # API routes
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── users.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   └── auth_service.py
│   │   ├── repositories/            # Data access layer
│   │   │   ├── __init__.py
│   │   │   └── user_repository.py
│   │   ├── security/                # Security utilities
│   │   │   ├── __init__.py
│   │   │   └── password.py
│   │   └── dependencies.py          # FastAPI dependencies
│   ├── alembic/                     # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── pyproject.toml               # Poetry dependencies
│   ├── poetry.lock
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── unit/
│   │   └── integration/
│   └── Dockerfile
```

## Poetry Dependency Management

### Initial Setup

```bash
cd backend/user-service

# Install dependencies from poetry.lock
poetry install

# Install with dev dependencies
poetry install --with dev

# Activate virtual environment
poetry shell

# Or run commands without activating
poetry run python script.py
```

### Managing Dependencies

```bash
# Add a production dependency
poetry add fastapi

# Add a development dependency
poetry add --group dev pytest

# Add with version constraint
poetry add sqlalchemy@^2.0.0

# Update all dependencies
poetry update

# Update specific package
poetry update fastapi

# Remove a dependency
poetry remove package-name

# Show installed packages
poetry show

# Export to requirements.txt (for Docker)
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Common Dependencies

All services include:
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
sqlalchemy = "^2.0.23"
alembic = "^1.13.0"
asyncpg = "^0.29.0"
redis = "^5.0.1"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
aiokafka = "^0.10.0"
python-multipart = "^0.0.6"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
httpx = "^0.25.2"
faker = "^20.1.0"
black = "^23.12.0"
ruff = "^0.1.8"
mypy = "^1.7.1"
```

## Running Services Locally

### 1. Start Infrastructure

```bash
# From project root
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka
```

### 2. Install Shared Common Module

```bash
cd backend/shared/common
poetry install
```

### 3. Run a Service

```bash
cd backend/user-service

# Install dependencies
poetry install

# Run migrations
poetry run alembic upgrade head

# Start service with auto-reload
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload

# Or with more workers (production-like)
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8081
```

### 4. Access the Service

- **API Documentation**: http://localhost:8081/docs
- **Alternative Docs**: http://localhost:8081/redoc
- **Health Check**: http://localhost:8081/health

### Environment Variables

Create `.env` file in service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/user_service_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# JWT
JWT_SECRET=bookmyshow-secret-key-for-jwt-token-generation-and-validation-must-be-at-least-256-bits
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_NAME=User Service
DEBUG=true
LOG_LEVEL=INFO
```

## Database Migrations with Alembic

### Initial Setup

Alembic is already configured in each service. Configuration is in `alembic.ini` and `alembic/env.py`.

### Common Commands

```bash
# Create a new migration (auto-generate from models)
poetry run alembic revision --autogenerate -m "Add user table"

# Create empty migration (manual)
poetry run alembic revision -m "Custom migration"

# Apply all pending migrations
poetry run alembic upgrade head

# Apply specific migration
poetry run alembic upgrade <revision>

# Rollback one migration
poetry run alembic downgrade -1

# Rollback to specific revision
poetry run alembic downgrade <revision>

# View current version
poetry run alembic current

# View migration history
poetry run alembic history

# View SQL for migration (without applying)
poetry run alembic upgrade head --sql

# Stamp database with version (without running migrations)
poetry run alembic stamp head
```

### Creating Migrations

1. **Modify SQLAlchemy models** in `app/models/`

2. **Generate migration**:
   ```bash
   poetry run alembic revision --autogenerate -m "Add email_verified column"
   ```

3. **Review generated migration** in `alembic/versions/`

4. **Apply migration**:
   ```bash
   poetry run alembic upgrade head
   ```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Test migrations on development database first
- Use meaningful migration messages
- Never edit applied migrations
- Include both upgrade and downgrade logic
- Test downgrade before deploying

### Example Migration

```python
# alembic/versions/001_add_user_table.py
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade() -> None:
    op.drop_table('users')
```

## Testing

### Running Tests

```bash
cd backend/user-service

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run with coverage report
poetry run pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
poetry run pytest tests/unit/test_user_service.py

# Run specific test
poetry run pytest tests/unit/test_user_service.py::test_create_user

# Run with verbose output
poetry run pytest -v

# Run and stop on first failure
poetry run pytest -x

# Run tests matching pattern
poetry run pytest -k "test_auth"

# Run tests in parallel
poetry run pytest -n auto
```

### Test Structure

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

```python
# tests/unit/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(db):
    service = UserService(db)
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        first_name="John",
        last_name="Doe"
    )
    user = await service.create_user(user_data)
    assert user.email == "test@example.com"
    assert user.id is not None
```

```python
# tests/integration/test_auth_api.py
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_login(client):
    # Create user first
    client.post("/api/v1/auth/register", json={...})

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Code Quality

### Formatting with Black

```bash
# Format all Python files
poetry run black app/

# Check without modifying
poetry run black --check app/

# Format specific file
poetry run black app/main.py

# Configure in pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
```

### Linting with Ruff

```bash
# Check for issues
poetry run ruff check app/

# Auto-fix issues
poetry run ruff check app/ --fix

# Check specific file
poetry run ruff check app/main.py

# Configure in pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

### Type Checking with MyPy

```bash
# Type check all files
poetry run mypy app/

# Check specific file
poetry run mypy app/main.py

# Configure in pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install and use:
```bash
poetry add --group dev pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Debugging

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8081"
      ],
      "jinja": true,
      "justMyCode": false,
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/user_service_db"
      }
    }
  ]
}
```

### Python Debugger (pdb)

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()

# Common pdb commands:
# n - next line
# s - step into function
# c - continue execution
# p variable - print variable
# l - list code around current line
# q - quit debugger
```

### Logging

```python
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# In main.py
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Error with traceback")
```

## Common Issues and Solutions

### Issue: Poetry install fails

```bash
# Clear cache
poetry cache clear pypi --all

# Delete lock file and reinstall
rm poetry.lock
poetry install

# Update Poetry
poetry self update
```

### Issue: Import errors

```bash
# Ensure shared common module is installed
cd backend/shared/common
poetry install

# Install in editable mode
cd backend/user-service
poetry add ../shared/common --editable
```

### Issue: Alembic can't find models

```python
# In alembic/env.py, ensure all models are imported
from app.models.user import User
from app.models.refresh_token import RefreshToken
# Import all models here

target_metadata = Base.metadata
```

### Issue: Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps

# Test connection
poetry run python -c "from app.database import engine; print(engine.url)"

# Check DATABASE_URL format
# Correct: postgresql+asyncpg://user:pass@host:port/db
# Wrong: postgresql://user:pass@host:port/db (missing +asyncpg)
```

### Issue: Redis/Kafka connection errors

```bash
# Ensure services are running
docker-compose ps redis kafka

# Test Redis
redis-cli -h localhost -p 6379 ping

# Test Kafka
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Best Practices

### Code Organization

1. **Keep routes thin** - Move logic to services
2. **Use dependency injection** - Leverage FastAPI's dependency system
3. **Separate concerns** - Models, schemas, services, repositories
4. **Type everything** - Use type hints consistently
5. **Document with docstrings** - Use Google or NumPy style

### FastAPI Best Practices

```python
# Use Pydantic models for validation
from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    first_name: str
    last_name: str

# Use dependency injection
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return await user_service.create(db, user)

# Use async where possible
async def get_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

### Database Best Practices

```python
# Use connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# Use transactions
async with session.begin():
    user = await create_user(data)
    await create_audit_log(user.id)

# Use indexes
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
```

### Security Best Practices

```python
# Hash passwords
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(plain_password)

# Validate JWT tokens
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401)
    return await get_user_by_id(user_id)
```

### Testing Best Practices

1. Test business logic in unit tests
2. Test API contracts in integration tests
3. Use factories/fixtures for test data
4. Mock external dependencies
5. Aim for >80% code coverage
6. Test error cases

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

---

For project-specific information, see:
- [README.md](./README.md) - Project overview
- [LOCAL_SETUP.md](./LOCAL_SETUP.md) - Local setup guide
- [PYTHON_MIGRATION_PLAN.md](./PYTHON_MIGRATION_PLAN.md) - Migration plan
