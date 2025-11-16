"""Tests for main FastAPI application."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestMainEndpoints:
    """Test main application endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns gateway information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "API Gateway"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "routes" in data

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "API Gateway"
        assert data["version"] == "1.0.0"

    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint is accessible."""
        response = client.get("/metrics")

        # Prometheus metrics endpoint should return text
        assert response.status_code == 200

    def test_openapi_docs(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "API Gateway"

    def test_cors_headers(self, client):
        """Test CORS headers are properly configured."""
        response = client.options(
            "/api/v1/users/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # CORS should allow the request
        assert "access-control-allow-origin" in response.headers
