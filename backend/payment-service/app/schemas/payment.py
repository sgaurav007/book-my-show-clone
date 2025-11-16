from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.payment import PaymentStatus, PaymentMethod


class PaymentRequest(BaseModel):
    booking_id: int = Field(..., description="Booking ID")
    user_id: int = Field(..., description="User ID")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    gateway_name: str = Field(default="MOCK_GATEWAY", description="Payment gateway name")

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    id: int
    payment_reference: str
    booking_id: int
    user_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    gateway_transaction_id: Optional[str] = None
    payment_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookRequest(BaseModel):
    payment_reference: str
    gateway_transaction_id: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GatewayResponse(BaseModel):
    transaction_id: Optional[str] = None
    payment_url: Optional[str] = None
    success: bool
    message: str

    model_config = ConfigDict(from_attributes=True)
