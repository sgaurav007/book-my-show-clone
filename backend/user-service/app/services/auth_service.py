"""Authentication service for business logic."""

from datetime import datetime, timedelta

from bookmyshow_common.exceptions import InvalidTokenException, UnauthorizedException
from bookmyshow_common.security import JwtTokenProvider, PasswordHasher

from app.models import RefreshToken
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserProfileResponse
from app.services.user_service import UserService


class AuthService:
    """Service for authentication-related business logic."""

    def __init__(
        self,
        repository: UserRepository,
        user_service: UserService,
        jwt_provider: JwtTokenProvider,
    ):
        """Initialize auth service.
        
        Args:
            repository: User repository instance
            user_service: User service instance
            jwt_provider: JWT token provider instance
        """
        self.repository = repository
        self.user_service = user_service
        self.jwt_provider = jwt_provider
        self.password_hasher = PasswordHasher()

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate user and generate tokens.
        
        Args:
            request: Login request with email and password
            
        Returns:
            Login response with tokens and user profile
            
        Raises:
            UnauthorizedException: If authentication fails
        """
        # Get user by email
        user = await self.user_service.get_user_by_email(request.email)

        # Verify password
        if not self.password_hasher.verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        # Generate tokens
        access_token = self.jwt_provider.generate_access_token(user.email, user.id)
        refresh_token_str = self.jwt_provider.generate_refresh_token()

        # Save refresh token
        await self._save_refresh_token(user.id, refresh_token_str)

        # Update last login
        await self.user_service.update_last_login(user.id)

        # Refresh user to get updated last_login_at
        user = await self.user_service.get_user_by_id(user.id)

        user_profile = UserProfileResponse(
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

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="Bearer",
            expires_in=self.jwt_provider.get_access_token_expiration(),
            user=user_profile,
        )

    async def refresh_access_token(self, refresh_token_str: str) -> LoginResponse:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token_str: Refresh token string
            
        Returns:
            Login response with new access token
            
        Raises:
            InvalidTokenException: If refresh token is invalid or expired
        """
        # Get refresh token from database
        refresh_token = await self.repository.get_refresh_token_by_token(refresh_token_str)
        if not refresh_token:
            raise InvalidTokenException("Invalid refresh token")

        # Check if token is expired
        if refresh_token.expires_at < datetime.utcnow():
            await self.repository.delete_refresh_token(refresh_token)
            raise InvalidTokenException("Refresh token has expired")

        # Get user
        user = await self.user_service.get_user_by_id(refresh_token.user_id)

        # Generate new access token
        new_access_token = self.jwt_provider.generate_access_token(user.email, user.id)

        user_profile = UserProfileResponse(
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

        return LoginResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,
            token_type="Bearer",
            expires_in=self.jwt_provider.get_access_token_expiration(),
            user=user_profile,
        )

    async def logout(self, refresh_token: str) -> None:
        """Logout user by invalidating refresh token.
        
        Args:
            refresh_token: Refresh token to invalidate
        """
        await self.repository.delete_refresh_token_by_token(refresh_token)

    async def _save_refresh_token(self, user_id: int, token: str) -> None:
        """Save refresh token to database.
        
        Args:
            user_id: User ID
            token: Refresh token string
        """
        expires_at = datetime.utcnow() + timedelta(
            milliseconds=self.jwt_provider.get_refresh_token_expiration()
        )

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        await self.repository.save_refresh_token(refresh_token)
