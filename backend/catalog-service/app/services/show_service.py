from typing import List, Optional
from datetime import date

from app.models import Show
from app.repositories import ShowRepository, MovieRepository, SeatRepository
from app.schemas import CreateShowRequest


class ShowService:
    def __init__(
        self,
        repository: ShowRepository,
        movie_repository: MovieRepository,
        seat_repository: SeatRepository,
    ):
        self.repository = repository
        self.movie_repository = movie_repository
        self.seat_repository = seat_repository

    async def create_show(self, request: CreateShowRequest) -> Show:
        # Verify movie exists
        movie = await self.movie_repository.get_by_id(request.movie_id)
        if not movie:
            raise ValueError(f"Movie with id {request.movie_id} not found")
        
        show = Show(
            movie_id=request.movie_id,
            screen_id=request.screen_id,
            start_time=request.start_time,
            end_time=request.end_time,
            base_price=request.base_price,
        )
        
        return await self.repository.create(show)

    async def get_show_by_id(self, show_id: int) -> Optional[Show]:
        return await self.repository.get_by_id(show_id)

    async def get_shows_by_movie(self, movie_id: int) -> List[Show]:
        return await self.repository.get_by_movie_id(movie_id)

    async def get_shows_by_movie_and_city(self, movie_id: int, city: str) -> List[Show]:
        return await self.repository.get_by_movie_and_city(movie_id, city)

    async def get_shows_by_date(self, show_date: date) -> List[Show]:
        return await self.repository.get_by_date(show_date)

    async def get_shows_by_movie_city_and_date(
        self, movie_id: int, city: str, show_date: date
    ) -> List[Show]:
        return await self.repository.get_by_movie_city_and_date(movie_id, city, show_date)

    async def delete_show(self, show_id: int) -> None:
        show = await self.repository.get_by_id(show_id)
        if not show:
            raise ValueError(f"Show with id {show_id} not found")
        
        await self.repository.delete(show)
