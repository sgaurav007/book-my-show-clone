"""Rate limiting middleware for the API Gateway."""
import time
from typing import Callable, Optional
import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from datetime import datetime
import redis.asyncio as redis

from app.config import settings
from app.middleware.logging import get_client_ip


logger = structlog.get_logger(__name__)


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.

    This implements a token bucket / sliding window rate limiter using Redis.
    Each user or IP address has a limit of N requests per time window.
    """

    def __init__(self):
        """Initialize the rate limiter with Redis connection."""
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.rate_limit_enabled
        self.max_requests = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window

    async def connect(self):
        """Establish Redis connection."""
        if not self.enabled:
            return

        try:
            self.redis_client = await redis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                password=settings.redis_password if settings.redis_password else None,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info(
                "Rate limiter connected to Redis",
                host=settings.redis_host,
                port=settings.redis_port,
            )
        except Exception as e:
            logger.warning(
                "Failed to connect to Redis for rate limiting, disabling rate limiter",
                error=str(e),
            )
            self.enabled = False
            self.redis_client = None

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Rate limiter Redis connection closed")

    def get_key(self, request: Request) -> str:
        """
        Generate a unique key for rate limiting.

        Uses user ID if authenticated, otherwise uses client IP.

        Args:
            request: The incoming request

        Returns:
            Redis key for rate limiting
        """
        # Use user ID if authenticated
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"rate_limit:user:{request.state.user_id}"

        # Fall back to client IP
        client_ip = get_client_ip(request)
        return f"rate_limit:ip:{client_ip}"

    async def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """
        Check if the request should be allowed based on rate limits.

        Implements a sliding window rate limiter:
        - Uses Redis sorted sets to track request timestamps
        - Removes expired entries outside the time window
        - Checks if current request count is under the limit
        - Adds current request timestamp

        Args:
            request: The incoming request

        Returns:
            Tuple of (is_allowed, rate_limit_info)
            - is_allowed: True if request should proceed, False if rate limited
            - rate_limit_info: Dict with rate limit headers (limit, remaining, reset)
        """
        if not self.enabled or not self.redis_client:
            # Rate limiting disabled or Redis not available
            return True, {}

        key = self.get_key(request)
        current_time = time.time()
        window_start = current_time - self.window_seconds

        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            pipe.zcard(key)

            # Add current request timestamp
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration on the key
            pipe.expire(key, self.window_seconds)

            # Execute pipeline
            results = await pipe.execute()

            # Get request count (before adding current request)
            request_count = results[1]

            # Calculate rate limit info
            remaining = max(0, self.max_requests - request_count - 1)
            reset_time = int(current_time + self.window_seconds)

            rate_limit_info = {
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "X-RateLimit-Window": str(self.window_seconds),
            }

            # Check if rate limit exceeded
            if request_count >= self.max_requests:
                logger.warning(
                    "Rate limit exceeded",
                    key=key,
                    request_count=request_count,
                    limit=self.max_requests,
                    path=request.url.path,
                )
                return False, rate_limit_info

            logger.debug(
                "Rate limit check passed",
                key=key,
                request_count=request_count + 1,
                limit=self.max_requests,
                remaining=remaining,
            )

            return True, rate_limit_info

        except Exception as e:
            logger.error(
                "Rate limit check failed",
                error=str(e),
                key=key,
                exc_info=True,
            )
            # On error, allow the request (fail open)
            return True, {}


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """
    Rate limiting middleware.

    This middleware:
    - Checks if the request should be rate limited
    - Returns 429 Too Many Requests if limit exceeded
    - Adds rate limit headers to all responses
    - Uses Redis for distributed rate limiting

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the next handler or a 429 error
    """
    # Skip rate limiting for health and metrics endpoints
    if request.url.path in ["/health", "/metrics"]:
        return await call_next(request)

    # Initialize Redis connection if not already connected
    if not rate_limiter.redis_client and rate_limiter.enabled:
        await rate_limiter.connect()

    # Check rate limit
    is_allowed, rate_limit_info = await rate_limiter.is_allowed(request)

    if not is_allowed:
        # Rate limit exceeded
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            },
            headers=rate_limit_info,
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers to response
    for header, value in rate_limit_info.items():
        response.headers[header] = value

    return response
