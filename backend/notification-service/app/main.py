"""Main FastAPI application"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.dependencies import init_db, close_db, get_db
from app.api.v1.notifications import router as notifications_router
from app.events.kafka_consumer import KafkaConsumerManager
from app.events.booking_event_handler import BookingEventHandler
from app.events.payment_event_handler import PaymentEventHandler
from app.services.email_service import EmailService
from app.services.sms_service import SmsService
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global Kafka consumer manager
kafka_manager: KafkaConsumerManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Notification Service...")
    settings = Settings()

    # Initialize database
    await init_db(settings)
    logger.info("Database initialized")

    # Initialize Kafka consumers
    global kafka_manager
    kafka_manager = KafkaConsumerManager(settings)

    # Create service instances for event handlers
    email_service = EmailService()
    sms_service = SmsService()

    # Create handlers with dependency injection
    async def create_booking_handler():
        """Create booking event handler with database session"""
        async for db in get_db():
            repository = NotificationRepository(db)
            notification_service = NotificationService(repository)
            handler = BookingEventHandler(email_service, sms_service, notification_service)
            return handler

    async def create_payment_handler():
        """Create payment event handler with database session"""
        async for db in get_db():
            repository = NotificationRepository(db)
            notification_service = NotificationService(repository)
            handler = PaymentEventHandler(email_service, sms_service, notification_service)
            return handler

    # Get handler instances
    booking_handler = await create_booking_handler()
    payment_handler = await create_payment_handler()

    # Register event handlers
    kafka_manager.register_handler(
        settings.kafka_topic_booking_confirmed,
        booking_handler.handle_booking_confirmed,
    )
    kafka_manager.register_handler(
        settings.kafka_topic_booking_cancelled,
        booking_handler.handle_booking_cancelled,
    )
    kafka_manager.register_handler(
        settings.kafka_topic_payment_success,
        payment_handler.handle_payment_success,
    )
    kafka_manager.register_handler(
        settings.kafka_topic_payment_failed,
        payment_handler.handle_payment_failed,
    )

    # Start Kafka consumers
    await kafka_manager.start()
    logger.info("Kafka consumers started")

    logger.info("Notification Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Notification Service...")

    # Stop Kafka consumers
    if kafka_manager:
        await kafka_manager.stop()
        logger.info("Kafka consumers stopped")

    # Close database
    await close_db()
    logger.info("Database closed")

    logger.info("Notification Service shut down successfully")


# Create FastAPI app
def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = Settings()

    app = FastAPI(
        title=settings.app_name,
        description="Notification Service for BookMyShow",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(notifications_router, prefix="/api")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "notification-service"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8084,
        reload=True,
        log_level="info",
    )
