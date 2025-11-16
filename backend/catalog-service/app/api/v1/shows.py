from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_show_service, get_seat_service
from app.services import ShowService, SeatService
from app.schemas import ShowResponse, CreateShowRequest, SeatResponse

router = APIRouter(prefix="/shows", tags=["shows"])


@router.post("", response_model=dict, status_code=201)
async def create_show(
    request: CreateShowRequest,
    service: ShowService = Depends(get_show_service),
):
    """Create a new show"""
    try:
        show = await service.create_show(request)
        show_response = ShowResponse.model_validate(show)
        
        return {
            "success": True,
            "message": "Show created successfully",
            "data": show_response.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=dict)
async def get_show_by_id(
    id: int,
    service: ShowService = Depends(get_show_service),
):
    """Get a show by ID"""
    show = await service.get_show_by_id(id)
    if not show:
        raise HTTPException(status_code=404, detail=f"Show with id {id} not found")
    
    show_response = ShowResponse.model_validate(show)
    
    return {
        "success": True,
        "message": None,
        "data": show_response.model_dump(),
    }


@router.get("", response_model=dict)
async def get_shows(
    movieId: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    date: Optional[date] = Query(None),
    service: ShowService = Depends(get_show_service),
):
    """Get shows with optional filters (movieId, city, date)"""
    shows = []
    
    if movieId and city and date:
        shows = await service.get_shows_by_movie_city_and_date(movieId, city, date)
    elif movieId and city:
        shows = await service.get_shows_by_movie_and_city(movieId, city)
    elif movieId:
        shows = await service.get_shows_by_movie(movieId)
    elif date:
        shows = await service.get_shows_by_date(date)
    
    show_responses = [ShowResponse.model_validate(s) for s in shows]
    
    return {
        "success": True,
        "message": None,
        "data": [s.model_dump() for s in show_responses],
    }


@router.get("/{id}/seats", response_model=dict)
async def get_show_seats(
    id: int,
    show_service: ShowService = Depends(get_show_service),
    seat_service: SeatService = Depends(get_seat_service),
):
    """Get all seats for a show"""
    show = await show_service.get_show_by_id(id)
    if not show:
        raise HTTPException(status_code=404, detail=f"Show with id {id} not found")
    
    seats = await seat_service.get_seats_by_screen(show.screen_id)
    seat_responses = [SeatResponse.model_validate(s) for s in seats]
    
    return {
        "success": True,
        "message": None,
        "data": [s.model_dump() for s in seat_responses],
    }


@router.delete("/{id}", response_model=dict)
async def delete_show(
    id: int,
    service: ShowService = Depends(get_show_service),
):
    """Delete a show"""
    try:
        await service.delete_show(id)
        return {
            "success": True,
            "message": "Show deleted successfully",
            "data": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
