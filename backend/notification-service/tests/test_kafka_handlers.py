"""Tests for Kafka Event Handlers"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.events.booking_event_handler import BookingEventHandler
from app.events.payment_event_handler import PaymentEventHandler
from app.services.email_service import EmailService
from app.services.sms_service import SmsService
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository


@pytest.fixture
def booking_handler(db_session):
    """Create booking event handler"""
    repository = NotificationRepository(db_session)
    notification_service = NotificationService(repository)
    email_service = EmailService()
    sms_service = SmsService()

    return BookingEventHandler(email_service, sms_service, notification_service)


@pytest.fixture
def payment_handler(db_session):
    """Create payment event handler"""
    repository = NotificationRepository(db_session)
    notification_service = NotificationService(repository)
    email_service = EmailService()
    sms_service = SmsService()

    return PaymentEventHandler(email_service, sms_service, notification_service)


@pytest.mark.asyncio
async def test_handle_booking_confirmed(booking_handler, db_session):
    """Test handling booking confirmed event"""
    event_data = {
        "eventId": "evt_123",
        "eventType": "booking.confirmed",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "bookingId": 1,
            "bookingReference": "BKG123",
            "userId": 1,
            "userEmail": "test@example.com",
            "userPhone": "+1234567890",
            "showId": 1,
            "movieTitle": "Test Movie",
            "theaterName": "Test Theater",
            "showDateTime": datetime(2024, 12, 25, 18, 30).isoformat(),
            "seats": ["A1", "A2"],
            "totalAmount": "500.00",
            "paymentId": 1,
        },
    }

    # Handle event
    await booking_handler.handle_booking_confirmed(event_data)

    # Verify notifications were created
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    # Should have 2 notifications (EMAIL and SMS)
    assert total == 2

    # Check email notification
    email_notification = [n for n in notifications_list if n.channel == "EMAIL"][0]
    assert email_notification.notification_type == "BOOKING_CONFIRMED"
    assert email_notification.recipient == "test@example.com"
    assert email_notification.status == "SUCCESS"

    # Check SMS notification
    sms_notification = [n for n in notifications_list if n.channel == "SMS"][0]
    assert sms_notification.notification_type == "BOOKING_CONFIRMED"
    assert sms_notification.recipient == "+1234567890"
    assert sms_notification.status == "SUCCESS"


@pytest.mark.asyncio
async def test_handle_booking_cancelled(booking_handler, db_session):
    """Test handling booking cancelled event"""
    event_data = {
        "eventId": "evt_124",
        "eventType": "booking.cancelled",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "bookingId": 1,
            "bookingReference": "BKG123",
            "userId": 1,
            "userEmail": "test@example.com",
            "userPhone": "+1234567890",
            "movieTitle": "Test Movie",
            "theaterName": "Test Theater",
            "showDateTime": datetime(2024, 12, 25, 18, 30).isoformat(),
            "seats": ["A1", "A2"],
            "refundAmount": "500.00",
            "cancellationReason": "User request",
        },
    }

    # Handle event
    await booking_handler.handle_booking_cancelled(event_data)

    # Verify notifications were created
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    # Should have 2 notifications (EMAIL and SMS)
    assert total == 2

    # Check notifications are for cancellation
    for notification in notifications_list:
        assert notification.notification_type == "BOOKING_CANCELLED"
        assert notification.status == "SUCCESS"


@pytest.mark.asyncio
async def test_handle_payment_success(payment_handler, db_session):
    """Test handling payment success event"""
    event_data = {
        "eventId": "evt_125",
        "eventType": "payment.success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "paymentId": 1,
            "paymentReference": "PAY123",
            "bookingId": 1,
            "userId": 1,
            "userEmail": "test@example.com",
            "userPhone": "+1234567890",
            "amount": "500.00",
            "currency": "INR",
            "paymentMethod": "Credit Card",
            "gatewayTransactionId": "GTX123",
        },
    }

    # Handle event
    await payment_handler.handle_payment_success(event_data)

    # Verify notifications were created
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    # Should have 2 notifications (EMAIL and SMS)
    assert total == 2

    # Check notifications are for payment success
    for notification in notifications_list:
        assert notification.notification_type == "PAYMENT_SUCCESS"
        assert notification.status == "SUCCESS"


@pytest.mark.asyncio
async def test_handle_payment_failed(payment_handler, db_session):
    """Test handling payment failed event"""
    event_data = {
        "eventId": "evt_126",
        "eventType": "payment.failed",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "paymentId": 1,
            "paymentReference": "PAY123",
            "bookingId": 1,
            "userId": 1,
            "userEmail": "test@example.com",
            "userPhone": "+1234567890",
            "amount": "500.00",
            "currency": "INR",
            "paymentMethod": "Credit Card",
            "failureReason": "Insufficient funds",
            "errorCode": "ERR_001",
        },
    }

    # Handle event
    await payment_handler.handle_payment_failed(event_data)

    # Verify notifications were created
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    # Should have 2 notifications (EMAIL and SMS)
    assert total == 2

    # Check notifications are for payment failure
    for notification in notifications_list:
        assert notification.notification_type == "PAYMENT_FAILED"
        assert notification.status == "SUCCESS"


@pytest.mark.asyncio
async def test_handle_invalid_event_format(booking_handler, db_session):
    """Test handling invalid event format"""
    event_data = {
        "eventId": "evt_127",
        "eventType": "booking.confirmed",
        # Missing required fields
    }

    # Should not raise an exception, just log error
    await booking_handler.handle_booking_confirmed(event_data)

    # No notifications should be created
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    assert total == 0


@pytest.mark.asyncio
async def test_email_failure_recorded(booking_handler, db_session):
    """Test that email failures are recorded"""
    # Mock email service to raise exception
    booking_handler.email_service.send_booking_confirmation_email = AsyncMock(
        side_effect=Exception("SMTP error")
    )

    event_data = {
        "eventId": "evt_128",
        "eventType": "booking.confirmed",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "bookingId": 1,
            "bookingReference": "BKG123",
            "userId": 1,
            "userEmail": "test@example.com",
            "userPhone": "+1234567890",
            "showId": 1,
            "movieTitle": "Test Movie",
            "theaterName": "Test Theater",
            "showDateTime": datetime(2024, 12, 25, 18, 30).isoformat(),
            "seats": ["A1", "A2"],
            "totalAmount": "500.00",
            "paymentId": 1,
        },
    }

    # Handle event
    await booking_handler.handle_booking_confirmed(event_data)

    # Verify failed notification was recorded
    repository = NotificationRepository(db_session)
    notifications = await repository.get_by_user_id(1, skip=0, limit=10)
    notifications_list, total = notifications

    # Should have 2 notifications (EMAIL failed, SMS success)
    assert total == 2

    # Check email notification is marked as failed
    email_notification = [n for n in notifications_list if n.channel == "EMAIL"][0]
    assert email_notification.status == "FAILED"
    assert "SMTP error" in email_notification.error_message
