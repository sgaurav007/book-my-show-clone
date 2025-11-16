from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.events.kafka_producer import KafkaProducer
from common.database import async_session_maker

# Global instances
redis_client: Redis = None
kafka_producer: KafkaProducer = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> Redis:
    """Dependency for Redis client"""
    return redis_client


async def get_kafka_producer() -> KafkaProducer:
    """Dependency for Kafka producer"""
    return kafka_producer
