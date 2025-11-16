from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.refund import RefundStatus


class RefundRequest(BaseModel):
    payment_id: int = Field(..., description="Payment ID to refund")
    refund_amount: Decimal = Field(..., gt=0, description="Amount to refund")
    reason: Optional[str] = Field(None, description="Reason for refund")

    model_config = ConfigDict(from_attributes=True)


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    refund_amount: Decimal
    refund_status: RefundStatus
    refund_reference: Optional[str] = None
    gateway_refund_id: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
