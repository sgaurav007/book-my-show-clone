"""JWT Authentication middleware for the API Gateway."""
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = [
    # Auth endpoints (new v1 paths)
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    # User endpoints (new v1 paths)
    "/api/v1/users/register",
    "/api/v1/users/login",
    "/api/v1/users/refresh-token",
    # Catalog endpoints (new v1 paths) - GET only
    "/api/v1/movies",
    "/api/v1/theaters",
    "/api/v1/shows",
    "/api/v1/cities",
    # Legacy paths (without v1)
    "/api/users/register",
    "/api/users/login",
    "/api/users/refresh-token",
    "/api/catalog/movies",
    "/api/catalog/theaters",
    "/api/catalog/shows",
    "/api/catalog/cities",
    # System endpoints
    "/health",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
]


class JWTValidator:
    """JWT token validation and claims extraction."""

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def validate_token(self, token: str) -> bool:
        """Validate JWT token and check expiration."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return False
            return True
        except JWTError as e:
            logger.debug(f"Token validation failed: {str(e)}")
            return False

    def get_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract all claims from JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Failed to extract claims from token: {str(e)}")
            return None

    def get_user_id(self, token: str) -> Optional[int]:
        """Extract user ID from token."""
        claims = self.get_claims(token)
        if claims:
            return claims.get("userId") or claims.get("user_id")
        return None

    def get_username(self, token: str) -> Optional[str]:
        """Extract username from token."""
        claims = self.get_claims(token)
        if claims:
            return claims.get("sub")  # Subject typically contains username
        return None

    def get_role(self, token: str) -> Optional[str]:
        """Extract role from token."""
        claims = self.get_claims(token)
        if claims:
            return claims.get("role")
        return None


def is_public_endpoint(path: str, method: str) -> bool:
    """Check if the endpoint is public (doesn't require authentication)."""
    # Exact match or prefix match for public endpoints
    for public_path in PUBLIC_ENDPOINTS:
        if path == public_path or path.startswith(public_path):
            # Additional check for GET methods on catalog endpoints
            if public_path.startswith("/api/catalog") and method != "GET":
                return False
            return True
    return False


async def auth_middleware(request: Request, call_next):
    """Authentication middleware to validate JWT tokens."""
    path = request.url.path
    method = request.method

    # Skip authentication for public endpoints
    if is_public_endpoint(path, method):
        return await call_next(request)

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": "MISSING_AUTHORIZATION",
                    "message": "Missing authorization header",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )

    # Validate Bearer token format
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": "INVALID_AUTHORIZATION",
                    "message": "Invalid authorization header format",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )

    # Extract token
    token = auth_header[7:]  # Remove "Bearer " prefix

    # Validate token
    jwt_validator = JWTValidator(settings.jwt_secret, settings.jwt_algorithm)
    if not jwt_validator.validate_token(token):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired token",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )

    # Extract user information from token
    try:
        user_id = jwt_validator.get_user_id(token)
        username = jwt_validator.get_username(token)
        role = jwt_validator.get_role(token)

        # Add user information to request state for downstream use
        request.state.user_id = user_id
        request.state.username = username
        request.state.role = role

        # Add custom headers for backend services
        # We'll modify the request headers in the proxy function
        request.state.auth_headers = {
            "X-User-Id": str(user_id) if user_id else "",
            "X-Username": username or "",
            "X-User-Role": role or "",
        }

        logger.debug(f"Authenticated user: {username} (ID: {user_id}, Role: {role})")

    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": "TOKEN_VALIDATION_FAILED",
                    "message": f"Token validation failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        )

    # Continue with the request
    return await call_next(request)
