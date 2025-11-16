"""Application configuration using Pydantic Settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "User Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/user_service"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "bookmyshow-secret-key-for-jwt-token-generation-and-validation-must-be-at-least-256-bits"
    jwt_algorithm: str = "HS256"
    access_token_expiration: int = 3600000  # 1 hour in milliseconds
    refresh_token_expiration: int = 86400000  # 24 hours in milliseconds

    # CORS
    cors_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"


def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings instance
    """
    return Settings()
