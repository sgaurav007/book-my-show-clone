"""Common middleware for FastAPI applications."""

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .exceptions import BookMyShowException
from .schemas import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def setup_cors_middleware(
    app: FastAPI,
    allow_origins: list[str] = ["*"],
    allow_credentials: bool = True,
    allow_methods: list[str] = ["*"],
    allow_headers: list[str] = ["*"],
):
    """Setup CORS middleware for FastAPI app.
    
    Args:
        app: FastAPI application
        allow_origins: List of allowed origins
        allow_credentials: Whether to allow credentials
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed headers
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )


async def request_logging_middleware(request: Request, call_next: Callable):
    """Middleware to log requests and responses.
    
    Args:
        request: FastAPI request
        call_next: Next middleware in chain
    """
    start_time = time.time()
    
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
        },
    )
    
    return response


def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for FastAPI app.
    
    Args:
        app: FastAPI application
    """

    @app.exception_handler(BookMyShowException)
    async def bookmyshow_exception_handler(request: Request, exc: BookMyShowException):
        """Handle custom BookMyShow exceptions."""
        error_response = ErrorResponse(
            status=exc.status_code,
            error=exc.__class__.__name__,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        validation_errors = [
            ErrorDetail(
                field=".".join(str(loc) for loc in error["loc"]),
                message=error["msg"],
            )
            for error in exc.errors()
        ]
        
        error_response = ErrorResponse(
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="ValidationError",
            message="Request validation failed",
            path=request.url.path,
            validation_errors=validation_errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )
        
        error_response = ErrorResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="InternalServerError",
            message="An internal server error occurred",
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json"),
        )


def setup_middleware(app: FastAPI, cors_origins: list[str] = ["*"]):
    """Setup all middleware and exception handlers.
    
    Args:
        app: FastAPI application
        cors_origins: List of allowed CORS origins
    """
    setup_cors_middleware(app, allow_origins=cors_origins)
    app.middleware("http")(request_logging_middleware)
    setup_exception_handlers(app)
