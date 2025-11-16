import logging
import random
import string
import time
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.kafka_producer import PaymentEventPublisher
from app.models.payment import Payment, PaymentStatus
from app.repositories.payment_repository import PaymentRepository
from app.repositories.payment_audit_log_repository import PaymentAuditLogRepository
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services.gateway_adapter import MockPaymentGatewayAdapter

logger = logging.getLogger(__name__)


class PaymentAlreadyProcessedException(Exception):
    pass


class PaymentNotFoundException(Exception):
    pass


class PaymentService:
    def __init__(
        self,
        db: AsyncSession,
        event_publisher: PaymentEventPublisher,
        gateway_adapter: MockPaymentGatewayAdapter,
    ):
        self.payment_repo = PaymentRepository(db)
        self.audit_repo = PaymentAuditLogRepository(db)
        self.event_publisher = event_publisher
        self.gateway_adapter = gateway_adapter

    async def initiate_payment(self, request: PaymentRequest) -> PaymentResponse:
        logger.info(f"Initiating payment for booking ID: {request.booking_id}")

        # Check if payment already exists for this booking
        if await self.payment_repo.exists_by_booking_id(request.booking_id):
            raise PaymentAlreadyProcessedException("Payment already exists for this booking")

        # Create payment record
        payment = Payment(
            payment_reference=self._generate_payment_reference(),
            booking_id=request.booking_id,
            user_id=request.user_id,
            amount=request.amount,
            currency="INR",
            payment_method=request.payment_method,
            payment_status=PaymentStatus.INITIATED,
            gateway_name=request.gateway_name,
        )

        saved_payment = await self.payment_repo.save(payment)

        # Initiate payment with gateway
        gateway_response = await self.gateway_adapter.initiate_payment(
            saved_payment.payment_reference, saved_payment.amount, request.payment_method
        )

        # Update payment with gateway transaction ID
        saved_payment.gateway_transaction_id = gateway_response.transaction_id
        await self.payment_repo.update(saved_payment)

        # Log audit event
        await self.audit_repo.create(
            saved_payment.id,
            "PAYMENT_INITIATED",
            {
                "paymentReference": saved_payment.payment_reference,
                "amount": str(saved_payment.amount),
                "gatewayTransactionId": gateway_response.transaction_id or "N/A",
            },
        )

        # Publish Kafka event
        await self.event_publisher.publish_payment_initiated(saved_payment)

        logger.info(f"Payment initiated successfully: {saved_payment.payment_reference}")

        # Create response
        response = PaymentResponse.model_validate(saved_payment)
        response.payment_url = gateway_response.payment_url
        return response

    async def confirm_payment(self, payment_reference: str, gateway_transaction_id: str):
        logger.info(f"Confirming payment: {payment_reference}")

        payment = await self.payment_repo.find_by_payment_reference(payment_reference)
        if not payment:
            raise PaymentNotFoundException(f"Payment not found: {payment_reference}")

        # Idempotent - if already confirmed, just return
        if payment.payment_status == PaymentStatus.SUCCESS:
            logger.warning(f"Payment already confirmed: {payment_reference}")
            return

        payment.payment_status = PaymentStatus.SUCCESS
        payment.gateway_transaction_id = gateway_transaction_id
        await self.payment_repo.update(payment)

        # Log audit event
        await self.audit_repo.create(
            payment.id,
            "PAYMENT_CONFIRMED",
            {
                "paymentReference": payment_reference,
                "gatewayTransactionId": gateway_transaction_id,
            },
        )

        # Publish Kafka event
        await self.event_publisher.publish_payment_success(payment)

        logger.info(f"Payment confirmed successfully: {payment_reference}")

    async def fail_payment(self, payment_reference: str, failure_reason: str):
        logger.info(f"Failing payment: {payment_reference}")

        payment = await self.payment_repo.find_by_payment_reference(payment_reference)
        if not payment:
            raise PaymentNotFoundException(f"Payment not found: {payment_reference}")

        payment.payment_status = PaymentStatus.FAILED
        payment.failure_reason = failure_reason
        await self.payment_repo.update(payment)

        # Log audit event
        await self.audit_repo.create(
            payment.id,
            "PAYMENT_FAILED",
            {"paymentReference": payment_reference, "failureReason": failure_reason},
        )

        # Publish Kafka event
        await self.event_publisher.publish_payment_failed(payment)

        logger.error(f"Payment failed: {payment_reference}, reason: {failure_reason}")

    async def get_payment_by_id(self, payment_id: int) -> PaymentResponse:
        payment = await self.payment_repo.find_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundException(f"Payment not found with id: {payment_id}")
        return PaymentResponse.model_validate(payment)

    async def get_payment_by_booking_id(self, booking_id: int) -> PaymentResponse:
        payment = await self.payment_repo.find_by_booking_id(booking_id)
        if not payment:
            raise PaymentNotFoundException(f"Payment not found for booking: {booking_id}")
        return PaymentResponse.model_validate(payment)

    def _generate_payment_reference(self) -> str:
        timestamp = int(time.time() * 1000)
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"PAY{timestamp}{random_str}"
