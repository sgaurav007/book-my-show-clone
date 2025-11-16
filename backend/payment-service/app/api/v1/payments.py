import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_db,
    get_payment_service,
    get_refund_service,
)
from app.schemas.payment import PaymentRequest, PaymentResponse, WebhookRequest
from app.schemas.refund import RefundRequest, RefundResponse
from app.services.payment_service import (
    PaymentService,
    PaymentAlreadyProcessedException,
    PaymentNotFoundException,
)
from app.services.refund_service import RefundService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/initiate", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def initiate_payment(
    request: PaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Initiate a new payment"""
    try:
        logger.info(f"Received payment initiation request for booking: {request.booking_id}")
        response = await payment_service.initiate_payment(request)
        return response
    except PaymentAlreadyProcessedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating payment: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}", response_model=PaymentResponse)
async def get_payment_by_id(
    id: int,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Get payment by ID"""
    try:
        logger.info(f"Fetching payment by id: {id}")
        response = await payment_service.get_payment_by_id(id)
        return response
    except PaymentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching payment: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/booking/{bookingId}", response_model=PaymentResponse)
async def get_payment_by_booking_id(
    bookingId: int,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Get payment by booking ID"""
    try:
        logger.info(f"Fetching payment by booking id: {bookingId}")
        response = await payment_service.get_payment_by_booking_id(bookingId)
        return response
    except PaymentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching payment: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_webhook(
    request: WebhookRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Handle payment gateway webhook"""
    try:
        logger.info(
            f"Received webhook for payment: {request.payment_reference} with status: {request.status}"
        )

        if request.status.upper() == "SUCCESS":
            await payment_service.confirm_payment(
                request.payment_reference, request.gateway_transaction_id
            )
        elif request.status.upper() == "FAILED":
            await payment_service.fail_payment(
                request.payment_reference, request.failure_reason or "Payment failed"
            )

        return {"message": "Webhook processed successfully"}
    except PaymentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/refund", response_model=RefundResponse, status_code=status.HTTP_200_OK)
async def process_refund(
    request: RefundRequest,
    refund_service: RefundService = Depends(get_refund_service),
):
    """Process a refund"""
    try:
        logger.info(f"Received refund request for payment: {request.payment_id}")
        response = await refund_service.process_refund(request)
        return response
    except Exception as e:
        logger.error(f"Error processing refund: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{paymentId}/refunds", response_model=List[RefundResponse])
async def get_refunds_by_payment_id(
    paymentId: int,
    refund_service: RefundService = Depends(get_refund_service),
):
    """Get all refunds for a payment"""
    try:
        logger.info(f"Fetching refunds for payment: {paymentId}")
        refunds = await refund_service.get_refunds_by_payment_id(paymentId)
        return refunds
    except Exception as e:
        logger.error(f"Error fetching refunds: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
