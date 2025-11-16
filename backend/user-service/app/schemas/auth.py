"""Authentication-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field

from .user import UserProfileResponse


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Response schema for login."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in milliseconds")
    user: UserProfileResponse = Field(..., description="User profile information")


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str = Field(..., description="Refresh token")
