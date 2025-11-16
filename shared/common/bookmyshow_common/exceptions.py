"""Custom exception classes for BookMyShow application."""

from typing import Any, Optional
from fastapi import status


class BookMyShowException(Exception):
    """Base exception class for BookMyShow application."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(BookMyShowException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: Optional[str] = None,
        resource_name: Optional[str] = None,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
    ):
        if message is None and resource_name and field_name and field_value:
            message = f"{resource_name} not found with {field_name}: '{field_value}'"
        elif message is None:
            message = "Resource not found"
        
        self.resource_name = resource_name
        self.field_name = field_name
        self.field_value = field_value
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ResourceAlreadyExistsException(BookMyShowException):
    """Exception raised when a resource already exists."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationException(BookMyShowException):
    """Exception raised for validation errors."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class BusinessException(BookMyShowException):
    """Exception raised for business logic violations."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InvalidTokenException(BookMyShowException):
    """Exception raised for invalid tokens."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class UnauthorizedException(BookMyShowException):
    """Exception raised for unauthorized access."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class BadRequestException(BookMyShowException):
    """Exception raised for bad requests."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
