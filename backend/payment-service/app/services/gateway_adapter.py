import asyncio
import logging
import random
import uuid
from decimal import Decimal

from app.models.payment import PaymentMethod
from app.schemas.payment import GatewayResponse

logger = logging.getLogger(__name__)


class MockPaymentGatewayAdapter:
    def __init__(self, success_rate: float = 0.9, processing_time_ms: int = 1000):
        self.success_rate = success_rate
        self.processing_time_ms = processing_time_ms

    async def initiate_payment(
        self, payment_reference: str, amount: Decimal, payment_method: PaymentMethod
    ) -> GatewayResponse:
        logger.info(
            f"Initiating payment with gateway - Reference: {payment_reference}, "
            f"Amount: {amount}, Method: {payment_method}"
        )

        await self._simulate_processing_delay()

        is_success = random.random() < self.success_rate

        if is_success:
            transaction_id = f"TXN_{uuid.uuid4().hex[:16]}"
            payment_url = f"https://mock-gateway.com/pay/{payment_reference}"

            logger.info(f"Payment initiated successfully - Transaction ID: {transaction_id}")

            return GatewayResponse(
                transaction_id=transaction_id,
                payment_url=payment_url,
                success=True,
                message="Payment initiated successfully",
            )
        else:
            logger.warning(f"Payment initiation failed for reference: {payment_reference}")

            return GatewayResponse(
                transaction_id=None,
                payment_url=None,
                success=False,
                message="Payment failed",
            )

    async def process_refund(self, transaction_id: str, refund_amount: Decimal) -> GatewayResponse:
        logger.info(f"Processing refund - Transaction ID: {transaction_id}, Amount: {refund_amount}")

        await self._simulate_processing_delay()

        refund_id = f"REFUND_{uuid.uuid4().hex[:16]}"

        logger.info(f"Refund processed successfully - Refund ID: {refund_id}")

        return GatewayResponse(
            transaction_id=refund_id,
            payment_url=None,
            success=True,
            message="Refund processed successfully",
        )

    async def _simulate_processing_delay(self):
        if self.processing_time_ms > 0:
            await asyncio.sleep(self.processing_time_ms / 1000.0)
