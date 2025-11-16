"""User service for business logic."""

from datetime import datetime

from bookmyshow_common.exceptions import (
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)
from bookmyshow_common.security import PasswordHasher

from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import RegisterRequest, UpdateProfileRequest, UserProfileResponse


class UserService:
    """Service for user-related business logic."""

    def __init__(self, repository: UserRepository):
        """Initialize user service.
        
        Args:
            repository: User repository instance
        """
        self.repository = repository
        self.password_hasher = PasswordHasher()

    async def register_user(self, request: RegisterRequest) -> UserProfileResponse:
        """Register a new user.
        
        Args:
            request: User registration request
            
        Returns:
            User profile response
            
        Raises:
            ResourceAlreadyExistsException: If user with email already exists
        """
        # Check if user already exists
        if await self.repository.exists_by_email(request.email):
            raise ResourceAlreadyExistsException(
                f"User with email {request.email} already exists"
            )

        # Create user
        user = User(
            email=request.email,
            password_hash=self.password_hasher.hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            role="CUSTOMER",
            is_active=True,
            is_email_verified=False,
        )

        saved_user = await self.repository.create_user(user)
        return self._map_to_user_profile_response(saved_user)

    async def get_user_profile(self, user_id: int) -> UserProfileResponse:
        """Get user profile by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile response
            
        Raises:
            ResourceNotFoundException: If user not found
        """
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(message=f"User not found with id: {user_id}")
        return self._map_to_user_profile_response(user)

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User model
            
        Raises:
            ResourceNotFoundException: If user not found
        """
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise ResourceNotFoundException(message=f"User not found with email: {email}")
        return user

    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User model
            
        Raises:
            ResourceNotFoundException: If user not found
        """
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(message=f"User not found with id: {user_id}")
        return user

    async def update_user_profile(
        self, user_id: int, request: UpdateProfileRequest
    ) -> UserProfileResponse:
        """Update user profile.
        
        Args:
            user_id: User ID
            request: Update profile request
            
        Returns:
            Updated user profile response
            
        Raises:
            ResourceNotFoundException: If user not found
        """
        user = await self.get_user_by_id(user_id)

        # Update fields if provided
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.last_name is not None:
            user.last_name = request.last_name
        if request.phone_number is not None:
            user.phone_number = request.phone_number

        updated_user = await self.repository.update_user(user)
        return self._map_to_user_profile_response(updated_user)

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp.
        
        Args:
            user_id: User ID
        """
        await self.repository.update_last_login(user_id, datetime.utcnow())

    def _map_to_user_profile_response(self, user: User) -> UserProfileResponse:
        """Map User model to UserProfileResponse.
        
        Args:
            user: User model instance
            
        Returns:
            User profile response
        """
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )
