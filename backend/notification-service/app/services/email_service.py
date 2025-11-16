"""Email Service"""
import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from jinja2 import Template

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails (Mock implementation)"""

    DATE_TIME_FORMAT = "%d %b %Y, %I:%M %p"

    def __init__(self):
        """Initialize email service"""
        pass

    async def send_booking_confirmation_email(
        self,
        email: str,
        booking_reference: str,
        movie_title: str,
        theater_name: str,
        show_date_time: datetime,
        seats: List[str],
        total_amount: Decimal,
    ) -> None:
        """Send booking confirmation email"""
        logger.info("=" * 58)
        logger.info("SENDING BOOKING CONFIRMATION EMAIL")
        logger.info("=" * 58)
        logger.info(f"To: {email}")
        logger.info(f"Subject: Booking Confirmed - {booking_reference}")
        logger.info("")
        logger.info("Dear Customer,")
        logger.info("")
        logger.info("Your booking has been confirmed!")
        logger.info("")
        logger.info(f"Booking Reference: {booking_reference}")
        logger.info(f"Movie: {movie_title}")
        logger.info(f"Theater: {theater_name}")
        logger.info(f"Show Time: {self._format_datetime(show_date_time)}")
        logger.info(f"Seats: {self._format_seats(seats)}")
        logger.info(f"Total Amount: Rs. {self._format_amount(total_amount)}")
        logger.info("")
        logger.info("Please arrive 15 minutes before the show time.")
        logger.info("Show this email or your booking reference at the counter.")
        logger.info("")
        logger.info("Thank you for choosing BookMyShow!")
        logger.info("=" * 58)

    async def send_booking_cancellation_email(
        self,
        email: str,
        booking_reference: str,
        movie_title: str,
        theater_name: str,
        show_date_time: datetime,
        seats: List[str],
        refund_amount: Decimal,
    ) -> None:
        """Send booking cancellation email"""
        logger.info("=" * 58)
        logger.info("SENDING BOOKING CANCELLATION EMAIL")
        logger.info("=" * 58)
        logger.info(f"To: {email}")
        logger.info(f"Subject: Booking Cancelled - {booking_reference}")
        logger.info("")
        logger.info("Dear Customer,")
        logger.info("")
        logger.info("Your booking has been cancelled.")
        logger.info("")
        logger.info(f"Booking Reference: {booking_reference}")
        logger.info(f"Movie: {movie_title}")
        logger.info(f"Theater: {theater_name}")
        logger.info(f"Show Time: {self._format_datetime(show_date_time)}")
        logger.info(f"Seats: {self._format_seats(seats)}")
        logger.info(f"Refund Amount: Rs. {self._format_amount(refund_amount)}")
        logger.info("")
        logger.info("The refund will be processed within 5-7 business days.")
        logger.info("")
        logger.info("We hope to serve you again soon!")
        logger.info("=" * 58)

    async def send_payment_receipt_email(
        self,
        email: str,
        payment_reference: str,
        amount: Decimal,
        currency: str,
        payment_method: str,
    ) -> None:
        """Send payment receipt email"""
        logger.info("=" * 58)
        logger.info("SENDING PAYMENT RECEIPT EMAIL")
        logger.info("=" * 58)
        logger.info(f"To: {email}")
        logger.info(f"Subject: Payment Receipt - {payment_reference}")
        logger.info("")
        logger.info("Dear Customer,")
        logger.info("")
        logger.info("We have received your payment successfully.")
        logger.info("")
        logger.info(f"Payment Reference: {payment_reference}")
        logger.info(f"Amount: {self._format_amount(amount)} {currency}")
        logger.info(f"Payment Method: {payment_method}")
        logger.info(f"Transaction Date: {self._format_datetime(datetime.now())}")
        logger.info("")
        logger.info("This is your official payment receipt.")
        logger.info("Please keep it for your records.")
        logger.info("")
        logger.info("Thank you for your payment!")
        logger.info("=" * 58)

    async def send_payment_failure_email(
        self,
        email: str,
        payment_reference: str,
        amount: Decimal,
        failure_reason: str,
    ) -> None:
        """Send payment failure email"""
        logger.info("=" * 58)
        logger.info("SENDING PAYMENT FAILURE EMAIL")
        logger.info("=" * 58)
        logger.info(f"To: {email}")
        logger.info(f"Subject: Payment Failed - {payment_reference}")
        logger.info("")
        logger.info("Dear Customer,")
        logger.info("")
        logger.info("Unfortunately, your payment could not be processed.")
        logger.info("")
        logger.info(f"Payment Reference: {payment_reference}")
        logger.info(f"Amount: Rs. {self._format_amount(amount)}")
        logger.info(f"Failure Reason: {failure_reason}")
        logger.info("")
        logger.info("Please try again with a different payment method or contact your bank.")
        logger.info("Your booking is still on hold and will expire in 15 minutes.")
        logger.info("")
        logger.info("For assistance, please contact our support team.")
        logger.info("=" * 58)

    def _format_seats(self, seats: List[str]) -> str:
        """Format seat list"""
        if not seats:
            return ""
        return ", ".join(seats)

    def _format_amount(self, amount: Decimal) -> str:
        """Format amount"""
        if amount is None:
            return "0.00"
        return str(amount)

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime"""
        if dt is None:
            return ""
        return dt.strftime(self.DATE_TIME_FORMAT)
