"""Notification Pydantic schemas"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Notification Response Schemas
class NotificationResponse(BaseModel):
    """Notification response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_type: str
    channel: str
    recipient: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    status: str
    metadata: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated notification list response"""

    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Kafka Event Schemas
class BookingData(BaseModel):
    """Booking data in event"""

    booking_id: int = Field(alias="bookingId")
    booking_reference: str = Field(alias="bookingReference")
    user_id: int = Field(alias="userId")
    user_email: str = Field(alias="userEmail")
    user_phone: str = Field(alias="userPhone")
    show_id: int = Field(alias="showId")
    movie_title: str = Field(alias="movieTitle")
    theater_name: str = Field(alias="theaterName")
    show_date_time: datetime = Field(alias="showDateTime")
    seats: List[str]
    total_amount: Decimal = Field(alias="totalAmount")
    payment_id: Optional[int] = Field(None, alias="paymentId")

    model_config = ConfigDict(populate_by_name=True)


class BookingConfirmedEvent(BaseModel):
    """Booking confirmed Kafka event"""

    event_id: str = Field(alias="eventId")
    event_type: str = Field(alias="eventType")
    timestamp: datetime
    data: BookingData

    model_config = ConfigDict(populate_by_name=True)


class BookingCancellationData(BaseModel):
    """Booking cancellation data in event"""

    booking_id: int = Field(alias="bookingId")
    booking_reference: str = Field(alias="bookingReference")
    user_id: int = Field(alias="userId")
    user_email: str = Field(alias="userEmail")
    user_phone: str = Field(alias="userPhone")
    movie_title: str = Field(alias="movieTitle")
    theater_name: str = Field(alias="theaterName")
    show_date_time: datetime = Field(alias="showDateTime")
    seats: List[str]
    refund_amount: Decimal = Field(alias="refundAmount")
    cancellation_reason: Optional[str] = Field(None, alias="cancellationReason")

    model_config = ConfigDict(populate_by_name=True)


class BookingCancelledEvent(BaseModel):
    """Booking cancelled Kafka event"""

    event_id: str = Field(alias="eventId")
    event_type: str = Field(alias="eventType")
    timestamp: datetime
    data: BookingCancellationData

    model_config = ConfigDict(populate_by_name=True)


class PaymentData(BaseModel):
    """Payment data in event"""

    payment_id: int = Field(alias="paymentId")
    payment_reference: str = Field(alias="paymentReference")
    booking_id: int = Field(alias="bookingId")
    user_id: int = Field(alias="userId")
    user_email: str = Field(alias="userEmail")
    user_phone: str = Field(alias="userPhone")
    amount: Decimal
    currency: str
    payment_method: str = Field(alias="paymentMethod")
    gateway_transaction_id: Optional[str] = Field(None, alias="gatewayTransactionId")

    model_config = ConfigDict(populate_by_name=True)


class PaymentSuccessEvent(BaseModel):
    """Payment success Kafka event"""

    event_id: str = Field(alias="eventId")
    event_type: str = Field(alias="eventType")
    timestamp: datetime
    data: PaymentData

    model_config = ConfigDict(populate_by_name=True)


class PaymentFailureData(BaseModel):
    """Payment failure data in event"""

    payment_id: int = Field(alias="paymentId")
    payment_reference: str = Field(alias="paymentReference")
    booking_id: int = Field(alias="bookingId")
    user_id: int = Field(alias="userId")
    user_email: str = Field(alias="userEmail")
    user_phone: str = Field(alias="userPhone")
    amount: Decimal
    currency: str
    payment_method: str = Field(alias="paymentMethod")
    failure_reason: str = Field(alias="failureReason")
    error_code: Optional[str] = Field(None, alias="errorCode")

    model_config = ConfigDict(populate_by_name=True)


class PaymentFailedEvent(BaseModel):
    """Payment failed Kafka event"""

    event_id: str = Field(alias="eventId")
    event_type: str = Field(alias="eventType")
    timestamp: datetime
    data: PaymentFailureData

    model_config = ConfigDict(populate_by_name=True)
