from fastapi import APIRouter, Depends

from app.dependencies import get_theater_service
from app.services import TheaterService

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", response_model=dict)
async def get_all_cities(
    service: TheaterService = Depends(get_theater_service),
):
    """Get all cities with theater count"""
    cities = await service.get_all_cities()
    
    return {
        "success": True,
        "message": None,
        "data": [c.model_dump() for c in cities],
    }
