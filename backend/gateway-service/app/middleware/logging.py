"""Request/Response logging middleware for the API Gateway."""
import time
from datetime import datetime
from typing import Callable
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = structlog.get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extract the client IP address from the request.

    Handles X-Forwarded-For and X-Real-IP headers for proxied requests.

    Args:
        request: The incoming request

    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (may contain multiple IPs)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    if request.client:
        return request.client.host

    return "unknown"


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log all incoming requests and outgoing responses.

    This middleware:
    - Logs request details (method, path, query params, client IP)
    - Measures request duration
    - Logs response details (status code, duration)
    - Uses structured logging for easy parsing

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the next handler
    """
    # Start timing
    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Extract request details
    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else None
    client_ip = get_client_ip(request)

    # Get authenticated user info if available
    user_id = None
    username = None
    if hasattr(request.state, "user_id"):
        user_id = request.state.user_id
    if hasattr(request.state, "username"):
        username = request.state.username

    # Log incoming request
    logger.info(
        "Incoming request",
        timestamp=timestamp,
        method=method,
        path=path,
        query=query,
        client_ip=client_ip,
        user_id=user_id,
        username=username,
    )

    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        # Log error and re-raise
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Request failed with exception",
            timestamp=datetime.utcnow().isoformat() + "Z",
            method=method,
            path=path,
            duration_ms=round(duration_ms, 2),
            error=str(e),
            exc_info=True,
        )
        raise

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log outgoing response
    logger.info(
        "Outgoing response",
        timestamp=datetime.utcnow().isoformat() + "Z",
        method=method,
        path=path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        user_id=user_id,
        username=username,
    )

    # Add custom headers to response for debugging
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "")
    response.headers["X-Response-Time"] = f"{round(duration_ms, 2)}ms"

    return response
