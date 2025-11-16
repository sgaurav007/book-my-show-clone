from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TheaterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CreateTheaterRequest(TheaterBase):
    pass


class TheaterResponse(TheaterBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
