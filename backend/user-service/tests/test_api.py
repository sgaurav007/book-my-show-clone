"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-service"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == user_data["email"]
    assert data["data"]["first_name"] == user_data["first_name"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }
    
    # First registration
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register user first
    user_data = {
        "email": "login@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_data = {
        "email": "login@example.com",
        "password": "password123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Test login with invalid password."""
    # Register user first
    user_data = {
        "email": "logintest@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login with wrong password
    login_data = {
        "email": "logintest@example.com",
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_get_user_profile(client: AsyncClient):
    """Test getting user profile."""
    # Register and login
    user_data = {
        "email": "profile@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "password123"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Get profile
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient):
    """Test updating user profile."""
    # Register and login
    user_data = {
        "email": "update@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "update@example.com", "password": "password123"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Update profile
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "phone_number": "9876543210",
    }
    response = await client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["first_name"] == "Updated"
    assert data["data"]["last_name"] == "Name"
    assert data["data"]["phone_number"] == "9876543210"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
