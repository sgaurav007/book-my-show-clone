from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.seat import SeatType


class SeatBase(BaseModel):
    row_label: str = Field(..., min_length=1, max_length=10)
    seat_number: int = Field(..., gt=0)
    seat_type: str
    screen_id: int


class SeatResponse(SeatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
