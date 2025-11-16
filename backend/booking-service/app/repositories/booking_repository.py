from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.booking import Booking, BookingStatus


class BookingRepository:
    """Repository for Booking entity operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, booking: Booking) -> Booking:
        """Create a new booking"""
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        result = await self.session.execute(
            select(Booking)
            .options(selectinload(Booking.seats))
            .where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_by_reference(self, booking_reference: str) -> Optional[Booking]:
        """Get booking by reference"""
        result = await self.session.execute(
            select(Booking)
            .options(selectinload(Booking.seats))
            .where(Booking.booking_reference == booking_reference)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> List[Booking]:
        """Get all bookings for a user"""
        result = await self.session.execute(
            select(Booking)
            .options(selectinload(Booking.seats))
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user_id_and_status(
        self, user_id: int, status: BookingStatus
    ) -> List[Booking]:
        """Get bookings by user ID and status"""
        result = await self.session.execute(
            select(Booking)
            .options(selectinload(Booking.seats))
            .where(Booking.user_id == user_id, Booking.booking_status == status)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_show_id(self, show_id: int) -> List[Booking]:
        """Get all bookings for a show"""
        result = await self.session.execute(
            select(Booking)
            .options(selectinload(Booking.seats))
            .where(Booking.show_id == show_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, booking: Booking) -> Booking:
        """Update booking"""
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def save(self, booking: Booking) -> Booking:
        """Save or update booking"""
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking
