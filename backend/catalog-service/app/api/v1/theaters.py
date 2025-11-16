from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_theater_service
from app.services import TheaterService
from app.schemas import TheaterResponse, CreateTheaterRequest

router = APIRouter(prefix="/theaters", tags=["theaters"])


@router.post("", response_model=dict, status_code=201)
async def create_theater(
    request: CreateTheaterRequest,
    service: TheaterService = Depends(get_theater_service),
):
    """Create a new theater"""
    try:
        theater = await service.create_theater(request)
        theater_response = TheaterResponse.model_validate(theater)
        
        return {
            "success": True,
            "message": "Theater created successfully",
            "data": theater_response.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=dict)
async def get_theater_by_id(
    id: int,
    service: TheaterService = Depends(get_theater_service),
):
    """Get a theater by ID"""
    theater = await service.get_theater_by_id(id)
    if not theater:
        raise HTTPException(status_code=404, detail=f"Theater with id {id} not found")
    
    theater_response = TheaterResponse.model_validate(theater)
    
    return {
        "success": True,
        "message": None,
        "data": theater_response.model_dump(),
    }


@router.get("", response_model=dict)
async def get_theaters(
    city: Optional[str] = Query(None),
    service: TheaterService = Depends(get_theater_service),
):
    """Get all theaters, optionally filtered by city"""
    if city:
        theaters = await service.get_theaters_by_city(city)
    else:
        theaters = await service.get_all_theaters()
    
    theater_responses = [TheaterResponse.model_validate(t) for t in theaters]
    
    return {
        "success": True,
        "message": None,
        "data": [t.model_dump() for t in theater_responses],
    }


@router.delete("/{id}", response_model=dict)
async def delete_theater(
    id: int,
    service: TheaterService = Depends(get_theater_service),
):
    """Delete a theater"""
    try:
        await service.delete_theater(id)
        return {
            "success": True,
            "message": "Theater deleted successfully",
            "data": None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
