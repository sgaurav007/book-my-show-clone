"""FastAPI dependencies for dependency injection."""

from typing import AsyncGenerator, Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from bookmyshow_common.database import DatabaseManager
from bookmyshow_common.exceptions import InvalidTokenException
from bookmyshow_common.security import JwtTokenProvider

from app.config import Settings, get_settings
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenData
from app.services.auth_service import AuthService
from app.services.user_service import UserService


# Global instances (will be initialized in main.py)
_db_manager: DatabaseManager = None
_jwt_provider: JwtTokenProvider = None


def init_dependencies(settings: Settings):
    """Initialize global dependencies.
    
    Args:
        settings: Application settings
    """
    global _db_manager, _jwt_provider
    
    _db_manager = DatabaseManager(
        database_url=settings.database_url,
        echo=settings.debug,
    )
    
    _jwt_provider = JwtTokenProvider(
        secret_key=settings.jwt_secret,
        access_token_expiration=settings.access_token_expiration,
        refresh_token_expiration=settings.refresh_token_expiration,
        algorithm=settings.jwt_algorithm,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.
    
    Yields:
        Database session
    """
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized")
    
    async for session in _db_manager.get_session():
        yield session


def get_jwt_provider() -> JwtTokenProvider:
    """Get JWT token provider.
    
    Returns:
        JWT token provider instance
    """
    if _jwt_provider is None:
        raise RuntimeError("JWT provider not initialized")
    return _jwt_provider


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Get user repository.
    
    Args:
        session: Database session
        
    Returns:
        User repository instance
    """
    return UserRepository(session)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service.
    
    Args:
        repository: User repository
        
    Returns:
        User service instance
    """
    return UserService(repository)


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
    user_service: UserService = Depends(get_user_service),
    jwt_provider: JwtTokenProvider = Depends(get_jwt_provider),
) -> AuthService:
    """Get auth service.
    
    Args:
        repository: User repository
        user_service: User service
        jwt_provider: JWT provider
        
    Returns:
        Auth service instance
    """
    return AuthService(repository, user_service, jwt_provider)


async def get_current_user(
    authorization: Annotated[str, Header()] = None,
    jwt_provider: JwtTokenProvider = Depends(get_jwt_provider),
) -> TokenData:
    """Get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        jwt_provider: JWT provider
        
    Returns:
        Token data with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Validate token and extract user info
        user_id = jwt_provider.get_user_id_from_token(token)
        email = jwt_provider.get_email_from_token(token)
        
        return TokenData(user_id=user_id, email=email)
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
