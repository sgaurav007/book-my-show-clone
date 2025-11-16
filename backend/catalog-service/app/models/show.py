from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    screen_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("screens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    base_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    movie: Mapped["Movie"] = relationship("Movie", lazy="joined")
    screen: Mapped["Screen"] = relationship("Screen", lazy="joined")
