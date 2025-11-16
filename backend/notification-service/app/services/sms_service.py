"""SMS Service"""
import logging
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class SmsService:
    """Service for sending SMS (Mock implementation)"""

    SMS_MAX_LENGTH = 160
    DATE_TIME_FORMAT = "%d %b, %I:%M %p"

    def __init__(self):
        """Initialize SMS service"""
        pass

    async def send_booking_confirmation_sms(
        self,
        phone_number: str,
        booking_reference: str,
        movie_title: str,
        show_date_time: datetime,
    ) -> None:
        """Send booking confirmation SMS"""
        message = (
            f"BookMyShow: Booking confirmed! Ref: {booking_reference}, "
            f"Movie: {movie_title}, Time: {self._format_datetime(show_date_time)}. "
            f"Show this SMS at counter."
        )

        truncated_message = self._truncate_sms(message)

        logger.info("=" * 58)
        logger.info("SENDING BOOKING CONFIRMATION SMS")
        logger.info("=" * 58)
        logger.info(f"To: {self._format_phone_number(phone_number)}")
        logger.info(f"Message: {truncated_message}")
        logger.info("=" * 58)

    async def send_booking_cancellation_sms(
        self,
        phone_number: str,
        booking_reference: str,
        movie_title: str,
        refund_amount: Decimal,
    ) -> None:
        """Send booking cancellation SMS"""
        message = (
            f"BookMyShow: Booking {booking_reference} cancelled. "
            f"Movie: {movie_title}. "
            f"Refund of Rs. {refund_amount} will be processed in 5-7 days."
        )

        truncated_message = self._truncate_sms(message)

        logger.info("=" * 58)
        logger.info("SENDING BOOKING CANCELLATION SMS")
        logger.info("=" * 58)
        logger.info(f"To: {self._format_phone_number(phone_number)}")
        logger.info(f"Message: {truncated_message}")
        logger.info("=" * 58)

    async def send_payment_success_sms(
        self,
        phone_number: str,
        payment_reference: str,
        amount: Decimal,
    ) -> None:
        """Send payment success SMS"""
        message = (
            f"BookMyShow: Payment of Rs. {amount} received successfully. "
            f"Ref: {payment_reference}. Thank you!"
        )

        truncated_message = self._truncate_sms(message)

        logger.info("=" * 58)
        logger.info("SENDING PAYMENT SUCCESS SMS")
        logger.info("=" * 58)
        logger.info(f"To: {self._format_phone_number(phone_number)}")
        logger.info(f"Message: {truncated_message}")
        logger.info("=" * 58)

    async def send_payment_failure_sms(
        self,
        phone_number: str,
        payment_reference: str,
        amount: Decimal,
        failure_reason: str,
    ) -> None:
        """Send payment failure SMS"""
        message = (
            f"BookMyShow: Payment of Rs. {amount} failed. "
            f"Ref: {payment_reference}. Reason: {failure_reason}. Please try again."
        )

        truncated_message = self._truncate_sms(message)

        logger.info("=" * 58)
        logger.info("SENDING PAYMENT FAILURE SMS")
        logger.info("=" * 58)
        logger.info(f"To: {self._format_phone_number(phone_number)}")
        logger.info(f"Message: {truncated_message}")
        logger.info("=" * 58)

    def _truncate_sms(self, message: str) -> str:
        """Truncate SMS to max length"""
        if not message:
            return ""
        if len(message) <= self.SMS_MAX_LENGTH:
            return message
        return message[: self.SMS_MAX_LENGTH - 3] + "..."

    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number with masking"""
        if not phone_number:
            return ""
        if len(phone_number) <= 6:
            return phone_number
        visible_digits = 4
        masked_length = len(phone_number) - visible_digits
        return "*" * masked_length + phone_number[masked_length:]

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime"""
        if dt is None:
            return ""
        return dt.strftime(self.DATE_TIME_FORMAT)
