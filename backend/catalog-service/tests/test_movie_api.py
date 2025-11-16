import pytest
from datetime import date
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_movie_endpoint(client: AsyncClient):
    """Test creating a movie via API"""
    movie_data = {
        "title": "Test Movie",
        "description": "A test movie",
        "duration_minutes": 120,
        "language": "English",
        "release_date": "2024-01-01",
        "rating": "PG-13",
        "genre": ["Action", "Adventure"],
        "poster_url": "http://example.com/poster.jpg",
        "trailer_url": "http://example.com/trailer.mp4",
    }
    
    response = await client.post("/api/catalog/movies", json=movie_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Movie created successfully"
    assert data["data"]["title"] == "Test Movie"


@pytest.mark.asyncio
async def test_get_movie_by_id_endpoint(client: AsyncClient):
    """Test getting a movie by ID via API"""
    # Create a movie first
    movie_data = {
        "title": "Test Movie",
        "description": "A test movie",
        "duration_minutes": 120,
        "language": "English",
        "release_date": "2024-01-01",
        "rating": "PG-13",
        "genre": ["Action"],
    }
    
    create_response = await client.post("/api/catalog/movies", json=movie_data)
    created_movie = create_response.json()["data"]
    movie_id = created_movie["id"]
    
    # Get the movie
    response = await client.get(f"/api/catalog/movies/{movie_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == movie_id
    assert data["data"]["title"] == "Test Movie"


@pytest.mark.asyncio
async def test_get_all_movies_endpoint(client: AsyncClient):
    """Test getting all movies via API"""
    # Create multiple movies
    for i in range(3):
        movie_data = {
            "title": f"Movie {i}",
            "description": "Test movie",
            "duration_minutes": 120,
            "language": "English",
            "release_date": "2024-01-01",
            "genre": ["Action"],
        }
        await client.post("/api/catalog/movies", json=movie_data)
    
    # Get all movies
    response = await client.get("/api/catalog/movies?page=0&size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["content"]) == 3
    assert data["data"]["totalElements"] == 3


@pytest.mark.asyncio
async def test_update_movie_endpoint(client: AsyncClient):
    """Test updating a movie via API"""
    # Create a movie
    movie_data = {
        "title": "Original Title",
        "description": "Original description",
        "duration_minutes": 120,
        "language": "English",
        "release_date": "2024-01-01",
        "genre": ["Action"],
    }
    
    create_response = await client.post("/api/catalog/movies", json=movie_data)
    movie_id = create_response.json()["data"]["id"]
    
    # Update the movie
    update_data = {
        "title": "Updated Title",
        "duration_minutes": 150,
    }
    
    response = await client.put(f"/api/catalog/movies/{movie_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["duration_minutes"] == 150


@pytest.mark.asyncio
async def test_delete_movie_endpoint(client: AsyncClient):
    """Test deleting a movie via API"""
    # Create a movie
    movie_data = {
        "title": "Test Movie",
        "description": "Test movie",
        "duration_minutes": 120,
        "language": "English",
        "release_date": "2024-01-01",
        "genre": ["Action"],
    }
    
    create_response = await client.post("/api/catalog/movies", json=movie_data)
    movie_id = create_response.json()["data"]["id"]
    
    # Delete the movie
    response = await client.delete(f"/api/catalog/movies/{movie_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Try to get the deleted movie
    get_response = await client.get(f"/api/catalog/movies/{movie_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
