"""FastAPI application entry point for User Service."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from bookmyshow_common.middleware import setup_middleware

from app.api.v1 import api_router
from app.config import get_settings
from app.dependencies import init_dependencies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting User Service...")
    init_dependencies(settings)
    logger.info("User Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down User Service...")
    logger.info("User Service shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="User authentication and profile management service for BookMyShow",
    lifespan=lifespan,
)

# Setup middleware (CORS, logging, exception handlers)
setup_middleware(app, cors_origins=settings.cors_origins)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "user-service",
            "version": settings.app_version,
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint.
    
    Returns:
        Service information
    """
    return JSONResponse(
        content={
            "service": settings.app_name,
            "version": settings.app_version,
            "description": "User authentication and profile management service",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
