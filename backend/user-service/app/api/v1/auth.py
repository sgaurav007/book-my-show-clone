"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, status

from bookmyshow_common.schemas import ApiResponse

from app.dependencies import get_auth_service, get_user_service
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest
from app.schemas.user import RegisterRequest, UserProfileResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[UserProfileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password",
)
async def register(
    request: RegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Register a new user.
    
    Args:
        request: User registration data
        user_service: User service instance
        
    Returns:
        API response with user profile
    """
    user = await user_service.register_user(request)
    return ApiResponse.success_response(
        data=user,
        message="User registered successfully",
    )


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive access and refresh tokens",
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login user and return tokens.
    
    Args:
        request: Login credentials
        auth_service: Auth service instance
        
    Returns:
        API response with tokens and user profile
    """
    response = await auth_service.login(request)
    return ApiResponse.success_response(
        data=response,
        message="Login successful",
    )


@router.post(
    "/refresh",
    response_model=ApiResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token.
    
    Args:
        request: Refresh token request
        auth_service: Auth service instance
        
    Returns:
        API response with new access token
    """
    response = await auth_service.refresh_access_token(request.refresh_token)
    return ApiResponse.success_response(
        data=response,
        message="Token refreshed successfully",
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Invalidate refresh token and logout user",
)
async def logout(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logout user by invalidating refresh token.
    
    Args:
        request: Refresh token to invalidate
        auth_service: Auth service instance
        
    Returns:
        API response confirming logout
    """
    await auth_service.logout(request.refresh_token)
    return ApiResponse.success_response(
        data=None,
        message="Logout successful",
    )
