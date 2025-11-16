from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ScreenBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    total_seats: int = Field(..., gt=0)
    theater_id: int


class ScreenResponse(ScreenBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
