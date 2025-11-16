"""Kafka client utilities for async producer and consumer."""

import json
import logging
from typing import Any, Callable, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Async Kafka producer wrapper."""

    def __init__(self, bootstrap_servers: str):
        """Initialize Kafka producer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Start Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        """Stop Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send(self, topic: str, value: dict[str, Any], key: Optional[str] = None):
        """Send message to Kafka topic.
        
        Args:
            topic: Topic name
            value: Message value (will be JSON serialized)
            key: Optional message key
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not started")
        
        key_bytes = key.encode("utf-8") if key else None
        await self.producer.send(topic, value=value, key=key_bytes)
        logger.debug(f"Sent message to topic {topic}: {value}")


class KafkaConsumer:
    """Async Kafka consumer wrapper."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
    ):
        """Initialize Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            group_id: Consumer group ID
            topics: List of topics to subscribe to
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.consumer: Optional[AIOKafkaConsumer] = None

    async def start(self):
        """Start Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topics: {self.topics}")

    async def stop(self):
        """Stop Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(self, handler: Callable[[dict[str, Any]], Any]):
        """Consume messages from Kafka topics.
        
        Args:
            handler: Async function to handle each message
        """
        if not self.consumer:
            raise RuntimeError("Kafka consumer not started")
        
        try:
            async for message in self.consumer:
                try:
                    await handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error consuming messages: {e}", exc_info=True)
            raise


class KafkaEventPublisher:
    """Event publisher for domain events."""

    def __init__(self, producer: KafkaProducer):
        """Initialize event publisher.
        
        Args:
            producer: Kafka producer instance
        """
        self.producer = producer

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: dict[str, Any],
        entity_id: Optional[str] = None,
    ):
        """Publish domain event.
        
        Args:
            topic: Topic name
            event_type: Type of event
            data: Event data
            entity_id: Optional entity ID to use as message key
        """
        event = {
            "event_type": event_type,
            "data": data,
        }
        
        await self.producer.send(topic, value=event, key=entity_id)
        logger.info(f"Published event {event_type} to topic {topic}")
