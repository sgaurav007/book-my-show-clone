import json
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from app.models.payment import Payment
from app.models.refund import Refund

logger = logging.getLogger(__name__)


class PaymentEventData(BaseModel):
    payment_id: int
    payment_reference: str
    booking_id: int
    user_id: int
    amount: Decimal
    currency: str
    payment_method: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None

    class Config:
        json_encoders = {Decimal: str}


class PaymentEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    data: PaymentEventData

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), Decimal: str}


class PaymentEventPublisher:
    PAYMENT_INITIATED_TOPIC = "payment.initiated"
    PAYMENT_SUCCESS_TOPIC = "payment.success"
    PAYMENT_FAILED_TOPIC = "payment.failed"
    PAYMENT_REFUNDED_TOPIC = "payment.refunded"

    def __init__(self, producer: Optional[AIOKafkaProducer] = None):
        self.producer = producer

    async def publish_payment_initiated(self, payment: Payment):
        event = self._create_payment_event("PAYMENT_INITIATED", payment)
        await self._send_event(
            self.PAYMENT_INITIATED_TOPIC, payment.payment_reference, event
        )
        logger.info(f"Published payment initiated event for: {payment.payment_reference}")

    async def publish_payment_success(self, payment: Payment):
        event = self._create_payment_event("PAYMENT_SUCCESS", payment)
        await self._send_event(self.PAYMENT_SUCCESS_TOPIC, payment.payment_reference, event)
        logger.info(f"Published payment success event for: {payment.payment_reference}")

    async def publish_payment_failed(self, payment: Payment):
        event = self._create_payment_event("PAYMENT_FAILED", payment)
        await self._send_event(self.PAYMENT_FAILED_TOPIC, payment.payment_reference, event)
        logger.info(f"Published payment failed event for: {payment.payment_reference}")

    async def publish_refund_processed(self, refund: Refund, payment: Payment):
        data = PaymentEventData(
            payment_id=payment.id,
            payment_reference=payment.payment_reference,
            booking_id=payment.booking_id,
            user_id=payment.user_id,
            amount=refund.refund_amount,
            currency=payment.currency,
            payment_method=payment.payment_method.value if payment.payment_method else None,
            gateway_transaction_id=payment.gateway_transaction_id,
            status=payment.payment_status.value,
            failure_reason=None,
        )

        event = PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type="PAYMENT_REFUNDED",
            timestamp=datetime.utcnow(),
            data=data,
        )

        await self._send_event(
            self.PAYMENT_REFUNDED_TOPIC, payment.payment_reference, event
        )
        logger.info(f"Published refund processed event for payment: {payment.payment_reference}")

    def _create_payment_event(self, event_type: str, payment: Payment) -> PaymentEvent:
        data = PaymentEventData(
            payment_id=payment.id,
            payment_reference=payment.payment_reference,
            booking_id=payment.booking_id,
            user_id=payment.user_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method.value if payment.payment_method else None,
            gateway_transaction_id=payment.gateway_transaction_id,
            status=payment.payment_status.value,
            failure_reason=payment.failure_reason,
        )

        return PaymentEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
        )

    async def _send_event(self, topic: str, key: str, event: PaymentEvent):
        if not self.producer:
            logger.warning(f"Kafka producer not configured, skipping event: {event.event_type}")
            return

        try:
            event_json = event.model_dump_json()
            await self.producer.send_and_wait(
                topic, key=key.encode("utf-8"), value=event_json.encode("utf-8")
            )
        except Exception as e:
            logger.error(f"Failed to publish event to Kafka: {e}", exc_info=True)
            raise
