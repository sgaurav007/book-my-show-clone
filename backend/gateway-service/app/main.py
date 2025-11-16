"""Main FastAPI application for the API Gateway."""
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import httpx

from app.config import settings
from app.middleware.auth import auth_middleware
from app.middleware.logging import logging_middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.routes.proxy import router as proxy_router


# Configure structured logging
def setup_logging():
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


setup_logging()
logger = structlog.get_logger(__name__)


# Shared HTTP client for proxying requests
http_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager - handles startup and shutdown."""
    # Startup
    global http_client
    logger.info("Starting API Gateway", version=settings.app_version)

    # Initialize HTTP client with connection pooling
    limits = httpx.Limits(
        max_keepalive_connections=settings.http_pool_connections,
        max_connections=settings.http_pool_maxsize,
    )
    timeout = httpx.Timeout(settings.http_timeout)

    http_client = httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
    )

    logger.info(
        "HTTP client initialized",
        pool_connections=settings.http_pool_connections,
        pool_maxsize=settings.http_pool_maxsize,
        timeout=settings.http_timeout,
    )

    yield

    # Shutdown
    logger.info("Shutting down API Gateway")
    if http_client:
        await http_client.aclose()
    logger.info("API Gateway shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API Gateway for BookMyShow Clone - Routes requests to backend microservices",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
    max_age=settings.cors_max_age,
)


# Add custom middleware in order
app.middleware("http")(logging_middleware)
if settings.rate_limit_enabled:
    app.middleware("http")(rate_limit_middleware)
app.middleware("http")(auth_middleware)


# Include routers
app.include_router(proxy_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# Metrics endpoint (Prometheus)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "path": request.url.path,
            }
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with gateway information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "description": "API Gateway for BookMyShow Clone",
        "routes": {
            "user_service": "/api/v1/auth/*, /api/v1/users/*",
            "catalog_service": "/api/v1/movies/*, /api/v1/theaters/*, /api/v1/shows/*, /api/v1/cities/*",
            "booking_service": "/api/v1/bookings/*",
            "payment_service": "/api/v1/payments/*",
            "notification_service": "/api/v1/notifications/*",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging configuration
    )
