import json
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer
from app.schemas.booking import (
    BookingCreateEvent,
    BookingConfirmedEvent,
    BookingCancelledEvent,
)

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Kafka producer for publishing booking events"""

    BOOKING_CREATED_TOPIC = "booking-created"
    BOOKING_CONFIRMED_TOPIC = "booking-confirmed"
    BOOKING_CANCELLED_TOPIC = "booking-cancelled"

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Start the Kafka producer"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(
                    v, default=self._json_serializer
                ).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
            await self.producer.start()
            logger.info(f"Kafka producer started: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and Decimal objects"""
        from datetime import datetime
        from decimal import Decimal

        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    async def publish_booking_created(self, event: BookingCreateEvent):
        """Publish booking created event"""
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return

        try:
            event_dict = event.model_dump()
            await self.producer.send_and_wait(
                self.BOOKING_CREATED_TOPIC,
                value=event_dict,
                key=str(event.booking_id),
            )
            logger.info(
                f"Published BookingCreatedEvent for booking: {event.booking_reference}"
            )
        except Exception as e:
            logger.error(f"Failed to publish BookingCreatedEvent: {e}")

    async def publish_booking_confirmed(self, event: BookingConfirmedEvent):
        """Publish booking confirmed event"""
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return

        try:
            event_dict = event.model_dump()
            await self.producer.send_and_wait(
                self.BOOKING_CONFIRMED_TOPIC,
                value=event_dict,
                key=str(event.booking_id),
            )
            logger.info(
                f"Published BookingConfirmedEvent for booking: {event.booking_reference}"
            )
        except Exception as e:
            logger.error(f"Failed to publish BookingConfirmedEvent: {e}")

    async def publish_booking_cancelled(self, event: BookingCancelledEvent):
        """Publish booking cancelled event"""
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return

        try:
            event_dict = event.model_dump()
            await self.producer.send_and_wait(
                self.BOOKING_CANCELLED_TOPIC,
                value=event_dict,
                key=str(event.booking_id),
            )
            logger.info(
                f"Published BookingCancelledEvent for booking: {event.booking_reference}"
            )
        except Exception as e:
            logger.error(f"Failed to publish BookingCancelledEvent: {e}")
