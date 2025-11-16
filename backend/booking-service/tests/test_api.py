import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"


@pytest.mark.asyncio
async def test_lock_seats_success(client: AsyncClient, sample_lock_seats_request):
    """Test successful seat locking"""
    response = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Seats locked successfully"
    assert data["data"]["user_id"] == sample_lock_seats_request["user_id"]
    assert data["data"]["show_id"] == sample_lock_seats_request["show_id"]
    assert data["data"]["booking_status"] == "PENDING"
    assert len(data["data"]["seats"]) == 1


@pytest.mark.asyncio
async def test_lock_seats_invalid_request(client: AsyncClient):
    """Test seat locking with invalid request"""
    invalid_request = {
        "user_id": 1,
        "show_id": 1,
        "seats": []  # Empty seats list
    }
    
    response = await client.post("/api/bookings/lock-seats", json=invalid_request)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_confirm_booking_success(client: AsyncClient, sample_lock_seats_request):
    """Test successful booking confirmation"""
    # First, lock seats to create a booking
    lock_response = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    booking_id = lock_response.json()["data"]["id"]
    
    # Confirm the booking
    confirm_request = {"payment_id": 999}
    response = await client.post(f"/api/bookings/{booking_id}/confirm", json=confirm_request)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Booking confirmed successfully"
    assert data["data"]["booking_status"] == "CONFIRMED"
    assert data["data"]["payment_id"] == 999


@pytest.mark.asyncio
async def test_confirm_booking_not_found(client: AsyncClient):
    """Test confirming a non-existent booking"""
    confirm_request = {"payment_id": 999}
    response = await client.post("/api/bookings/99999/confirm", json=confirm_request)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_booking_by_id(client: AsyncClient, sample_lock_seats_request):
    """Test getting a booking by ID"""
    # Create a booking first
    lock_response = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    booking_id = lock_response.json()["data"]["id"]
    
    # Get the booking
    response = await client.get(f"/api/bookings/{booking_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == booking_id


@pytest.mark.asyncio
async def test_get_booking_not_found(client: AsyncClient):
    """Test getting a non-existent booking"""
    response = await client.get("/api/bookings/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_booking_success(client: AsyncClient, sample_lock_seats_request):
    """Test successful booking cancellation"""
    # Create a booking first
    lock_response = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    booking_id = lock_response.json()["data"]["id"]
    
    # Cancel the booking
    response = await client.delete(f"/api/bookings/{booking_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Booking cancelled successfully"


@pytest.mark.asyncio
async def test_cancel_booking_not_found(client: AsyncClient):
    """Test cancelling a non-existent booking"""
    response = await client.delete("/api/bookings/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_bookings_by_user_id(client: AsyncClient, sample_lock_seats_request):
    """Test getting all bookings for a user"""
    # Create multiple bookings
    for _ in range(3):
        await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    
    # Get all bookings for the user
    user_id = sample_lock_seats_request["user_id"]
    response = await client.get(f"/api/bookings/user/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_double_booking_prevention(client: AsyncClient, sample_lock_seats_request):
    """Test that the same seats cannot be booked twice"""
    # First booking
    response1 = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    assert response1.status_code == 200
    
    # Try to book the same seats again
    response2 = await client.post("/api/bookings/lock-seats", json=sample_lock_seats_request)
    assert response2.status_code == 500  # Should fail due to locked seats
