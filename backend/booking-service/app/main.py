import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from app.config import settings
from app.api.v1 import bookings
from app.events.kafka_producer import KafkaProducer
from app import dependencies
from common.database import init_database
from common.exception_handlers import add_exception_handlers

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info(f"Starting {settings.service_name}...")

    # Initialize database
    await init_database()
    logger.info("Database initialized")

    # Initialize Redis
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password if settings.redis_password else None,
        decode_responses=False,
    )
    dependencies.redis_client = redis_client
    logger.info("Redis client initialized")

    # Initialize Kafka producer
    kafka_producer = KafkaProducer(settings.kafka_bootstrap_servers)
    await kafka_producer.start()
    dependencies.kafka_producer = kafka_producer
    logger.info("Kafka producer initialized")

    logger.info(f"{settings.service_name} started successfully")

    yield

    # Cleanup
    logger.info(f"Shutting down {settings.service_name}...")

    # Close Kafka producer
    if dependencies.kafka_producer:
        await dependencies.kafka_producer.stop()

    # Close Redis
    if dependencies.redis_client:
        await dependencies.redis_client.close()

    logger.info(f"{settings.service_name} shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Booking Service API",
    description="Booking Service for BookMyShow Clone",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "UP",
        "service": settings.service_name,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
