"""Notification Repository"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Repository for notification operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user with pagination"""
        # Get total count
        count_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_by_user_and_type(
        self, user_id: int, notification_type: str
    ) -> List[Notification]:
        """Get notifications by user ID and type"""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_status(
        self, user_id: int, status: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[Notification], int]:
        """Get notifications by user ID and status with pagination"""
        # Get total count
        count_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.status == status)
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = (
            select(Notification)
            .where(and_(Notification.user_id == user_id, Notification.status == status))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_by_status(self, status: str) -> List[Notification]:
        """Get all notifications with a specific status"""
        query = select(Notification).where(Notification.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[Notification]:
        """Get notifications within a date range"""
        query = select(Notification).where(
            and_(
                Notification.created_at >= start,
                Notification.created_at <= end,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_user_and_status(self, user_id: int, status: str) -> int:
        """Count notifications for a user with a specific status"""
        query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.status == status)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(self, notification: Notification) -> Notification:
        """Update notification"""
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def delete_by_user_id(self, user_id: int) -> int:
        """Delete all notifications for a user"""
        query = select(Notification).where(Notification.user_id == user_id)
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        count = len(notifications)

        for notification in notifications:
            await self.session.delete(notification)

        await self.session.commit()
        return count
