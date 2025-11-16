import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_theater_endpoint(client: AsyncClient):
    """Test creating a theater via API"""
    theater_data = {
        "name": "Test Theater",
        "city": "New York",
        "address": "123 Main St",
        "latitude": 40.7128,
        "longitude": -74.0060,
    }
    
    response = await client.post("/api/catalog/theaters", json=theater_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Theater"
    assert data["data"]["city"] == "New York"


@pytest.mark.asyncio
async def test_get_theaters_by_city_endpoint(client: AsyncClient):
    """Test getting theaters by city via API"""
    # Create theaters in different cities
    cities = ["New York", "Los Angeles", "New York"]
    for city in cities:
        theater_data = {
            "name": f"Theater in {city}",
            "city": city,
            "address": "123 Main St",
        }
        await client.post("/api/catalog/theaters", json=theater_data)
    
    # Get theaters in New York
    response = await client.get("/api/catalog/theaters?city=New York")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_all_cities_endpoint(client: AsyncClient):
    """Test getting all cities via API"""
    # Create theaters in different cities
    cities = ["New York", "Los Angeles", "Chicago", "New York"]
    for city in cities:
        theater_data = {
            "name": f"Theater in {city}",
            "city": city,
            "address": "123 Main St",
        }
        await client.post("/api/catalog/theaters", json=theater_data)
    
    # Get all cities
    response = await client.get("/api/catalog/cities")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3  # 3 unique cities
    
    # Check city data
    city_names = [city["name"] for city in data["data"]]
    assert "New York" in city_names
    assert "Los Angeles" in city_names
    assert "Chicago" in city_names
