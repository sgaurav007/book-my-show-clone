from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MovieGenre(Base):
    __tablename__ = "movie_genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    __table_args__ = (
        Index("idx_movie_genres_movie_id", "movie_id"),
        Index("idx_movie_genres_genre", "genre"),
    )
