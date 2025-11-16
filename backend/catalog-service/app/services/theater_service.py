import json
from typing import List, Optional
from redis.asyncio import Redis

from app.models import Theater
from app.repositories import TheaterRepository
from app.schemas import CreateTheaterRequest, CityResponse


class TheaterService:
    def __init__(self, repository: TheaterRepository, redis: Optional[Redis] = None):
        self.repository = repository
        self.redis = redis
        self.cache_ttl = 900  # 15 minutes

    async def create_theater(self, request: CreateTheaterRequest) -> Theater:
        theater = Theater(
            name=request.name,
            city=request.city,
            address=request.address,
            latitude=request.latitude,
            longitude=request.longitude,
            is_active=True,
        )
        
        created_theater = await self.repository.create(theater)
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"theaters:city:{request.city}")
            await self.redis.delete("theaters:all")
            await self.redis.delete("cities:all")
        
        return created_theater

    async def get_theater_by_id(self, theater_id: int) -> Optional[Theater]:
        cache_key = f"theater:{theater_id}"
        
        # Try to get from cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Get from database
        theater = await self.repository.get_by_id(theater_id)
        
        if theater and self.redis:
            # Cache the result
            theater_dict = {
                "id": theater.id,
                "name": theater.name,
                "city": theater.city,
                "address": theater.address,
                "latitude": theater.latitude,
                "longitude": theater.longitude,
                "is_active": theater.is_active,
            }
            await self.redis.setex(cache_key, self.cache_ttl, json.dumps(theater_dict))
        
        return theater

    async def get_all_theaters(self) -> List[Theater]:
        cache_key = "theaters:all"
        
        # Try to get from cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Get from database
        theaters = await self.repository.get_all()
        
        if self.redis:
            # Cache the result
            await self.redis.setex(cache_key, self.cache_ttl, json.dumps([
                {
                    "id": t.id,
                    "name": t.name,
                    "city": t.city,
                    "address": t.address,
                    "latitude": t.latitude,
                    "longitude": t.longitude,
                    "is_active": t.is_active,
                }
                for t in theaters
            ]))
        
        return theaters

    async def get_theaters_by_city(self, city: str) -> List[Theater]:
        cache_key = f"theaters:city:{city}"
        
        # Try to get from cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Get from database
        theaters = await self.repository.get_by_city(city)
        
        if self.redis:
            # Cache the result
            await self.redis.setex(cache_key, self.cache_ttl, json.dumps([
                {
                    "id": t.id,
                    "name": t.name,
                    "city": t.city,
                    "address": t.address,
                    "latitude": t.latitude,
                    "longitude": t.longitude,
                    "is_active": t.is_active,
                }
                for t in theaters
            ]))
        
        return theaters

    async def get_all_cities(self) -> List[CityResponse]:
        cache_key = "cities:all"
        
        # Try to get from cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                cities_data = json.loads(cached)
                return [CityResponse(**city) for city in cities_data]
        
        # Get from database
        cities = await self.repository.get_all_cities()
        cities_response = [
            CityResponse(name=city, theater_count=count) for city, count in cities
        ]
        
        if self.redis:
            # Cache the result
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps([{"name": c.name, "theater_count": c.theater_count} for c in cities_response])
            )
        
        return cities_response

    async def delete_theater(self, theater_id: int) -> None:
        theater = await self.repository.get_by_id(theater_id)
        if not theater:
            raise ValueError(f"Theater with id {theater_id} not found")
        
        city = theater.city
        await self.repository.delete(theater)
        
        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"theater:{theater_id}")
            await self.redis.delete(f"theaters:city:{city}")
            await self.redis.delete("theaters:all")
            await self.redis.delete("cities:all")
