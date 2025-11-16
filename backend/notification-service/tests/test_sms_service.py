"""Tests for SMS Service"""
import pytest
from datetime import datetime
from decimal import Decimal

from app.services.sms_service import SmsService


@pytest.mark.asyncio
async def test_send_booking_confirmation_sms():
    """Test sending booking confirmation SMS"""
    service = SmsService()

    # This should not raise an exception
    await service.send_booking_confirmation_sms(
        phone_number="+1234567890",
        booking_reference="BKG123",
        movie_title="Test Movie",
        show_date_time=datetime(2024, 12, 25, 18, 30),
    )


@pytest.mark.asyncio
async def test_send_booking_cancellation_sms():
    """Test sending booking cancellation SMS"""
    service = SmsService()

    # This should not raise an exception
    await service.send_booking_cancellation_sms(
        phone_number="+1234567890",
        booking_reference="BKG123",
        movie_title="Test Movie",
        refund_amount=Decimal("500.00"),
    )


@pytest.mark.asyncio
async def test_send_payment_success_sms():
    """Test sending payment success SMS"""
    service = SmsService()

    # This should not raise an exception
    await service.send_payment_success_sms(
        phone_number="+1234567890",
        payment_reference="PAY123",
        amount=Decimal("500.00"),
    )


@pytest.mark.asyncio
async def test_send_payment_failure_sms():
    """Test sending payment failure SMS"""
    service = SmsService()

    # This should not raise an exception
    await service.send_payment_failure_sms(
        phone_number="+1234567890",
        payment_reference="PAY123",
        amount=Decimal("500.00"),
        failure_reason="Insufficient funds",
    )


def test_truncate_sms():
    """Test SMS truncation"""
    service = SmsService()

    # Test short message
    short_message = "Short message"
    assert service._truncate_sms(short_message) == short_message

    # Test long message
    long_message = "A" * 200
    truncated = service._truncate_sms(long_message)
    assert len(truncated) == 160
    assert truncated.endswith("...")

    # Test empty message
    assert service._truncate_sms("") == ""

    # Test None
    assert service._truncate_sms(None) == ""


def test_format_phone_number():
    """Test phone number formatting"""
    service = SmsService()

    # Test full phone number
    formatted = service._format_phone_number("+1234567890")
    assert formatted == "******7890"

    # Test short phone number
    assert service._format_phone_number("123") == "123"

    # Test empty phone number
    assert service._format_phone_number("") == ""

    # Test None
    assert service._format_phone_number(None) == ""


def test_format_datetime():
    """Test datetime formatting"""
    service = SmsService()

    # Test with datetime
    dt = datetime(2024, 12, 25, 18, 30)
    formatted = service._format_datetime(dt)
    assert "25 Dec" in formatted
    assert "06:30 PM" in formatted

    # Test with None
    assert service._format_datetime(None) == ""
