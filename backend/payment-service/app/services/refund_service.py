import logging
import random
import string
import time
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.kafka_producer import PaymentEventPublisher
from app.models.payment import Payment, PaymentStatus
from app.models.refund import Refund, RefundStatus
from app.repositories.payment_repository import PaymentRepository
from app.repositories.refund_repository import RefundRepository
from app.schemas.refund import RefundRequest, RefundResponse
from app.services.gateway_adapter import MockPaymentGatewayAdapter

logger = logging.getLogger(__name__)


class RefundService:
    def __init__(
        self,
        db: AsyncSession,
        event_publisher: PaymentEventPublisher,
        gateway_adapter: MockPaymentGatewayAdapter,
    ):
        self.payment_repo = PaymentRepository(db)
        self.refund_repo = RefundRepository(db)
        self.event_publisher = event_publisher
        self.gateway_adapter = gateway_adapter

    async def process_refund(self, request: RefundRequest) -> RefundResponse:
        logger.info(f"Processing refund for payment: {request.payment_id}")

        # Get payment
        payment = await self.payment_repo.find_by_id(request.payment_id)
        if not payment:
            raise Exception(f"Payment not found with id: {request.payment_id}")

        if payment.payment_status != PaymentStatus.SUCCESS:
            raise Exception(f"Payment is not in SUCCESS status: {payment.payment_status}")

        # Create refund record
        refund = Refund(
            payment_id=request.payment_id,
            refund_amount=request.refund_amount,
            refund_status=RefundStatus.INITIATED,
            refund_reference=self._generate_refund_reference(),
            reason=request.reason,
        )

        saved_refund = await self.refund_repo.save(refund)

        # Process refund with gateway
        if payment.gateway_transaction_id:
            gateway_response = await self.gateway_adapter.process_refund(
                payment.gateway_transaction_id, request.refund_amount
            )
            saved_refund.gateway_refund_id = gateway_response.transaction_id
            saved_refund.refund_status = (
                RefundStatus.SUCCESS if gateway_response.success else RefundStatus.FAILED
            )
            await self.refund_repo.update(saved_refund)

        # Update payment status to REFUNDED
        payment.payment_status = PaymentStatus.REFUNDED
        await self.payment_repo.update(payment)

        # Publish Kafka event
        await self.event_publisher.publish_refund_processed(saved_refund, payment)

        logger.info(f"Refund processed successfully: {saved_refund.refund_reference}")

        return RefundResponse.model_validate(saved_refund)

    async def get_refunds_by_payment_id(self, payment_id: int) -> List[RefundResponse]:
        refunds = await self.refund_repo.find_by_payment_id(payment_id)
        return [RefundResponse.model_validate(refund) for refund in refunds]

    def _generate_refund_reference(self) -> str:
        timestamp = int(time.time() * 1000)
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"REF{timestamp}{random_str}"
