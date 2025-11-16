import pytest
from decimal import Decimal
from unittest.mock import AsyncMock

from app.models.payment import PaymentMethod, PaymentStatus
from app.schemas.payment import PaymentRequest
from app.schemas.refund import RefundRequest
from app.services.payment_service import PaymentService
from app.services.refund_service import RefundService


@pytest.mark.asyncio
async def test_process_refund(test_session, mock_event_publisher, mock_gateway_adapter):
    """Test refund processing"""
    payment_service = PaymentService(test_session, mock_event_publisher, mock_gateway_adapter)
    refund_service = RefundService(test_session, mock_event_publisher, mock_gateway_adapter)
    
    # Mock all event publisher methods
    mock_event_publisher.publish_payment_initiated = AsyncMock()
    mock_event_publisher.publish_payment_success = AsyncMock()
    mock_event_publisher.publish_refund_processed = AsyncMock()
    
    # Create and confirm a payment
    payment_request = PaymentRequest(
        booking_id=10,
        user_id=1,
        amount=Decimal("500.00"),
        payment_method=PaymentMethod.CARD,
    )
    
    payment_response = await payment_service.initiate_payment(payment_request)
    await payment_service.confirm_payment(payment_response.payment_reference, "TXN999")
    
    # Process refund
    refund_request = RefundRequest(
        payment_id=payment_response.id,
        refund_amount=Decimal("500.00"),
        reason="Customer request",
    )
    
    refund_response = await refund_service.process_refund(refund_request)
    
    assert refund_response.payment_id == payment_response.id
    assert refund_response.refund_amount == Decimal("500.00")
    assert refund_response.reason == "Customer request"
    assert refund_response.refund_reference is not None


@pytest.mark.asyncio
async def test_get_refunds_by_payment_id(test_session, mock_event_publisher, mock_gateway_adapter):
    """Test getting refunds by payment ID"""
    payment_service = PaymentService(test_session, mock_event_publisher, mock_gateway_adapter)
    refund_service = RefundService(test_session, mock_event_publisher, mock_gateway_adapter)
    
    # Mock event publisher methods
    mock_event_publisher.publish_payment_initiated = AsyncMock()
    mock_event_publisher.publish_payment_success = AsyncMock()
    mock_event_publisher.publish_refund_processed = AsyncMock()
    
    # Create and confirm a payment
    payment_request = PaymentRequest(
        booking_id=11,
        user_id=1,
        amount=Decimal("600.00"),
        payment_method=PaymentMethod.UPI,
    )
    
    payment_response = await payment_service.initiate_payment(payment_request)
    await payment_service.confirm_payment(payment_response.payment_reference, "TXN888")
    
    # Process refund
    refund_request = RefundRequest(
        payment_id=payment_response.id,
        refund_amount=Decimal("300.00"),
        reason="Partial refund",
    )
    
    await refund_service.process_refund(refund_request)
    
    # Get refunds
    refunds = await refund_service.get_refunds_by_payment_id(payment_response.id)
    assert len(refunds) == 1
    assert refunds[0].refund_amount == Decimal("300.00")
