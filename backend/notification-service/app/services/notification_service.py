"""Notification Service"""
import logging
from typing import Optional
from datetime import datetime

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification business logic"""

    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def create_notification(
        self,
        user_id: int,
        notification_type: str,
        channel: str,
        recipient: str,
        subject: str,
        content: str,
        status: str,
        metadata: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            channel=channel,
            recipient=recipient,
            subject=subject,
            content=content,
            status=status,
            metadata=metadata,
            error_message=error_message,
        )

        logger.info(
            f"Creating notification for user {user_id}: "
            f"type={notification_type}, channel={channel}, status={status}"
        )

        return await self.repository.create(notification)

    async def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        logger.debug(f"Fetching notification {notification_id}")
        return await self.repository.get_by_id(notification_id)

    async def get_user_notifications(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> tuple[list[Notification], int, int]:
        """Get paginated notifications for a user"""
        logger.debug(f"Fetching notifications for user {user_id}")
        skip = (page - 1) * page_size
        notifications, total = await self.repository.get_by_user_id(
            user_id, skip=skip, limit=page_size
        )
        total_pages = (total + page_size - 1) // page_size
        return notifications, total, total_pages

    async def get_user_notifications_by_type(
        self, user_id: int, notification_type: str
    ) -> list[Notification]:
        """Get notifications for a user by type"""
        logger.debug(f"Fetching {notification_type} notifications for user {user_id}")
        return await self.repository.get_by_user_and_type(user_id, notification_type)

    async def get_user_notifications_by_status(
        self, user_id: int, status: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Notification], int, int]:
        """Get paginated notifications for a user by status"""
        logger.debug(f"Fetching {status} notifications for user {user_id}")
        skip = (page - 1) * page_size
        notifications, total = await self.repository.get_by_user_and_status(
            user_id, status, skip=skip, limit=page_size
        )
        total_pages = (total + page_size - 1) // page_size
        return notifications, total, total_pages

    async def get_notifications_by_status(self, status: str) -> list[Notification]:
        """Get all notifications with a specific status"""
        logger.debug(f"Fetching all {status} notifications")
        return await self.repository.get_by_status(status)

    async def get_notifications_by_date_range(
        self, start: datetime, end: datetime
    ) -> list[Notification]:
        """Get notifications within a date range"""
        logger.debug(f"Fetching notifications between {start} and {end}")
        return await self.repository.get_by_date_range(start, end)

    async def count_user_notifications_by_status(self, user_id: int, status: str) -> int:
        """Count notifications for a user with a specific status"""
        logger.debug(f"Counting {status} notifications for user {user_id}")
        return await self.repository.count_by_user_and_status(user_id, status)

    async def mark_as_success(self, notification: Notification) -> Notification:
        """Mark notification as successful"""
        logger.info(f"Marking notification {notification.id} as SUCCESS")
        notification.status = "SUCCESS"
        return await self.repository.update(notification)

    async def mark_as_failed(
        self, notification: Notification, error_message: str
    ) -> Notification:
        """Mark notification as failed"""
        logger.warning(
            f"Marking notification {notification.id} as FAILED: {error_message}"
        )
        notification.status = "FAILED"
        notification.error_message = error_message
        return await self.repository.update(notification)
