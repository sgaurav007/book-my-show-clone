from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    BigInteger,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.database import Base


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    seat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    seat_number: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="seats"
    )

    __table_args__ = (
        Index('idx_booking_id', 'booking_id'),
        Index('idx_seat_id', 'seat_id'),
        UniqueConstraint('booking_id', 'seat_id', name='idx_booking_seat_unique'),
    )
