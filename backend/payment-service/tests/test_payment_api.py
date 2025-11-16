import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models.payment import PaymentMethod


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "payment-service"


@pytest.mark.asyncio
async def test_initiate_payment(client: AsyncClient):
    """Test payment initiation"""
    payload = {
        "booking_id": 1,
        "user_id": 1,
        "amount": 100.50,
        "payment_method": "CARD",
        "gateway_name": "MOCK_GATEWAY",
    }
    
    response = await client.post("/api/payments/initiate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["booking_id"] == 1
    assert data["user_id"] == 1
    assert float(data["amount"]) == 100.50
    assert data["status"] == "INITIATED"
    assert "payment_reference" in data
    assert "payment_url" in data


@pytest.mark.asyncio
async def test_initiate_payment_duplicate_booking(client: AsyncClient):
    """Test payment initiation with duplicate booking"""
    payload = {
        "booking_id": 2,
        "user_id": 1,
        "amount": 100.50,
        "payment_method": "CARD",
        "gateway_name": "MOCK_GATEWAY",
    }
    
    # First request should succeed
    response1 = await client.post("/api/payments/initiate", json=payload)
    assert response1.status_code == 200
    
    # Second request with same booking_id should fail
    response2 = await client.post("/api/payments/initiate", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_payment_by_id(client: AsyncClient):
    """Test get payment by ID"""
    # First create a payment
    payload = {
        "booking_id": 3,
        "user_id": 1,
        "amount": 100.50,
        "payment_method": "UPI",
    }
    
    create_response = await client.post("/api/payments/initiate", json=payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]
    
    # Get payment by ID
    response = await client.get(f"/api/payments/{payment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payment_id
    assert data["booking_id"] == 3


@pytest.mark.asyncio
async def test_get_payment_by_booking_id(client: AsyncClient):
    """Test get payment by booking ID"""
    # First create a payment
    payload = {
        "booking_id": 4,
        "user_id": 1,
        "amount": 200.00,
        "payment_method": "NETBANKING",
    }
    
    create_response = await client.post("/api/payments/initiate", json=payload)
    assert create_response.status_code == 200
    
    # Get payment by booking ID
    response = await client.get("/api/payments/booking/4")
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == 4
    assert float(data["amount"]) == 200.00


@pytest.mark.asyncio
async def test_webhook_success(client: AsyncClient):
    """Test webhook with success status"""
    # First create a payment
    payload = {
        "booking_id": 5,
        "user_id": 1,
        "amount": 150.00,
        "payment_method": "WALLET",
    }
    
    create_response = await client.post("/api/payments/initiate", json=payload)
    assert create_response.status_code == 200
    payment_ref = create_response.json()["payment_reference"]
    
    # Send webhook with success
    webhook_payload = {
        "payment_reference": payment_ref,
        "gateway_transaction_id": "TXN123456",
        "status": "SUCCESS",
    }
    
    response = await client.post("/api/payments/webhook", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook processed successfully"
    
    # Verify payment status updated
    payment_response = await client.get(f"/api/payments/booking/5")
    assert payment_response.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_webhook_failed(client: AsyncClient):
    """Test webhook with failed status"""
    # First create a payment
    payload = {
        "booking_id": 6,
        "user_id": 1,
        "amount": 250.00,
        "payment_method": "CARD",
    }
    
    create_response = await client.post("/api/payments/initiate", json=payload)
    assert create_response.status_code == 200
    payment_ref = create_response.json()["payment_reference"]
    
    # Send webhook with failed status
    webhook_payload = {
        "payment_reference": payment_ref,
        "status": "FAILED",
        "failure_reason": "Insufficient funds",
    }
    
    response = await client.post("/api/payments/webhook", json=webhook_payload)
    assert response.status_code == 200
    
    # Verify payment status updated
    payment_response = await client.get(f"/api/payments/booking/6")
    assert payment_response.json()["status"] == "FAILED"


@pytest.mark.asyncio
async def test_get_payment_not_found(client: AsyncClient):
    """Test get payment that doesn't exist"""
    response = await client.get("/api/payments/99999")
    assert response.status_code == 404
