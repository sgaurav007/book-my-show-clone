"""Configuration settings for Notification Service"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="allow")

    # Application
    app_name: str = "notification-service"
    debug: bool = False
    api_prefix: str = "/api/notifications"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5436/notification_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group_id: str = "notification-service"
    kafka_auto_offset_reset: str = "earliest"
    kafka_enable_auto_commit: bool = True
    kafka_max_poll_records: int = 10

    # Kafka Topics
    kafka_topic_booking_confirmed: str = "booking.confirmed"
    kafka_topic_booking_cancelled: str = "booking.cancelled"
    kafka_topic_payment_success: str = "payment.success"
    kafka_topic_payment_failed: str = "payment.failed"

    # Email Configuration
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = False
    smtp_from_email: str = "noreply@bookmyshow.com"
    smtp_from_name: str = "BookMyShow"

    # SMS Configuration (Mock Twilio)
    sms_enabled: bool = True
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = "+1234567890"

    # Logging
    log_level: str = "INFO"


settings = Settings()
