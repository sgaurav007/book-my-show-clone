import logging
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import payments
from app.config import settings
from app import dependencies

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Payment Service...")
    
    # Initialize Kafka producer
    if settings.kafka_enabled:
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                value_serializer=lambda v: v.encode("utf-8") if v else None,
            )
            await producer.start()
            dependencies.kafka_producer = producer
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.warning(f"Failed to start Kafka producer: {e}")
            dependencies.kafka_producer = None
    else:
        logger.info("Kafka is disabled")
        dependencies.kafka_producer = None
    
    logger.info("Payment Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Payment Service...")
    
    if dependencies.kafka_producer:
        await dependencies.kafka_producer.stop()
        logger.info("Kafka producer stopped")
    
    # Close database connections
    await dependencies.engine.dispose()
    logger.info("Database connections closed")
    
    logger.info("Payment Service shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Payment Service",
    description="Payment Service for BookMyShow Clone",
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

# Include routers
app.include_router(payments.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-service",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "payment-service",
        "version": "1.0.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
