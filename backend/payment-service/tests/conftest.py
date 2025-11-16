import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.dependencies import get_db, get_event_publisher, get_gateway_adapter
from app.models.payment import Base as PaymentBase
from app.events.kafka_producer import PaymentEventPublisher
from app.services.gateway_adapter import MockPaymentGatewayAdapter

# Test database URL (using SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(PaymentBase.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(PaymentBase.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_event_publisher():
    """Mock Kafka event publisher"""
    return PaymentEventPublisher(producer=None)


@pytest.fixture
def mock_gateway_adapter():
    """Mock payment gateway adapter"""
    return MockPaymentGatewayAdapter(success_rate=1.0, processing_time_ms=0)


@pytest.fixture
async def client(test_session, mock_event_publisher, mock_gateway_adapter):
    """Create a test client"""
    
    async def override_get_db():
        yield test_session
    
    def override_get_event_publisher():
        return mock_event_publisher
    
    def override_get_gateway_adapter():
        return mock_gateway_adapter
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_event_publisher] = override_get_event_publisher
    app.dependency_overrides[get_gateway_adapter] = override_get_gateway_adapter
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
