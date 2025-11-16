"""Shared dependencies for the API Gateway."""
from typing import Optional
from fastapi import Request, HTTPException, status
from datetime import datetime


async def get_current_user_id(request: Request) -> Optional[int]:
    """
    Extract the current authenticated user ID from request state.

    This dependency can be used in route handlers to get the authenticated user ID.
    Returns None if the user is not authenticated.

    Args:
        request: The FastAPI request object

    Returns:
        User ID if authenticated, None otherwise
    """
    return getattr(request.state, "user_id", None)


async def require_authentication(request: Request) -> int:
    """
    Require authentication and return the user ID.

    This dependency ensures the request is authenticated and returns the user ID.
    Raises HTTPException if not authenticated.

    Args:
        request: The FastAPI request object

    Returns:
        User ID

    Raises:
        HTTPException: If user is not authenticated
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            },
        )
    return user_id


async def get_current_username(request: Request) -> Optional[str]:
    """
    Extract the current authenticated username from request state.

    Args:
        request: The FastAPI request object

    Returns:
        Username if authenticated, None otherwise
    """
    return getattr(request.state, "username", None)


async def get_current_user_role(request: Request) -> Optional[str]:
    """
    Extract the current authenticated user role from request state.

    Args:
        request: The FastAPI request object

    Returns:
        User role if authenticated, None otherwise
    """
    return getattr(request.state, "role", None)


async def require_admin_role(request: Request) -> int:
    """
    Require admin role and return the user ID.

    This dependency ensures the request is authenticated with admin role.
    Raises HTTPException if not authenticated or not an admin.

    Args:
        request: The FastAPI request object

    Returns:
        User ID

    Raises:
        HTTPException: If user is not authenticated or not an admin
    """
    user_id = await require_authentication(request)
    role = getattr(request.state, "role", None)

    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Admin access required",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            },
        )

    return user_id
