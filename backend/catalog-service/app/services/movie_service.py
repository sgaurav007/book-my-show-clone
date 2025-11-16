import json
from typing import List, Optional
from redis.asyncio import Redis

from app.models import Movie
from app.repositories import MovieRepository
from app.schemas import CreateMovieRequest, UpdateMovieRequest, MovieResponse


class MovieService:
    def __init__(self, repository: MovieRepository, redis: Optional[Redis] = None):
        self.repository = repository
        self.redis = redis
        self.cache_ttl = 300  # 5 minutes for list
        self.item_cache_ttl = 600  # 10 minutes for individual items

    async def create_movie(self, request: CreateMovieRequest) -> Movie:
        movie = Movie(
            title=request.title,
            description=request.description,
            duration_minutes=request.duration_minutes,
            language=request.language,
            release_date=request.release_date,
            rating=request.rating,
            poster_url=request.poster_url,
            trailer_url=request.trailer_url,
            is_active=True,
        )
        
        created_movie = await self.repository.create(movie, request.genre or [])
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete("movies:all")
        
        return created_movie

    async def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        cache_key = f"movie:{movie_id}"
        
        # Try to get from cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                movie_dict = json.loads(cached)
                # Fetch genres separately
                genres = await self.repository.get_genres_by_movie_id(movie_id)
                movie_dict['genre'] = genres
                return movie_dict
        
        # Get from database
        movie = await self.repository.get_by_id(movie_id)
        
        if movie and self.redis:
            # Get genres
            genres = await self.repository.get_genres_by_movie_id(movie_id)
            # Cache the result
            movie_dict = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "duration_minutes": movie.duration_minutes,
                "language": movie.language,
                "release_date": movie.release_date.isoformat(),
                "rating": movie.rating,
                "poster_url": movie.poster_url,
                "trailer_url": movie.trailer_url,
                "is_active": movie.is_active,
                "genre": genres,
            }
            await self.redis.setex(cache_key, self.item_cache_ttl, json.dumps(movie_dict))
        
        return movie

    async def get_all_movies(self, page: int = 0, size: int = 10) -> tuple[List[Movie], int]:
        skip = page * size
        movies, total = await self.repository.get_all(skip, size)
        return movies, total

    async def search_movies(self, query: str) -> List[Movie]:
        return await self.repository.search_by_title_or_genre(query)

    async def update_movie(self, movie_id: int, request: UpdateMovieRequest) -> Movie:
        movie = await self.repository.get_by_id(movie_id)
        if not movie:
            raise ValueError(f"Movie with id {movie_id} not found")
        
        # Update fields
        if request.title is not None:
            movie.title = request.title
        if request.description is not None:
            movie.description = request.description
        if request.duration_minutes is not None:
            movie.duration_minutes = request.duration_minutes
        if request.language is not None:
            movie.language = request.language
        if request.release_date is not None:
            movie.release_date = request.release_date
        if request.rating is not None:
            movie.rating = request.rating
        if request.poster_url is not None:
            movie.poster_url = request.poster_url
        if request.trailer_url is not None:
            movie.trailer_url = request.trailer_url
        if request.is_active is not None:
            movie.is_active = request.is_active
        
        if request.genre is not None:
            await self.repository.update_genres(movie_id, request.genre)
        
        updated_movie = await self.repository.update(movie)
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"movie:{movie_id}")
            await self.redis.delete("movies:all")
        
        return updated_movie

    async def delete_movie(self, movie_id: int) -> None:
        movie = await self.repository.get_by_id(movie_id)
        if not movie:
            raise ValueError(f"Movie with id {movie_id} not found")
        
        await self.repository.delete(movie)
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"movie:{movie_id}")
            await self.redis.delete("movies:all")

    async def get_movie_genres(self, movie_id: int) -> List[str]:
        return await self.repository.get_genres_by_movie_id(movie_id)
