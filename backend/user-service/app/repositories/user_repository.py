"""User repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken, User


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_user(self, user: User) -> User:
        """Create a new user.
        
        Args:
            user: User model instance
            
        Returns:
            Created user
        """
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email.
        
        Args:
            email: User email
            
        Returns:
            True if user exists
        """
        result = await self.session.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None

    async def update_user(self, user: User) -> User:
        """Update user.
        
        Args:
            user: User model instance
            
        Returns:
            Updated user
        """
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_last_login(self, user_id: int, last_login: datetime) -> None:
        """Update user's last login timestamp.
        
        Args:
            user_id: User ID
            last_login: Last login timestamp
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login_at = last_login
            await self.session.flush()

    # RefreshToken operations

    async def save_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        """Save refresh token.
        
        Args:
            refresh_token: RefreshToken model instance
            
        Returns:
            Saved refresh token
        """
        self.session.add(refresh_token)
        await self.session.flush()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string.
        
        Args:
            token: Refresh token string
            
        Returns:
            RefreshToken or None
        """
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_refresh_token(self, refresh_token: RefreshToken) -> None:
        """Delete refresh token.
        
        Args:
            refresh_token: RefreshToken model instance
        """
        await self.session.delete(refresh_token)
        await self.session.flush()

    async def delete_refresh_token_by_token(self, token: str) -> None:
        """Delete refresh token by token string.
        
        Args:
            token: Refresh token string
        """
        await self.session.execute(delete(RefreshToken).where(RefreshToken.token == token))
        await self.session.flush()
