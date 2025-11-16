"""Configuration settings for the API Gateway."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = 8080

    # JWT Configuration
    jwt_secret: str = Field(
        default="bookmyshow-super-secret-key-change-in-production-minimum-256-bits-required-for-hmac-sha256-algorithm",
        env="JWT_SECRET"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400000  # milliseconds

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    cors_expose_headers: List[str] = ["Authorization", "X-User-Id", "X-Username", "X-User-Role"]
    cors_max_age: int = 3600

    # Backend Service URLs
    user_service_url: str = Field(
        default="http://localhost:8081",
        env="USER_SERVICE_URL"
    )
    catalog_service_url: str = Field(
        default="http://localhost:8082",
        env="CATALOG_SERVICE_URL"
    )
    booking_service_url: str = Field(
        default="http://localhost:8083",
        env="BOOKING_SERVICE_URL"
    )
    payment_service_url: str = Field(
        default="http://localhost:8084",
        env="PAYMENT_SERVICE_URL"
    )
    notification_service_url: str = Field(
        default="http://localhost:8085",
        env="NOTIFICATION_SERVICE_URL"
    )

    # Redis Configuration (for rate limiting)
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds

    # HTTP Client Configuration
    http_timeout: int = 30  # seconds
    http_pool_connections: int = 100
    http_pool_maxsize: int = 100

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = "json"  # json or text

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
