from typing import List, Optional

from app.models import Seat
from app.repositories import SeatRepository


class SeatService:
    def __init__(self, repository: SeatRepository):
        self.repository = repository

    async def get_seat_by_id(self, seat_id: int) -> Optional[Seat]:
        return await self.repository.get_by_id(seat_id)

    async def get_seats_by_screen(self, screen_id: int) -> List[Seat]:
        return await self.repository.get_by_screen_id(screen_id)
