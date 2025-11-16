from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "payment-service"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8084
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/payment_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_enabled: bool = True
    
    # Payment Gateway
    gateway_success_rate: float = 0.9
    gateway_processing_time_ms: int = 1000
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
