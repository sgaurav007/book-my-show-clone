from fastapi import APIRouter
from .movies import router as movies_router
from .theaters import router as theaters_router
from .shows import router as shows_router
from .cities import router as cities_router

api_router = APIRouter(prefix="/api/catalog")

api_router.include_router(movies_router)
api_router.include_router(theaters_router)
api_router.include_router(shows_router)
api_router.include_router(cities_router)

__all__ = ["api_router"]
