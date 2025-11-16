"""Payment Event Handler"""
import json
import logging
from typing import Dict, Any

from pydantic import ValidationError

from app.schemas.notification import PaymentSuccessEvent, PaymentFailedEvent
from app.services.email_service import EmailService
from app.services.sms_service import SmsService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PaymentEventHandler:
    """Handler for payment events"""

    def __init__(
        self,
        email_service: EmailService,
        sms_service: SmsService,
        notification_service: NotificationService,
    ):
        self.email_service = email_service
        self.sms_service = sms_service
        self.notification_service = notification_service

    async def handle_payment_success(self, message: Dict[str, Any]):
        """Handle payment success event"""
        try:
            # Parse event
            event = PaymentSuccessEvent(**message)
            data = event.data

            logger.info(
                f"Processing payment success event: paymentId={data.payment_id}, "
                f"reference={data.payment_reference}"
            )

            # Send email notification
            try:
                await self.email_service.send_payment_receipt_email(
                    email=data.user_email,
                    payment_reference=data.payment_reference,
                    amount=data.amount,
                    currency=data.currency,
                    payment_method=data.payment_method,
                )

                # Record successful email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_SUCCESS",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Payment Receipt - {data.payment_reference}",
                    content=f"Payment of {data.amount} {data.currency} received successfully",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Payment receipt email sent successfully: {data.payment_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send payment receipt email: {data.payment_reference}",
                    exc_info=True,
                )
                # Record failed email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_SUCCESS",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Payment Receipt - {data.payment_reference}",
                    content=f"Payment of {data.amount} {data.currency} received successfully",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

            # Send SMS notification
            try:
                await self.sms_service.send_payment_success_sms(
                    phone_number=data.user_phone,
                    payment_reference=data.payment_reference,
                    amount=data.amount,
                )

                # Record successful SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_SUCCESS",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Payment Received",
                    content="Payment received successfully",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Payment success SMS sent successfully: {data.payment_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send payment success SMS: {data.payment_reference}",
                    exc_info=True,
                )
                # Record failed SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_SUCCESS",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Payment Received",
                    content="Payment received successfully",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

        except ValidationError as e:
            logger.error(f"Invalid payment success event format: {e}")
        except Exception as e:
            logger.error(f"Error handling payment success event: {e}", exc_info=True)

    async def handle_payment_failed(self, message: Dict[str, Any]):
        """Handle payment failed event"""
        try:
            # Parse event
            event = PaymentFailedEvent(**message)
            data = event.data

            logger.info(
                f"Processing payment failed event: paymentId={data.payment_id}, "
                f"reference={data.payment_reference}"
            )

            # Send email notification
            try:
                await self.email_service.send_payment_failure_email(
                    email=data.user_email,
                    payment_reference=data.payment_reference,
                    amount=data.amount,
                    failure_reason=data.failure_reason,
                )

                # Record successful email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_FAILED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Payment Failed - {data.payment_reference}",
                    content=f"Payment of {data.amount} failed: {data.failure_reason}",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Payment failure email sent successfully: {data.payment_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send payment failure email: {data.payment_reference}",
                    exc_info=True,
                )
                # Record failed email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_FAILED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Payment Failed - {data.payment_reference}",
                    content=f"Payment of {data.amount} failed: {data.failure_reason}",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

            # Send SMS notification
            try:
                await self.sms_service.send_payment_failure_sms(
                    phone_number=data.user_phone,
                    payment_reference=data.payment_reference,
                    amount=data.amount,
                    failure_reason=data.failure_reason,
                )

                # Record successful SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_FAILED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Payment Failed",
                    content=f"Payment failed: {data.failure_reason}",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Payment failure SMS sent successfully: {data.payment_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send payment failure SMS: {data.payment_reference}",
                    exc_info=True,
                )
                # Record failed SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="PAYMENT_FAILED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Payment Failed",
                    content=f"Payment failed: {data.failure_reason}",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

        except ValidationError as e:
            logger.error(f"Invalid payment failed event format: {e}")
        except Exception as e:
            logger.error(f"Error handling payment failed event: {e}", exc_info=True)
