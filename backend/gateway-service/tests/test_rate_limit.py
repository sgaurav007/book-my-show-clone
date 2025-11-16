"""Tests for rate limiting middleware."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import time

from app.middleware.rate_limit import RateLimiter, rate_limit_middleware
from app.config import settings


class TestRateLimiter:
    """Test rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_disabled(self):
        """Test that rate limiter can be disabled."""
        with patch.object(settings, "rate_limit_enabled", False):
            limiter = RateLimiter()
            assert limiter.enabled is False

            # Mock request
            mock_request = MagicMock()
            mock_request.state.user_id = 123

            is_allowed, info = await limiter.is_allowed(mock_request)
            assert is_allowed is True
            assert info == {}

    @pytest.mark.asyncio
    async def test_rate_limiter_get_key_authenticated(self):
        """Test rate limiter key generation for authenticated users."""
        limiter = RateLimiter()

        # Mock authenticated request
        mock_request = MagicMock()
        mock_request.state.user_id = 123

        key = limiter.get_key(mock_request)
        assert key == "rate_limit:user:123"

    @pytest.mark.asyncio
    async def test_rate_limiter_get_key_unauthenticated(self):
        """Test rate limiter key generation for unauthenticated users."""
        limiter = RateLimiter()

        # Mock unauthenticated request
        mock_request = MagicMock()
        mock_request.state = MagicMock()
        mock_request.state.user_id = None
        mock_request.headers.get.return_value = None
        mock_request.client.host = "192.168.1.1"

        with patch("app.middleware.rate_limit.get_client_ip", return_value="192.168.1.1"):
            key = limiter.get_key(mock_request)
            assert key == "rate_limit:ip:192.168.1.1"

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_within_limit(self, mock_redis):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter()
        limiter.redis_client = mock_redis

        # Mock Redis pipeline
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[None, 5, None, None])  # 5 requests so far
        mock_redis.pipeline.return_value = mock_pipe

        # Mock request
        mock_request = MagicMock()
        mock_request.state.user_id = 123
        mock_request.url.path = "/api/v1/test"

        is_allowed, info = await limiter.is_allowed(mock_request)

        assert is_allowed is True
        assert "X-RateLimit-Limit" in info
        assert "X-RateLimit-Remaining" in info
        assert int(info["X-RateLimit-Remaining"]) >= 0

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(self, mock_redis):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter()
        limiter.redis_client = mock_redis
        limiter.max_requests = 10

        # Mock Redis pipeline - simulate 10 requests already made
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[None, 10, None, None])
        mock_redis.pipeline.return_value = mock_pipe

        # Mock request
        mock_request = MagicMock()
        mock_request.state.user_id = 123
        mock_request.url.path = "/api/v1/test"

        is_allowed, info = await limiter.is_allowed(mock_request)

        assert is_allowed is False
        assert "X-RateLimit-Limit" in info
        assert info["X-RateLimit-Remaining"] == "0"

    @pytest.mark.asyncio
    async def test_rate_limiter_fails_open_on_redis_error(self, mock_redis):
        """Test that rate limiter fails open (allows) on Redis errors."""
        limiter = RateLimiter()
        limiter.redis_client = mock_redis

        # Mock Redis error
        mock_redis.pipeline.side_effect = Exception("Redis error")

        # Mock request
        mock_request = MagicMock()
        mock_request.state.user_id = 123
        mock_request.url.path = "/api/v1/test"

        is_allowed, info = await limiter.is_allowed(mock_request)

        # Should allow the request on error (fail open)
        assert is_allowed is True


class TestRateLimitMiddleware:
    """Test rate limiting middleware integration."""

    def test_rate_limit_headers_added(self, client, valid_jwt_token):
        """Test that rate limit headers are added to responses."""
        with patch("app.middleware.rate_limit.rate_limiter") as mock_limiter:
            # Mock rate limiter to allow request
            mock_limiter.enabled = True
            mock_limiter.redis_client = MagicMock()
            mock_limiter.is_allowed = AsyncMock(return_value=(True, {
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "99",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
            }))

            with patch("app.routes.proxy.http_client") as mock_http:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.content = b'{"data": "test"}'
                mock_response.headers = {"content-type": "application/json"}
                mock_http.request = MagicMock(return_value=mock_response)

                response = client.get(
                    "/api/v1/users/123",
                    headers={"Authorization": f"Bearer {valid_jwt_token}"},
                )

                # Check rate limit headers
                assert "x-ratelimit-limit" in response.headers
                assert "x-ratelimit-remaining" in response.headers

    def test_rate_limit_exceeded_returns_429(self, client, valid_jwt_token):
        """Test that exceeding rate limit returns 429 error."""
        with patch("app.middleware.rate_limit.rate_limiter") as mock_limiter:
            # Mock rate limiter to block request
            mock_limiter.enabled = True
            mock_limiter.redis_client = MagicMock()
            mock_limiter.is_allowed = AsyncMock(return_value=(False, {
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
            }))

            response = client.get(
                "/api/v1/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 429
            data = response.json()
            assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_skips_health_endpoint(self, client):
        """Test that rate limiting is skipped for health endpoint."""
        # The health endpoint should never be rate limited
        for _ in range(200):  # Try many times
            response = client.get("/health")
            assert response.status_code == 200
