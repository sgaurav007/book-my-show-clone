"""Tests for Email Service"""
import pytest
from datetime import datetime
from decimal import Decimal

from app.services.email_service import EmailService


@pytest.mark.asyncio
async def test_send_booking_confirmation_email():
    """Test sending booking confirmation email"""
    service = EmailService()

    # This should not raise an exception
    await service.send_booking_confirmation_email(
        email="test@example.com",
        booking_reference="BKG123",
        movie_title="Test Movie",
        theater_name="Test Theater",
        show_date_time=datetime(2024, 12, 25, 18, 30),
        seats=["A1", "A2"],
        total_amount=Decimal("500.00"),
    )


@pytest.mark.asyncio
async def test_send_booking_cancellation_email():
    """Test sending booking cancellation email"""
    service = EmailService()

    # This should not raise an exception
    await service.send_booking_cancellation_email(
        email="test@example.com",
        booking_reference="BKG123",
        movie_title="Test Movie",
        theater_name="Test Theater",
        show_date_time=datetime(2024, 12, 25, 18, 30),
        seats=["A1", "A2"],
        refund_amount=Decimal("500.00"),
    )


@pytest.mark.asyncio
async def test_send_payment_receipt_email():
    """Test sending payment receipt email"""
    service = EmailService()

    # This should not raise an exception
    await service.send_payment_receipt_email(
        email="test@example.com",
        payment_reference="PAY123",
        amount=Decimal("500.00"),
        currency="INR",
        payment_method="Credit Card",
    )


@pytest.mark.asyncio
async def test_send_payment_failure_email():
    """Test sending payment failure email"""
    service = EmailService()

    # This should not raise an exception
    await service.send_payment_failure_email(
        email="test@example.com",
        payment_reference="PAY123",
        amount=Decimal("500.00"),
        failure_reason="Insufficient funds",
    )


def test_format_seats():
    """Test seat formatting"""
    service = EmailService()

    # Test with seats
    assert service._format_seats(["A1", "A2", "B3"]) == "A1, A2, B3"

    # Test with empty list
    assert service._format_seats([]) == ""

    # Test with single seat
    assert service._format_seats(["A1"]) == "A1"


def test_format_amount():
    """Test amount formatting"""
    service = EmailService()

    # Test with amount
    assert service._format_amount(Decimal("500.00")) == "500.00"

    # Test with None
    assert service._format_amount(None) == "0.00"


def test_format_datetime():
    """Test datetime formatting"""
    service = EmailService()

    # Test with datetime
    dt = datetime(2024, 12, 25, 18, 30)
    formatted = service._format_datetime(dt)
    assert "25 Dec 2024" in formatted
    assert "06:30 PM" in formatted

    # Test with None
    assert service._format_datetime(None) == ""
