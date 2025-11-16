"""Booking Event Handler"""
import json
import logging
from typing import Dict, Any

from pydantic import ValidationError

from app.schemas.notification import BookingConfirmedEvent, BookingCancelledEvent
from app.services.email_service import EmailService
from app.services.sms_service import SmsService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class BookingEventHandler:
    """Handler for booking events"""

    def __init__(
        self,
        email_service: EmailService,
        sms_service: SmsService,
        notification_service: NotificationService,
    ):
        self.email_service = email_service
        self.sms_service = sms_service
        self.notification_service = notification_service

    async def handle_booking_confirmed(self, message: Dict[str, Any]):
        """Handle booking confirmed event"""
        try:
            # Parse event
            event = BookingConfirmedEvent(**message)
            data = event.data

            logger.info(
                f"Processing booking confirmed event: bookingId={data.booking_id}, "
                f"reference={data.booking_reference}"
            )

            # Send email notification
            try:
                await self.email_service.send_booking_confirmation_email(
                    email=data.user_email,
                    booking_reference=data.booking_reference,
                    movie_title=data.movie_title,
                    theater_name=data.theater_name,
                    show_date_time=data.show_date_time,
                    seats=data.seats,
                    total_amount=data.total_amount,
                )

                # Record successful email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CONFIRMED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Booking Confirmation - {data.booking_reference}",
                    content=f"Your booking for {data.movie_title} has been confirmed",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Booking confirmation email sent successfully: {data.booking_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send booking confirmation email: {data.booking_reference}",
                    exc_info=True,
                )
                # Record failed email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CONFIRMED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Booking Confirmation - {data.booking_reference}",
                    content=f"Your booking for {data.movie_title} has been confirmed",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

            # Send SMS notification
            try:
                await self.sms_service.send_booking_confirmation_sms(
                    phone_number=data.user_phone,
                    booking_reference=data.booking_reference,
                    movie_title=data.movie_title,
                    show_date_time=data.show_date_time,
                )

                # Record successful SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CONFIRMED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Booking Confirmation",
                    content=f"Booking confirmed for {data.movie_title}",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Booking confirmation SMS sent successfully: {data.booking_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send booking confirmation SMS: {data.booking_reference}",
                    exc_info=True,
                )
                # Record failed SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CONFIRMED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Booking Confirmation",
                    content=f"Booking confirmed for {data.movie_title}",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

        except ValidationError as e:
            logger.error(f"Invalid booking confirmed event format: {e}")
        except Exception as e:
            logger.error(f"Error handling booking confirmed event: {e}", exc_info=True)

    async def handle_booking_cancelled(self, message: Dict[str, Any]):
        """Handle booking cancelled event"""
        try:
            # Parse event
            event = BookingCancelledEvent(**message)
            data = event.data

            logger.info(
                f"Processing booking cancelled event: bookingId={data.booking_id}, "
                f"reference={data.booking_reference}"
            )

            # Send email notification
            try:
                await self.email_service.send_booking_cancellation_email(
                    email=data.user_email,
                    booking_reference=data.booking_reference,
                    movie_title=data.movie_title,
                    theater_name=data.theater_name,
                    show_date_time=data.show_date_time,
                    seats=data.seats,
                    refund_amount=data.refund_amount,
                )

                # Record successful email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CANCELLED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Booking Cancelled - {data.booking_reference}",
                    content=f"Your booking for {data.movie_title} has been cancelled",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Booking cancellation email sent successfully: {data.booking_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send booking cancellation email: {data.booking_reference}",
                    exc_info=True,
                )
                # Record failed email notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CANCELLED",
                    channel="EMAIL",
                    recipient=data.user_email,
                    subject=f"Booking Cancelled - {data.booking_reference}",
                    content=f"Your booking for {data.movie_title} has been cancelled",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

            # Send SMS notification
            try:
                await self.sms_service.send_booking_cancellation_sms(
                    phone_number=data.user_phone,
                    booking_reference=data.booking_reference,
                    movie_title=data.movie_title,
                    refund_amount=data.refund_amount,
                )

                # Record successful SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CANCELLED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Booking Cancelled",
                    content=f"Booking cancelled for {data.movie_title}",
                    status="SUCCESS",
                    metadata=json.dumps(message),
                )

                logger.info(
                    f"Booking cancellation SMS sent successfully: {data.booking_reference}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to send booking cancellation SMS: {data.booking_reference}",
                    exc_info=True,
                )
                # Record failed SMS notification
                await self.notification_service.create_notification(
                    user_id=data.user_id,
                    notification_type="BOOKING_CANCELLED",
                    channel="SMS",
                    recipient=data.user_phone,
                    subject="Booking Cancelled",
                    content=f"Booking cancelled for {data.movie_title}",
                    status="FAILED",
                    metadata=json.dumps(message),
                    error_message=str(e),
                )

        except ValidationError as e:
            logger.error(f"Invalid booking cancelled event format: {e}")
        except Exception as e:
            logger.error(f"Error handling booking cancelled event: {e}", exc_info=True)
