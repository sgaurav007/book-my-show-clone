import pytest
import pytest_asyncio
from decimal import Decimal
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient
from redis.asyncio import Redis
from fakeredis import aioredis as fakeredis

from app.main import app
from app.dependencies import get_db, get_redis, get_kafka_producer
from app.events.kafka_producer import KafkaProducer
from common.database import Base

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5434/booking_test_db"


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(test_db_engine):
    """Create test session maker"""
    return async_sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )


@pytest_asyncio.fixture(scope="function")
async def test_session(test_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def fake_redis():
    """Create fake Redis client for testing"""
    redis = await fakeredis.FakeRedis()
    yield redis
    await redis.close()


@pytest_asyncio.fixture(scope="function")
async def mock_kafka_producer():
    """Create mock Kafka producer"""
    
    class MockKafkaProducer:
        async def start(self):
            pass
        
        async def stop(self):
            pass
        
        async def publish_booking_created(self, event):
            pass
        
        async def publish_booking_confirmed(self, event):
            pass
        
        async def publish_booking_cancelled(self, event):
            pass
    
    return MockKafkaProducer()


@pytest_asyncio.fixture(scope="function")
async def client(test_session, fake_redis, mock_kafka_producer):
    """Create test HTTP client"""
    
    async def override_get_db():
        yield test_session
    
    async def override_get_redis():
        return fake_redis
    
    async def override_get_kafka_producer():
        return mock_kafka_producer
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_kafka_producer] = override_get_kafka_producer
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_seat_info():
    """Sample seat information"""
    return {
        "seat_id": 1,
        "seat_number": "A1",
        "price": "100.00"
    }


@pytest.fixture
def sample_lock_seats_request(sample_seat_info):
    """Sample lock seats request"""
    return {
        "user_id": 1,
        "show_id": 1,
        "seats": [sample_seat_info]
    }
