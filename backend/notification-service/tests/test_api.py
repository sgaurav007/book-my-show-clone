"""Tests for API endpoints"""
import pytest
from httpx import AsyncClient

from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "notification-service"


@pytest.mark.asyncio
async def test_get_user_notifications(client: AsyncClient, db_session):
    """Test getting user notifications"""
    # Create test notifications
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

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

    # Get user notifications
    response = await client.get("/api/v1/notifications/user/1")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["notifications"]) == 3
    assert data["page"] == 1
    assert data["total_pages"] == 1


@pytest.mark.asyncio
async def test_get_user_notifications_with_pagination(client: AsyncClient, db_session):
    """Test getting user notifications with pagination"""
    # Create test notifications
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    for i in range(25):
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
    response = await client.get("/api/v1/notifications/user/1?page=1&page_size=10")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 25
    assert len(data["notifications"]) == 10
    assert data["page"] == 1
    assert data["total_pages"] == 3

    # Get second page
    response = await client.get("/api/v1/notifications/user/1?page=2&page_size=10")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 25
    assert len(data["notifications"]) == 10
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_get_notification_by_id(client: AsyncClient, db_session):
    """Test getting notification by ID"""
    # Create test notification
    repository = NotificationRepository(db_session)
    service = NotificationService(repository)

    notification = await service.create_notification(
        user_id=1,
        notification_type="BOOKING_CONFIRMED",
        channel="EMAIL",
        recipient="test@example.com",
        subject="Test",
        content="Test content",
        status="SUCCESS",
    )

    # Get notification by ID
    response = await client.get(f"/api/v1/notifications/{notification.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == notification.id
    assert data["user_id"] == 1
    assert data["notification_type"] == "BOOKING_CONFIRMED"
    assert data["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_get_notification_not_found(client: AsyncClient):
    """Test getting non-existent notification"""
    response = await client.get("/api/v1/notifications/9999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_notifications_empty(client: AsyncClient):
    """Test getting notifications for user with no notifications"""
    response = await client.get("/api/v1/notifications/user/999")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert len(data["notifications"]) == 0
