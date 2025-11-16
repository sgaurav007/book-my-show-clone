import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RefundStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    payment_id = Column(BigInteger, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    refund_amount = Column(DECIMAL(10, 2), nullable=False)
    refund_status = Column(Enum(RefundStatus), nullable=False, index=True)
    refund_reference = Column(String(100), unique=True, nullable=True)
    gateway_refund_id = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
