import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Movie
from app.repositories import MovieRepository
from app.services import MovieService
from app.schemas import CreateMovieRequest, UpdateMovieRequest


@pytest.mark.asyncio
async def test_create_movie(db_session: AsyncSession, fake_redis):
    """Test creating a movie"""
    repository = MovieRepository(db_session)
    service = MovieService(repository, fake_redis)
    
    request = CreateMovieRequest(
        title="Test Movie",
        description="A test movie",
        duration_minutes=120,
        language="English",
        release_date=date(2024, 1, 1),
        rating="PG-13",
        genre=["Action", "Adventure"],
        poster_url="http://example.com/poster.jpg",
        trailer_url="http://example.com/trailer.mp4",
    )
    
    movie = await service.create_movie(request)
    
    assert movie.id is not None
    assert movie.title == "Test Movie"
    assert movie.duration_minutes == 120
    assert movie.is_active is True


@pytest.mark.asyncio
async def test_get_movie_by_id(db_session: AsyncSession, fake_redis):
    """Test getting a movie by ID"""
    repository = MovieRepository(db_session)
    service = MovieService(repository, fake_redis)
    
    # Create a movie first
    request = CreateMovieRequest(
        title="Test Movie",
        description="A test movie",
        duration_minutes=120,
        language="English",
        release_date=date(2024, 1, 1),
        rating="PG-13",
        genre=["Action"],
    )
    created_movie = await service.create_movie(request)
    
    # Get the movie
    movie = await service.get_movie_by_id(created_movie.id)
    
    assert movie is not None
    assert movie.id == created_movie.id
    assert movie.title == "Test Movie"


@pytest.mark.asyncio
async def test_update_movie(db_session: AsyncSession, fake_redis):
    """Test updating a movie"""
    repository = MovieRepository(db_session)
    service = MovieService(repository, fake_redis)
    
    # Create a movie
    request = CreateMovieRequest(
        title="Original Title",
        description="Original description",
        duration_minutes=120,
        language="English",
        release_date=date(2024, 1, 1),
        rating="PG-13",
        genre=["Action"],
    )
    created_movie = await service.create_movie(request)
    
    # Update the movie
    update_request = UpdateMovieRequest(
        title="Updated Title",
        duration_minutes=150,
    )
    updated_movie = await service.update_movie(created_movie.id, update_request)
    
    assert updated_movie.title == "Updated Title"
    assert updated_movie.duration_minutes == 150
    assert updated_movie.description == "Original description"


@pytest.mark.asyncio
async def test_delete_movie(db_session: AsyncSession, fake_redis):
    """Test deleting a movie"""
    repository = MovieRepository(db_session)
    service = MovieService(repository, fake_redis)
    
    # Create a movie
    request = CreateMovieRequest(
        title="Test Movie",
        description="A test movie",
        duration_minutes=120,
        language="English",
        release_date=date(2024, 1, 1),
        rating="PG-13",
        genre=["Action"],
    )
    created_movie = await service.create_movie(request)
    
    # Delete the movie
    await service.delete_movie(created_movie.id)
    
    # Try to get the deleted movie
    movie = await service.get_movie_by_id(created_movie.id)
    assert movie is None


@pytest.mark.asyncio
async def test_search_movies(db_session: AsyncSession, fake_redis):
    """Test searching movies"""
    repository = MovieRepository(db_session)
    service = MovieService(repository, fake_redis)
    
    # Create multiple movies
    movies_data = [
        ("Action Movie", ["Action", "Thriller"]),
        ("Comedy Movie", ["Comedy"]),
        ("Action Comedy", ["Action", "Comedy"]),
    ]
    
    for title, genres in movies_data:
        request = CreateMovieRequest(
            title=title,
            description="Test movie",
            duration_minutes=120,
            language="English",
            release_date=date(2024, 1, 1),
            genre=genres,
        )
        await service.create_movie(request)
    
    # Search for action movies
    results = await service.search_movies("action")
    assert len(results) == 2
    
    # Search for comedy movies
    results = await service.search_movies("comedy")
    assert len(results) == 2
