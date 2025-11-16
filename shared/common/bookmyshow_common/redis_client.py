"""Redis client utilities with distributed locking support."""

import asyncio
from typing import Optional
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from redis.asyncio import Redis


class RedisClient:
    """Async Redis client wrapper with utilities."""

    def __init__(self, redis_url: str):
        """Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.client: Optional[Redis] = None

    async def connect(self):
        """Connect to Redis."""
        self.client = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis.
        
        Args:
            key: Key to get
            
        Returns:
            Value or None if not found
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
    ) -> bool:
        """Set value in Redis.
        
        Args:
            key: Key to set
            value: Value to set
            ex: Expiration time in seconds
            
        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        """Delete key from Redis.
        
        Args:
            key: Key to delete
            
        Returns:
            Number of keys deleted
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.exists(key) > 0

    @asynccontextmanager
    async def distributed_lock(
        self,
        lock_key: str,
        timeout: int = 10,
        blocking_timeout: int = 5,
    ):
        """Acquire distributed lock using Redis.
        
        Args:
            lock_key: Lock key name
            timeout: Lock timeout in seconds
            blocking_timeout: Time to wait for lock acquisition
            
        Yields:
            Lock object
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        lock = self.client.lock(
            lock_key,
            timeout=timeout,
            blocking_timeout=blocking_timeout,
        )
        
        acquired = await lock.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock: {lock_key}")
        
        try:
            yield lock
        finally:
            try:
                await lock.release()
            except Exception:
                pass  # Lock may have already expired


class RedisCacheManager:
    """Cache manager using Redis."""

    def __init__(self, redis_client: RedisClient, prefix: str = "cache"):
        """Initialize cache manager.
        
        Args:
            redis_client: Redis client instance
            prefix: Key prefix for cache entries
        """
        self.redis_client = redis_client
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[str]:
        """Get cached value."""
        return await self.redis_client.get(self._make_key(key))

    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        return await self.redis_client.set(self._make_key(key), value, ex=ttl)

    async def delete(self, key: str) -> int:
        """Delete cached value."""
        return await self.redis_client.delete(self._make_key(key))

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if not self.redis_client.client:
            raise RuntimeError("Redis client not connected")
        
        full_pattern = self._make_key(pattern)
        keys = []
        async for key in self.redis_client.client.scan_iter(match=full_pattern):
            keys.append(key)
        
        if keys:
            await self.redis_client.client.delete(*keys)
