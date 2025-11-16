"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bookmyshow_common.models import Base
from bookmyshow_common.security import JwtTokenProvider

from app.config import Settings
from app.dependencies import init_dependencies, get_db, get_jwt_provider
from app.main import app


# Test database URL (using SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1",
        debug=True,
    )


@pytest.fixture
def test_jwt_provider() -> JwtTokenProvider:
    """Create test JWT provider."""
    return JwtTokenProvider(
        secret_key="test-secret-key",
        access_token_expiration=3600000,
        refresh_token_expiration=86400000,
    )


@pytest.fixture
async def client(test_session: AsyncSession, test_jwt_provider: JwtTokenProvider) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    
    # Override dependencies
    async def override_get_db():
        yield test_session
    
    def override_get_jwt_provider():
        return test_jwt_provider
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_jwt_provider] = override_get_jwt_provider
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides
    app.dependency_overrides.clear()
