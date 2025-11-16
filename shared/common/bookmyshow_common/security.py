"""JWT token provider and security utilities."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .exceptions import InvalidTokenException


class JwtTokenProvider:
    """JWT token provider for access and refresh tokens."""

    def __init__(
        self,
        secret_key: str = "bookmyshow-secret-key-for-jwt-token-generation-and-validation-must-be-at-least-256-bits",
        access_token_expiration: int = 3600000,  # 1 hour in milliseconds
        refresh_token_expiration: int = 86400000,  # 24 hours in milliseconds
        algorithm: str = "HS256",
    ):
        """Initialize JWT token provider.
        
        Args:
            secret_key: Secret key for JWT signing
            access_token_expiration: Access token expiration in milliseconds
            refresh_token_expiration: Refresh token expiration in milliseconds
            algorithm: JWT algorithm
        """
        self.secret_key = secret_key
        self.access_token_expiration = access_token_expiration
        self.refresh_token_expiration = refresh_token_expiration
        self.algorithm = algorithm

    def generate_access_token(self, email: str, user_id: int) -> str:
        """Generate JWT access token.
        
        Args:
            email: User email
            user_id: User ID
            
        Returns:
            JWT access token
        """
        now = datetime.utcnow()
        expiry = now + timedelta(milliseconds=self.access_token_expiration)
        
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": now,
            "exp": expiry,
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self) -> str:
        """Generate refresh token (UUID).
        
        Returns:
            Refresh token string
        """
        return str(uuid.uuid4())

    def get_user_id_from_token(self, token: str) -> int:
        """Extract user ID from JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User ID
            
        Raises:
            InvalidTokenException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise InvalidTokenException("Token missing subject claim")
            return int(user_id)
        except JWTError as e:
            raise InvalidTokenException(f"Invalid JWT token: {str(e)}")
        except ValueError:
            raise InvalidTokenException("Invalid user ID in token")

    def get_email_from_token(self, token: str) -> str:
        """Extract email from JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User email
            
        Raises:
            InvalidTokenException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email = payload.get("email")
            if email is None:
                raise InvalidTokenException("Token missing email claim")
            return email
        except JWTError as e:
            raise InvalidTokenException(f"Invalid JWT token: {str(e)}")

    def validate_token(self, token: str) -> bool:
        """Validate JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return True
        except JWTError:
            return False

    def get_access_token_expiration(self) -> int:
        """Get access token expiration in milliseconds.
        
        Returns:
            Access token expiration in milliseconds
        """
        return self.access_token_expiration

    def get_refresh_token_expiration(self) -> int:
        """Get refresh token expiration in milliseconds.
        
        Returns:
            Refresh token expiration in milliseconds
        """
        return self.refresh_token_expiration


class PasswordHasher:
    """Password hashing utilities using bcrypt."""

    def __init__(self):
        """Initialize password hasher."""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)
