from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_movie_service
from app.services import MovieService
from app.schemas import MovieResponse, CreateMovieRequest, UpdateMovieRequest

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model=dict, status_code=201)
async def create_movie(
    request: CreateMovieRequest,
    service: MovieService = Depends(get_movie_service),
):
    """Create a new movie"""
    try:
        movie = await service.create_movie(request)
        genres = await service.get_movie_genres(movie.id)
        
        movie_response = MovieResponse(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            duration_minutes=movie.duration_minutes,
            language=movie.language,
            release_date=movie.release_date,
            rating=movie.rating,
            genre=genres,
            poster_url=movie.poster_url,
            trailer_url=movie.trailer_url,
            is_active=movie.is_active,
            created_at=movie.created_at,
            updated_at=movie.updated_at,
        )
        
        return {
            "success": True,
            "message": "Movie created successfully",
            "data": movie_response.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=dict)
async def get_movie_by_id(
    id: int,
    service: MovieService = Depends(get_movie_service),
):
    """Get a movie by ID"""
    movie = await service.get_movie_by_id(id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {id} not found")
    
    genres = await service.get_movie_genres(id)
    movie_response = MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        duration_minutes=movie.duration_minutes,
        language=movie.language,
        release_date=movie.release_date,
        rating=movie.rating,
        genre=genres,
        poster_url=movie.poster_url,
        trailer_url=movie.trailer_url,
        is_active=movie.is_active,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
    )
    
    return {
        "success": True,
        "message": None,
        "data": movie_response.model_dump(),
    }


@router.get("", response_model=dict)
async def get_all_movies(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
):
    """Get all movies with pagination"""
    movies, total = await service.get_all_movies(page, size)
    
    movie_responses = []
    for movie in movies:
        genres = await service.get_movie_genres(movie.id)
        movie_responses.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                duration_minutes=movie.duration_minutes,
                language=movie.language,
                release_date=movie.release_date,
                rating=movie.rating,
                genre=genres,
                poster_url=movie.poster_url,
                trailer_url=movie.trailer_url,
                is_active=movie.is_active,
                created_at=movie.created_at,
                updated_at=movie.updated_at,
            )
        )
    
    total_pages = (total + size - 1) // size
    page_response = {
        "content": [m.model_dump() for m in movie_responses],
        "page": page,
        "size": size,
        "totalElements": total,
        "totalPages": total_pages,
        "last": page >= total_pages - 1,
    }
    
    return {
        "success": True,
        "message": None,
        "data": page_response,
    }


@router.get("/search", response_model=dict)
async def search_movies(
    q: str = Query(..., min_length=1),
    service: MovieService = Depends(get_movie_service),
):
    """Search movies by title or genre"""
    movies = await service.search_movies(q)
    
    movie_responses = []
    for movie in movies:
        genres = await service.get_movie_genres(movie.id)
        movie_responses.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                duration_minutes=movie.duration_minutes,
                language=movie.language,
                release_date=movie.release_date,
                rating=movie.rating,
                genre=genres,
                poster_url=movie.poster_url,
                trailer_url=movie.trailer_url,
                is_active=movie.is_active,
                created_at=movie.created_at,
                updated_at=movie.updated_at,
            )
        )
    
    return {
        "success": True,
        "message": None,
        "data": [m.model_dump() for m in movie_responses],
    }


@router.put("/{id}", response_model=dict)
async def update_movie(
    id: int,
    request: UpdateMovieRequest,
    service: MovieService = Depends(get_movie_service),
):
    """Update a movie"""
    try:
        movie = await service.update_movie(id, request)
        genres = await service.get_movie_genres(movie.id)
        
        movie_response = MovieResponse(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            duration_minutes=movie.duration_minutes,
            language=movie.language,
            release_date=movie.release_date,
            rating=movie.rating,
            genre=genres,
            poster_url=movie.poster_url,
            trailer_url=movie.trailer_url,
            is_active=movie.is_active,
            created_at=movie.created_at,
            updated_at=movie.updated_at,
        )
        
        return {
            "success": True,
            "message": "Movie updated successfully",
            "data": movie_response.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", response_model=dict)
async def delete_movie(
    id: int,
    service: MovieService = Depends(get_movie_service),
):
    """Delete a movie"""
    try:
        await service.delete_movie(id)
        return {
            "success": True,
            "message": "Movie deleted successfully",
            "data": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
