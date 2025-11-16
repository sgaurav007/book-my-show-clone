from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    String,
    Numeric,
    DateTime,
    Index,
    Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.database import Base


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    booking_reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    show_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    booking_status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, name="booking_status_enum", create_constraint=True),
        nullable=False,
        index=True
    )
    payment_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    seats: Mapped[List["BookingSeat"]] = relationship(
        "BookingSeat",
        back_populates="booking",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        Index('idx_booking_reference', 'booking_reference'),
        Index('idx_user_id', 'user_id'),
        Index('idx_show_id', 'show_id'),
        Index('idx_booking_status', 'booking_status'),
        Index('idx_expires_at', 'expires_at'),
    )
