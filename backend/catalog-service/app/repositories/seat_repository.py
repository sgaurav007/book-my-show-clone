from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Seat


class SeatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, seat_id: int) -> Optional[Seat]:
        result = await self.db.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def get_by_screen_id(self, screen_id: int) -> List[Seat]:
        result = await self.db.execute(
            select(Seat)
            .where(Seat.screen_id == screen_id)
            .order_by(Seat.row_label, Seat.seat_number)
        )
        return list(result.scalars().all())
