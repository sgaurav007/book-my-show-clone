from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Service info
    service_name: str = "booking-service"
    service_port: int = 8082

    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/booking_db"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Kafka settings
    kafka_bootstrap_servers: str = "localhost:9092"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
