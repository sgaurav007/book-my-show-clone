"""Tests for logging middleware."""
import pytest
from unittest.mock import patch, MagicMock

from app.middleware.logging import get_client_ip, logging_middleware


class TestClientIP:
    """Test client IP extraction."""

    def test_get_client_ip_from_x_forwarded_for(self):
        """Test extracting IP from X-Forwarded-For header."""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "192.168.1.1, 10.0.0.1"
        }.get(key)
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_from_x_real_ip(self):
        """Test extracting IP from X-Real-IP header."""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda key: {
            "X-Real-IP": "192.168.1.2"
        }.get(key)
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.2"

    def test_get_client_ip_from_direct_connection(self):
        """Test extracting IP from direct connection."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "192.168.1.3"

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.3"

    def test_get_client_ip_unknown(self):
        """Test fallback when no IP is available."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "unknown"


class TestLoggingMiddleware:
    """Test logging middleware integration."""

    def test_logging_middleware_logs_request_and_response(self, client):
        """Test that requests and responses are logged."""
        with patch("app.middleware.logging.logger") as mock_logger:
            response = client.get("/health")

            assert response.status_code == 200

            # Verify logging was called
            assert mock_logger.info.call_count >= 2  # At least request and response logs

            # Check that request was logged
            calls = mock_logger.info.call_args_list
            request_logged = any("Incoming request" in str(call) for call in calls)
            response_logged = any("Outgoing response" in str(call) for call in calls)

            assert request_logged
            assert response_logged

    def test_logging_middleware_adds_response_time_header(self, client):
        """Test that response time header is added."""
        response = client.get("/health")

        assert "x-response-time" in response.headers
        assert response.headers["x-response-time"].endswith("ms")

    def test_logging_middleware_logs_authenticated_user(self, client, valid_jwt_token):
        """Test that authenticated user info is logged."""
        with patch("app.middleware.logging.logger") as mock_logger:
            with patch("app.routes.proxy.http_client") as mock_http:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.content = b'{"data": "test"}'
                mock_response.headers = {"content-type": "application/json"}
                mock_http.request = MagicMock(return_value=mock_response)

                response = client.get(
                    "/api/v1/users/profile",
                    headers={"Authorization": f"Bearer {valid_jwt_token}"},
                )

                # Check that user_id was logged
                calls = mock_logger.info.call_args_list
                assert any(
                    "user_id" in str(call) and "123" in str(call)
                    for call in calls
                )

    def test_logging_middleware_logs_errors(self, client, valid_jwt_token):
        """Test that errors are logged."""
        with patch("app.middleware.logging.logger") as mock_logger:
            with patch("app.routes.proxy.http_client") as mock_http:
                # Simulate backend error
                mock_http.request = MagicMock(
                    side_effect=Exception("Backend error")
                )

                response = client.get(
                    "/api/v1/users/123",
                    headers={"Authorization": f"Bearer {valid_jwt_token}"},
                )

                # Error should be logged
                assert mock_logger.error.called
