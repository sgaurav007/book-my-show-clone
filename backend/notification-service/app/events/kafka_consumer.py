"""Kafka Consumer Manager"""
import asyncio
import json
import logging
from typing import Callable, Dict
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from app.config import Settings

logger = logging.getLogger(__name__)


class KafkaConsumerManager:
    """Manages Kafka consumers for different topics"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.handlers: Dict[str, Callable] = {}
        self._running = False

    def register_handler(self, topic: str, handler: Callable):
        """Register a message handler for a topic"""
        self.handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")

    async def start(self):
        """Start all Kafka consumers"""
        if self._running:
            logger.warning("Kafka consumers are already running")
            return

        logger.info("Starting Kafka consumers...")
        self._running = True

        for topic, handler in self.handlers.items():
            await self._start_consumer(topic, handler)

        logger.info(f"Started {len(self.consumers)} Kafka consumers")

    async def _start_consumer(self, topic: str, handler: Callable):
        """Start a consumer for a specific topic"""
        try:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.settings.kafka_bootstrap_servers,
                group_id=self.settings.kafka_consumer_group_id,
                auto_offset_reset=self.settings.kafka_auto_offset_reset,
                enable_auto_commit=self.settings.kafka_enable_auto_commit,
                max_poll_records=self.settings.kafka_max_poll_records,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )

            await consumer.start()
            self.consumers[topic] = consumer

            # Start consumer task
            task = asyncio.create_task(self._consume_messages(topic, consumer, handler))
            self.tasks[topic] = task

            logger.info(f"Started consumer for topic: {topic}")

        except KafkaError as e:
            logger.error(f"Failed to start consumer for topic {topic}: {e}")
            raise

    async def _consume_messages(
        self, topic: str, consumer: AIOKafkaConsumer, handler: Callable
    ):
        """Consume messages from a topic"""
        logger.info(f"Consuming messages from topic: {topic}")

        try:
            async for message in consumer:
                try:
                    logger.debug(
                        f"Received message from {topic}: partition={message.partition}, "
                        f"offset={message.offset}"
                    )

                    # Call the handler
                    await handler(message.value)

                except Exception as e:
                    logger.error(
                        f"Error processing message from {topic}: {e}",
                        exc_info=True,
                    )
                    # Continue processing other messages

        except asyncio.CancelledError:
            logger.info(f"Consumer task for topic {topic} was cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in consumer loop for topic {topic}: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop all Kafka consumers"""
        if not self._running:
            logger.warning("Kafka consumers are not running")
            return

        logger.info("Stopping Kafka consumers...")
        self._running = False

        # Cancel all consumer tasks
        for topic, task in self.tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"Consumer task for topic {topic} cancelled")

        # Stop all consumers
        for topic, consumer in self.consumers.items():
            try:
                await consumer.stop()
                logger.info(f"Stopped consumer for topic: {topic}")
            except Exception as e:
                logger.error(f"Error stopping consumer for topic {topic}: {e}")

        self.consumers.clear()
        self.tasks.clear()

        logger.info("All Kafka consumers stopped")

    @asynccontextmanager
    async def lifespan(self):
        """Context manager for consumer lifecycle"""
        try:
            await self.start()
            yield
        finally:
            await self.stop()
