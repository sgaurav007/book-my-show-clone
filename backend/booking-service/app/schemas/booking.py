from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.booking import BookingStatus
from app.schemas.seat import SeatInfo, SeatResponse


class LockSeatsRequest(BaseModel):
    """Schema for lock seats request"""
    user_id: int = Field(..., description="User ID")
    show_id: int = Field(..., description="Show ID")
    seats: List[SeatInfo] = Field(..., min_length=1, description="List of seats to book")

    model_config = ConfigDict(from_attributes=True)


class ConfirmBookingRequest(BaseModel):
    """Schema for confirm booking request"""
    payment_id: int = Field(..., description="Payment ID")

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: int
    booking_reference: str
    user_id: int
    show_id: int
    total_amount: Decimal
    booking_status: BookingStatus
    payment_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    seats: List[SeatResponse]

    model_config = ConfigDict(from_attributes=True)


class BookingCreateEvent(BaseModel):
    """Schema for booking created event"""
    booking_id: int
    booking_reference: str
    user_id: int
    show_id: int
    total_amount: Decimal
    seat_ids: List[int]
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class BookingConfirmedEvent(BaseModel):
    """Schema for booking confirmed event"""
    booking_id: int
    booking_reference: str
    user_id: int
    show_id: int
    payment_id: int
    total_amount: Decimal
    confirmed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingCancelledEvent(BaseModel):
    """Schema for booking cancelled event"""
    booking_id: int
    booking_reference: str
    user_id: int
    show_id: int
    seat_ids: List[int]
    reason: str
    cancelled_at: datetime

    model_config = ConfigDict(from_attributes=True)
