"""Tests for Notification Service"""
import pytest
from datetime import datetime

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_create_notification(db_session):
    """Test creating a notification"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    notification = await service.create_notification(
        user_id=1,
        notification_type="BOOKING_CONFIRMED",
        channel="EMAIL",
        recipient="test@example.com",
        subject="Booking Confirmed",
        content="Your booking has been confirmed",
        status="SUCCESS",
        metadata='{"bookingId": 123}',
    )

    assert notification.id is not None
    assert notification.user_id == 1
    assert notification.notification_type == "BOOKING_CONFIRMED"
    assert notification.channel == "EMAIL"
    assert notification.recipient == "test@example.com"
    assert notification.status == "SUCCESS"


@pytest.mark.asyncio
async def test_get_notification_by_id(db_session):
    """Test getting notification by ID"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    # Create notification
    created = await service.create_notification(
        user_id=1,
        notification_type="BOOKING_CONFIRMED",
        channel="EMAIL",
        recipient="test@example.com",
        subject="Test",
        content="Test content",
        status="SUCCESS",
    )

    # Get notification
    notification = await service.get_notification_by_id(created.id)

    assert notification is not None
    assert notification.id == created.id
    assert notification.user_id == 1


@pytest.mark.asyncio
async def test_get_user_notifications(db_session):
    """Test getting user notifications"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    # Create multiple notifications
    for i in range(5):
        await service.create_notification(
            user_id=1,
            notification_type="BOOKING_CONFIRMED",
            channel="EMAIL",
            recipient="test@example.com",
            subject=f"Test {i}",
            content=f"Test content {i}",
            status="SUCCESS",
        )

    # Get user notifications
    notifications, total, total_pages = await service.get_user_notifications(
        user_id=1, page=1, page_size=10
    )

    assert len(notifications) == 5
    assert total == 5
    assert total_pages == 1


@pytest.mark.asyncio
async def test_get_user_notifications_pagination(db_session):
    """Test pagination of user notifications"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    # Create 15 notifications
    for i in range(15):
        await service.create_notification(
            user_id=1,
            notification_type="BOOKING_CONFIRMED",
            channel="EMAIL",
            recipient="test@example.com",
            subject=f"Test {i}",
            content=f"Test content {i}",
            status="SUCCESS",
        )

    # Get first page
    notifications, total, total_pages = await service.get_user_notifications(
        user_id=1, page=1, page_size=10
    )

    assert len(notifications) == 10
    assert total == 15
    assert total_pages == 2

    # Get second page
    notifications, total, total_pages = await service.get_user_notifications(
        user_id=1, page=2, page_size=10
    )

    assert len(notifications) == 5
    assert total == 15
    assert total_pages == 2


@pytest.mark.asyncio
async def test_mark_as_failed(db_session):
    """Test marking notification as failed"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    # Create notification
    notification = await service.create_notification(
        user_id=1,
        notification_type="BOOKING_CONFIRMED",
        channel="EMAIL",
        recipient="test@example.com",
        subject="Test",
        content="Test content",
        status="PENDING",
    )

    # Mark as failed
    updated = await service.mark_as_failed(notification, "SMTP connection error")

    assert updated.status == "FAILED"
    assert updated.error_message == "SMTP connection error"


@pytest.mark.asyncio
async def test_count_user_notifications_by_status(db_session):
    """Test counting user notifications by status"""
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    # Create notifications with different statuses
    for i in range(3):
        await service.create_notification(
            user_id=1,
            notification_type="BOOKING_CONFIRMED",
            channel="EMAIL",
            recipient="test@example.com",
            subject=f"Test {i}",
            content=f"Test content {i}",
            status="SUCCESS",
        )

    for i in range(2):
        await service.create_notification(
            user_id=1,
            notification_type="BOOKING_CONFIRMED",
            channel="EMAIL",
            recipient="test@example.com",
            subject=f"Test {i}",
            content=f"Test content {i}",
            status="FAILED",
        )

    # Count successful notifications
    success_count = await service.count_user_notifications_by_status(1, "SUCCESS")
    assert success_count == 3

    # Count failed notifications
    failed_count = await service.count_user_notifications_by_status(1, "FAILED")
    assert failed_count == 2
