from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from .movie import MovieResponse
from .screen import ScreenResponse


class ShowBase(BaseModel):
    movie_id: int
    screen_id: int
    start_time: datetime
    end_time: datetime
    base_price: Decimal = Field(..., ge=0, decimal_places=2)


class CreateShowRequest(ShowBase):
    pass


class ShowResponse(BaseModel):
    id: int
    movie_id: int
    screen_id: int
    start_time: datetime
    end_time: datetime
    base_price: Decimal
    created_at: datetime
    updated_at: datetime
    movie: Optional[MovieResponse] = None
    screen: Optional[ScreenResponse] = None

    model_config = ConfigDict(from_attributes=True)
