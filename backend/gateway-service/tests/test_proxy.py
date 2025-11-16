"""Tests for reverse proxy functionality."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from app.routes.proxy import get_target_service, proxy_request
from app.config import settings


class TestServiceRouting:
    """Test service routing logic."""

    @pytest.mark.parametrize("path,expected_service", [
        ("/api/v1/auth/login", settings.user_service_url),
        ("/api/v1/users/123", settings.user_service_url),
        ("/api/v1/movies", settings.catalog_service_url),
        ("/api/v1/theaters/456", settings.catalog_service_url),
        ("/api/v1/shows/789", settings.catalog_service_url),
        ("/api/v1/cities", settings.catalog_service_url),
        ("/api/v1/bookings/123", settings.booking_service_url),
        ("/api/v1/payments/456", settings.payment_service_url),
        ("/api/v1/notifications/789", settings.notification_service_url),
    ])
    def test_get_target_service(self, path, expected_service):
        """Test that paths are correctly routed to target services."""
        target = get_target_service(path)
        assert target == expected_service

    def test_get_target_service_unknown_path(self):
        """Test that unknown paths return None."""
        target = get_target_service("/api/v1/unknown/endpoint")
        assert target is None


class TestProxyEndpoints:
    """Test proxy endpoint functionality."""

    def test_proxy_user_service(self, client, valid_jwt_token):
        """Test proxying requests to user service."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock successful response from user service
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"id": 123, "username": "testuser"}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get(
                "/api/v1/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 200
            # Verify the request was made to the correct service
            mock_client.request.assert_called_once()
            call_args = mock_client.request.call_args
            assert settings.user_service_url in call_args[1]["url"]

    def test_proxy_catalog_service_no_auth(self, client):
        """Test proxying GET requests to catalog service without auth."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock successful response from catalog service
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"movies": []}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get("/api/v1/movies")

            assert response.status_code == 200

    def test_proxy_booking_service(self, client, valid_jwt_token):
        """Test proxying requests to booking service."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"bookings": []}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get(
                "/api/v1/bookings/list",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 200
            # Verify routing to booking service
            call_args = mock_client.request.call_args
            assert settings.booking_service_url in call_args[1]["url"]

    def test_proxy_payment_service(self, client, valid_jwt_token):
        """Test proxying requests to payment service."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b'{"paymentId": "pay_123"}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.post(
                "/api/v1/payments/create",
                json={"amount": 100, "bookingId": 123},
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 201

    def test_proxy_preserves_query_params(self, client, valid_jwt_token):
        """Test that query parameters are preserved when proxying."""
        with patch("app.routes.proxy.http_client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"data": []}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get(
                "/api/v1/movies?page=2&limit=10",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            # Verify query params were included in the proxied request
            call_args = mock_client.request.call_args
            assert "page=2" in call_args[1]["url"]
            assert "limit=10" in call_args[1]["url"]

    def test_proxy_preserves_request_body(self, client, valid_jwt_token):
        """Test that request body is preserved when proxying."""
        with patch("app.routes.proxy.http_client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b'{"id": 123}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            request_body = {"name": "Test Movie", "genre": "Action"}
            response = client.post(
                "/api/v1/movies",
                json=request_body,
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            # Verify the request body was passed through
            call_args = mock_client.request.call_args
            assert call_args[1]["content"] is not None

    def test_proxy_adds_user_headers(self, client, valid_jwt_token):
        """Test that user information headers are added to proxied requests."""
        with patch("app.routes.proxy.http_client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"data": "test"}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            response = client.get(
                "/api/v1/users/profile",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            # Verify X-User-Id header was added
            call_args = mock_client.request.call_args
            headers = call_args[1]["headers"]
            assert "X-User-Id" in headers
            assert headers["X-User-Id"] == "123"

    def test_proxy_unknown_service_404(self, client, valid_jwt_token):
        """Test that unknown service paths return 404."""
        response = client.get(
            "/api/v1/unknown/endpoint",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "SERVICE_NOT_FOUND"

    def test_proxy_backend_timeout(self, client, valid_jwt_token):
        """Test handling of backend service timeout."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock timeout exception
            mock_client.request = MagicMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            response = client.get(
                "/api/v1/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 504
            data = response.json()
            assert data["error"]["code"] == "GATEWAY_TIMEOUT"

    def test_proxy_backend_connection_error(self, client, valid_jwt_token):
        """Test handling of backend service connection error."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock connection error
            mock_client.request = MagicMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            response = client.get(
                "/api/v1/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 503
            data = response.json()
            assert data["error"]["code"] == "SERVICE_UNAVAILABLE"

    def test_proxy_backend_generic_error(self, client, valid_jwt_token):
        """Test handling of generic backend errors."""
        with patch("app.routes.proxy.http_client") as mock_client:
            # Mock generic exception
            mock_client.request = MagicMock(
                side_effect=Exception("Unexpected error")
            )

            response = client.get(
                "/api/v1/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 502
            data = response.json()
            assert data["error"]["code"] == "BAD_GATEWAY"

    def test_legacy_routes(self, client, valid_jwt_token):
        """Test that legacy routes (without /v1) still work."""
        with patch("app.routes.proxy.http_client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'{"data": "test"}'
            mock_response.headers = {"content-type": "application/json"}
            mock_client.request = MagicMock(return_value=mock_response)

            # Test legacy user route
            response = client.get(
                "/api/users/123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"},
            )

            assert response.status_code == 200
