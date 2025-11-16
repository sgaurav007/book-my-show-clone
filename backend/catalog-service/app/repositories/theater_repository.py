from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Theater


class TheaterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, theater: Theater) -> Theater:
        self.db.add(theater)
        await self.db.commit()
        await self.db.refresh(theater)
        return theater

    async def get_by_id(self, theater_id: int) -> Optional[Theater]:
        result = await self.db.execute(
            select(Theater)
            .options(selectinload(Theater.screens))
            .where(Theater.id == theater_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Theater]:
        result = await self.db.execute(
            select(Theater).order_by(Theater.name)
        )
        return list(result.scalars().all())

    async def get_by_city(self, city: str) -> List[Theater]:
        result = await self.db.execute(
            select(Theater)
            .where(Theater.city == city, Theater.is_active == True)
            .order_by(Theater.name)
        )
        return list(result.scalars().all())

    async def get_all_cities(self) -> List[tuple[str, int]]:
        result = await self.db.execute(
            select(Theater.city, func.count(Theater.id).label('count'))
            .where(Theater.is_active == True)
            .group_by(Theater.city)
            .order_by(Theater.city)
        )
        return list(result.all())

    async def delete(self, theater: Theater) -> None:
        await self.db.delete(theater)
        await self.db.commit()
