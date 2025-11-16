"""Tests for shared dependencies."""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.dependencies import (
    get_current_user_id,
    require_authentication,
    get_current_username,
    get_current_user_role,
    require_admin_role,
)


class TestDependencies:
    """Test shared dependency functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_id_authenticated(self):
        """Test getting user ID from authenticated request."""
        mock_request = MagicMock()
        mock_request.state.user_id = 123

        user_id = await get_current_user_id(mock_request)
        assert user_id == 123

    @pytest.mark.asyncio
    async def test_get_current_user_id_unauthenticated(self):
        """Test getting user ID from unauthenticated request."""
        mock_request = MagicMock()
        mock_request.state = MagicMock(spec=[])  # No user_id attribute

        user_id = await get_current_user_id(mock_request)
        assert user_id is None

    @pytest.mark.asyncio
    async def test_require_authentication_success(self):
        """Test require_authentication with authenticated user."""
        mock_request = MagicMock()
        mock_request.state.user_id = 123

        user_id = await require_authentication(mock_request)
        assert user_id == 123

    @pytest.mark.asyncio
    async def test_require_authentication_failure(self):
        """Test require_authentication with unauthenticated user."""
        mock_request = MagicMock()
        mock_request.state = MagicMock(spec=[])

        with pytest.raises(HTTPException) as exc_info:
            await require_authentication(mock_request)

        assert exc_info.value.status_code == 401
        assert "UNAUTHORIZED" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_username(self):
        """Test getting username from request."""
        mock_request = MagicMock()
        mock_request.state.username = "testuser"

        username = await get_current_username(mock_request)
        assert username == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_role(self):
        """Test getting user role from request."""
        mock_request = MagicMock()
        mock_request.state.role = "USER"

        role = await get_current_user_role(mock_request)
        assert role == "USER"

    @pytest.mark.asyncio
    async def test_require_admin_role_success(self):
        """Test require_admin_role with admin user."""
        mock_request = MagicMock()
        mock_request.state.user_id = 1
        mock_request.state.role = "ADMIN"

        user_id = await require_admin_role(mock_request)
        assert user_id == 1

    @pytest.mark.asyncio
    async def test_require_admin_role_non_admin(self):
        """Test require_admin_role with non-admin user."""
        mock_request = MagicMock()
        mock_request.state.user_id = 123
        mock_request.state.role = "USER"

        with pytest.raises(HTTPException) as exc_info:
            await require_admin_role(mock_request)

        assert exc_info.value.status_code == 403
        assert "FORBIDDEN" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_admin_role_unauthenticated(self):
        """Test require_admin_role with unauthenticated user."""
        mock_request = MagicMock()
        mock_request.state = MagicMock(spec=[])

        with pytest.raises(HTTPException) as exc_info:
            await require_admin_role(mock_request)

        assert exc_info.value.status_code == 401
