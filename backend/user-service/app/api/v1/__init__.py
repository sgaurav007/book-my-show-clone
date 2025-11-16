"""API v1 package for User Service."""

from fastapi import APIRouter

from . import auth, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

__all__ = ["api_router"]
