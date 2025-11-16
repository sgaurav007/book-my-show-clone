from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: int = Field(..., gt=0)
    language: str = Field(..., min_length=1, max_length=50)
    release_date: date
    rating: Optional[str] = Field(None, max_length=10)
    genre: Optional[List[str]] = Field(default_factory=list)
    poster_url: Optional[str] = Field(None, max_length=512)
    trailer_url: Optional[str] = Field(None, max_length=512)


class CreateMovieRequest(MovieBase):
    pass


class UpdateMovieRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, min_length=1, max_length=50)
    release_date: Optional[date] = None
    rating: Optional[str] = Field(None, max_length=10)
    genre: Optional[List[str]] = None
    poster_url: Optional[str] = Field(None, max_length=512)
    trailer_url: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None


class MovieResponse(MovieBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
