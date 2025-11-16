"""User management API endpoints."""

from fastapi import APIRouter, Depends, status

from bookmyshow_common.schemas import ApiResponse

from app.dependencies import get_current_user, get_user_service
from app.schemas.token import TokenData
from app.schemas.user import UpdateProfileRequest, UserProfileResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user",
)
async def get_my_profile(
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        user_service: User service instance
        
    Returns:
        API response with user profile
    """
    user = await user_service.get_user_profile(current_user.user_id)
    return ApiResponse.success_response(data=user)


@router.put(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user",
)
async def update_my_profile(
    request: UpdateProfileRequest,
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user's profile.
    
    Args:
        request: Profile update data
        current_user: Current authenticated user
        user_service: User service instance
        
    Returns:
        API response with updated user profile
    """
    user = await user_service.update_user_profile(current_user.user_id, request)
    return ApiResponse.success_response(
        data=user,
        message="Profile updated successfully",
    )
