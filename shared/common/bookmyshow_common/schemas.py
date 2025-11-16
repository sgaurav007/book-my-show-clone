"""Base Pydantic schemas for BookMyShow application."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base Pydantic schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    """Base schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


class ApiResponse(BaseSchema, Generic[T]):
    """Generic API response wrapper."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    timestamp: datetime = datetime.utcnow()

    @classmethod
    def success_response(cls, data: Optional[T] = None, message: str = "Success"):
        """Create a success response."""
        return cls(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
        )

    @classmethod
    def error_response(cls, message: str):
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            data=None,
            timestamp=datetime.utcnow(),
        )


class ErrorDetail(BaseModel):
    """Error detail schema."""

    field: str
    message: str


class ErrorResponse(BaseSchema):
    """Error response schema."""

    status: int
    error: str
    message: str
    path: str
    timestamp: datetime = datetime.utcnow()
    validation_errors: Optional[list[ErrorDetail]] = None


class PageResponse(BaseSchema, Generic[T]):
    """Paginated response schema."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
