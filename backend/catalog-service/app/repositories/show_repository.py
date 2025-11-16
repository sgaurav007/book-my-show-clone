from typing import List, Optional
from datetime import date
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models import Show, Screen, Theater


class ShowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, show: Show) -> Show:
        self.db.add(show)
        await self.db.commit()
        await self.db.refresh(show)
        return show

    async def get_by_id(self, show_id: int) -> Optional[Show]:
        result = await self.db.execute(
            select(Show)
            .options(joinedload(Show.movie), joinedload(Show.screen))
            .where(Show.id == show_id)
        )
        return result.scalar_one_or_none()

    async def get_by_movie_id(self, movie_id: int) -> List[Show]:
        result = await self.db.execute(
            select(Show)
            .options(joinedload(Show.movie), joinedload(Show.screen))
            .where(Show.movie_id == movie_id)
            .order_by(Show.start_time)
        )
        return list(result.scalars().all())

    async def get_by_movie_and_city(self, movie_id: int, city: str) -> List[Show]:
        result = await self.db.execute(
            select(Show)
            .join(Show.screen)
            .join(Screen.theater)
            .options(joinedload(Show.movie), joinedload(Show.screen))
            .where(Show.movie_id == movie_id, Theater.city == city)
            .order_by(Show.start_time)
        )
        return list(result.scalars().all())

    async def get_by_date(self, show_date: date) -> List[Show]:
        result = await self.db.execute(
            select(Show)
            .options(joinedload(Show.movie), joinedload(Show.screen))
            .where(cast(Show.start_time, Date) == show_date)
            .order_by(Show.start_time)
        )
        return list(result.scalars().all())

    async def get_by_movie_city_and_date(
        self, movie_id: int, city: str, show_date: date
    ) -> List[Show]:
        result = await self.db.execute(
            select(Show)
            .join(Show.screen)
            .join(Screen.theater)
            .options(joinedload(Show.movie), joinedload(Show.screen))
            .where(
                Show.movie_id == movie_id,
                Theater.city == city,
                cast(Show.start_time, Date) == show_date
            )
            .order_by(Show.start_time)
        )
        return list(result.scalars().all())

    async def delete(self, show: Show) -> None:
        await self.db.delete(show)
        await self.db.commit()
