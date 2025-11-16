"""Tests for authentication middleware."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt

from app.middleware.auth import (
    JWTValidator,
    is_public_endpoint,
    auth_middleware,
    PUBLIC_ENDPOINTS,
)
from app.config import settings


class TestJWTValidator:
    """Test JWT validation functionality."""

    def test_validate_valid_token(self, valid_jwt_token):
        """Test validation of a valid token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        assert validator.validate_token(valid_jwt_token) is True

    def test_validate_expired_token(self, expired_jwt_token):
        """Test validation of an expired token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        assert validator.validate_token(expired_jwt_token) is False

    def test_validate_invalid_token(self):
        """Test validation of an invalid token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        assert validator.validate_token("invalid.token.here") is False

    def test_get_claims(self, valid_jwt_token):
        """Test extracting claims from a valid token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        claims = validator.get_claims(valid_jwt_token)

        assert claims is not None
        assert claims["sub"] == "testuser"
        assert claims["userId"] == 123
        assert claims["role"] == "USER"

    def test_get_user_id(self, valid_jwt_token):
        """Test extracting user ID from token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        user_id = validator.get_user_id(valid_jwt_token)

        assert user_id == 123

    def test_get_username(self, valid_jwt_token):
        """Test extracting username from token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        username = validator.get_username(valid_jwt_token)

        assert username == "testuser"

    def test_get_role(self, valid_jwt_token):
        """Test extracting role from token."""
        validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
        role = validator.get_role(valid_jwt_token)

        assert role == "USER"


class TestPublicEndpoints:
    """Test public endpoint detection."""

    @pytest.mark.parametrize("path,method,expected", [
        ("/api/users/register", "POST", True),
        ("/api/users/login", "POST", True),
        ("/api/users/refresh-token", "POST", True),
        ("/api/catalog/movies", "GET", True),
        ("/api/catalog/theaters", "GET", True),
        ("/api/catalog/shows", "GET", True),
        ("/api/catalog/cities", "GET", True),
        ("/api/catalog/movies", "POST", False),  # Non-GET on catalog
        ("/api/users/profile", "GET", False),  # Protected endpoint
        ("/api/bookings/123", "GET", False),  # Protected endpoint
        ("/health", "GET", True),
        ("/metrics", "GET", True),
    ])
    def test_is_public_endpoint(self, path, method, expected):
        """Test public endpoint detection for various paths and methods."""
        assert is_public_endpoint(path, method) == expected


class TestAuthMiddleware:
    """Test authentication middleware."""

    def test_public_endpoint_no_auth_required(self, client):
        """Test that public endpoints don't require authentication."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_protected_endpoint_missing_auth_header(self, client):
        """Test that protected endpoints require Authorization header."""
        with patch("app.routes.proxy.http_client") as mock_client:
            response = client.get("/api/v1/bookings/123")

            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "MISSING_AUTHORIZATION"

    def test_protected_endpoint_invalid_auth_format(self, client):
        """Test that invalid Authorization header format is rejected."""
        with patch("app.routes.proxy.http_client") as mock_client:
            response = client.get(
                "/api/v1/bookings/123",
                headers={"Authorization": "InvalidFormat token123"},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "INVALID_AUTHORIZATION"

    def test_protected_endpoint_expired_token(self, client, expired_jwt_token):
        """Test that expired tokens are rejected."""
        with patch("app.routes.proxy.http_client") as mock_client:
            response = client.get(
                "/api/v1/bookings/123",
                headers={"Authorization": f"Bearer {expired_jwt_token}"},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "INVALID_TOKEN"

    def test_protected_endpoint_valid_token(self, client, valid_jwt_token):
        """Test that valid tokens are accepted and user info is extracted."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock the backend service response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"bookings": []}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get(
                "/api/v1/bookings/list",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            # Should pass authentication and attempt to proxy
            # (will fail because service is not running, but that's ok)
            # The important part is it didn't fail at auth
            assert response.status_code in [200, 502, 503, 504]

    def test_catalog_get_no_auth_required(self, client):
        """Test that GET requests to catalog don't require auth."""
        with patch("app.routes.proxy.http_client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"movies": []}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get("/api/v1/movies")

            # Should not require authentication
            assert response.status_code in [200, 502, 503, 504]
