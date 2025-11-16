from typing import AsyncGenerator

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.events.kafka_producer import PaymentEventPublisher
from app.services.gateway_adapter import MockPaymentGatewayAdapter
from app.services.payment_service import PaymentService
from app.services.refund_service import RefundService

# Database engine and session
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Global Kafka producer (will be initialized on startup)
kafka_producer: AIOKafkaProducer = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_event_publisher() -> PaymentEventPublisher:
    """Dependency for event publisher"""
    return PaymentEventPublisher(kafka_producer)


def get_gateway_adapter() -> MockPaymentGatewayAdapter:
    """Dependency for payment gateway adapter"""
    return MockPaymentGatewayAdapter(
        success_rate=settings.gateway_success_rate,
        processing_time_ms=settings.gateway_processing_time_ms,
    )


async def get_payment_service(
    db: AsyncSession = Depends(get_db),
) -> PaymentService:
    """Dependency for payment service"""
    event_publisher = get_event_publisher()
    gateway_adapter = get_gateway_adapter()
    return PaymentService(db, event_publisher, gateway_adapter)


async def get_refund_service(
    db: AsyncSession = Depends(get_db),
) -> RefundService:
    """Dependency for refund service"""
    event_publisher = get_event_publisher()
    gateway_adapter = get_gateway_adapter()
    return RefundService(db, event_publisher, gateway_adapter)
