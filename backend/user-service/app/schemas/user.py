"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    first_name: str = Field(..., min_length=1, description="User first name")
    last_name: str = Field(..., min_length=1, description="User last name")
    phone_number: Optional[str] = Field(None, description="User phone number")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is not None and v.strip():
            # Remove any whitespace
            v = v.strip()
            # Basic validation: should be 10-15 digits, optionally starting with +
            if not v.replace("+", "").isdigit():
                raise ValueError("Phone number must contain only digits and optional leading +")
            if len(v.replace("+", "")) < 10 or len(v.replace("+", "")) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
        return v


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""

    first_name: Optional[str] = Field(None, min_length=1, description="User first name")
    last_name: Optional[str] = Field(None, min_length=1, description="User last name")
    phone_number: Optional[str] = Field(None, description="User phone number")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is not None and v.strip():
            v = v.strip()
            if not v.replace("+", "").isdigit():
                raise ValueError("Phone number must contain only digits and optional leading +")
            if len(v.replace("+", "")) < 10 or len(v.replace("+", "")) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
        return v


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""

    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
