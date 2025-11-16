from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class SeatInfo(BaseModel):
    """Schema for seat information in booking request"""
    seat_id: int = Field(..., description="Seat ID")
    seat_number: str = Field(..., description="Seat number")
    price: Decimal = Field(..., description="Seat price", ge=0)

    model_config = ConfigDict(from_attributes=True)


class SeatResponse(BaseModel):
    """Schema for seat information in responses"""
    seat_id: int
    seat_number: str
    price: Decimal

    model_config = ConfigDict(from_attributes=True)
