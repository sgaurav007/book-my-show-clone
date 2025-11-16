from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Movie, MovieGenre


class MovieRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, movie: Movie, genres: List[str] = None) -> Movie:
        self.db.add(movie)
        await self.db.flush()
        
        if genres:
            for genre in genres:
                movie_genre = MovieGenre(movie_id=movie.id, genre=genre)
                self.db.add(movie_genre)
        
        await self.db.commit()
        await self.db.refresh(movie)
        return movie

    async def get_by_id(self, movie_id: int) -> Optional[Movie]:
        result = await self.db.execute(select(Movie).where(Movie.id == movie_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 10) -> tuple[List[Movie], int]:
        # Get total count
        count_result = await self.db.execute(select(func.count(Movie.id)))
        total = count_result.scalar()
        
        # Get paginated results
        result = await self.db.execute(
            select(Movie).offset(skip).limit(limit).order_by(Movie.id.desc())
        )
        movies = list(result.scalars().all())
        return movies, total

    async def get_active_movies(self) -> List[Movie]:
        result = await self.db.execute(
            select(Movie).where(Movie.is_active == True).order_by(Movie.release_date.desc())
        )
        return list(result.scalars().all())

    async def search_by_title_or_genre(self, query: str) -> List[Movie]:
        # Search movies by title or genre
        genre_subquery = (
            select(MovieGenre.movie_id)
            .where(func.lower(MovieGenre.genre).like(f"%{query.lower()}%"))
        )
        
        result = await self.db.execute(
            select(Movie).where(
                or_(
                    func.lower(Movie.title).like(f"%{query.lower()}%"),
                    Movie.id.in_(genre_subquery)
                )
            ).order_by(Movie.title)
        )
        return list(result.scalars().all())

    async def update(self, movie: Movie) -> Movie:
        await self.db.commit()
        await self.db.refresh(movie)
        return movie

    async def delete(self, movie: Movie) -> None:
        await self.db.delete(movie)
        await self.db.commit()

    async def get_genres_by_movie_id(self, movie_id: int) -> List[str]:
        result = await self.db.execute(
            select(MovieGenre.genre).where(MovieGenre.movie_id == movie_id)
        )
        return [row for row in result.scalars().all()]

    async def update_genres(self, movie_id: int, genres: List[str]) -> None:
        # Delete existing genres
        await self.db.execute(
            select(MovieGenre).where(MovieGenre.movie_id == movie_id)
        )
        await self.db.execute(
            MovieGenre.__table__.delete().where(MovieGenre.movie_id == movie_id)
        )
        
        # Add new genres
        for genre in genres:
            movie_genre = MovieGenre(movie_id=movie_id, genre=genre)
            self.db.add(movie_genre)
        
        await self.db.commit()
