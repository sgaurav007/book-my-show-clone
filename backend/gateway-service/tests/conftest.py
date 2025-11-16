"""Pytest configuration and fixtures for gateway service tests."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.main import app, http_client
from app.config import settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_http_client():
    """Mock the httpx.AsyncClient for testing proxy functionality."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    return mock_client


@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing."""
    from jose import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "testuser",
        "userId": 123,
        "user_id": 123,
        "role": "USER",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture
def expired_jwt_token():
    """Generate an expired JWT token for testing."""
    from jose import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "testuser",
        "userId": 123,
        "user_id": 123,
        "role": "USER",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture
def admin_jwt_token():
    """Generate an admin JWT token for testing."""
    from jose import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "adminuser",
        "userId": 1,
        "user_id": 1,
        "role": "ADMIN",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture
def mock_redis():
    """Mock Redis client for rate limiting tests."""
    with patch("app.middleware.rate_limit.redis") as mock:
        mock_client = AsyncMock()
        mock.from_url = AsyncMock(return_value=mock_client)
        yield mock_client


@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test."""
    yield
    # Any cleanup code here
