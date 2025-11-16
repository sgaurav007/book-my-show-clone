import logging
from typing import List
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class SeatLockService:
    """Service for managing seat locks using Redis"""

    LOCK_KEY_PREFIX = "seat:lock"
    LOCK_DURATION_MINUTES = 15

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _get_lock_key(self, show_id: int, seat_id: int) -> str:
        """Generate Redis lock key for a seat"""
        return f"{self.LOCK_KEY_PREFIX}:{show_id}:{seat_id}"

    async def lock_seats(
        self, show_id: int, seat_ids: List[int], user_id: int
    ) -> bool:
        """
        Lock multiple seats for a show using Redis.
        Uses Lua script for atomic operation.
        
        Args:
            show_id: Show ID
            seat_ids: List of seat IDs to lock
            user_id: User ID requesting the lock
            
        Returns:
            True if all seats were successfully locked, False otherwise
        """
        if not seat_ids:
            logger.warning("Cannot lock empty seat list")
            return False

        lock_keys = [self._get_lock_key(show_id, seat_id) for seat_id in seat_ids]
        lock_duration_seconds = self.LOCK_DURATION_MINUTES * 60

        # Lua script for atomic locking
        # First check if any key exists, if so return 0
        # If all keys are available, set them all with expiry
        lua_script = """
        for i, key in ipairs(KEYS) do
            if redis.call('EXISTS', key) == 1 then
                return 0
            end
        end
        for i, key in ipairs(KEYS) do
            redis.call('SETEX', key, ARGV[1], ARGV[2])
        end
        return 1
        """

        try:
            result = await self.redis.eval(
                lua_script,
                len(lock_keys),
                *lock_keys,
                str(lock_duration_seconds),
                str(user_id)
            )

            locked = result == 1
            if locked:
                logger.info(
                    f"Successfully locked {len(seat_ids)} seats for show {show_id} by user {user_id}"
                )
            else:
                logger.warning(
                    f"Failed to lock seats for show {show_id} by user {user_id}"
                )

            return locked

        except Exception as e:
            logger.error(f"Error locking seats: {e}")
            return False

    async def unlock_seats(self, show_id: int, seat_ids: List[int]) -> None:
        """
        Unlock multiple seats for a show
        
        Args:
            show_id: Show ID
            seat_ids: List of seat IDs to unlock
        """
        if not seat_ids:
            return

        lock_keys = [self._get_lock_key(show_id, seat_id) for seat_id in seat_ids]

        try:
            await self.redis.delete(*lock_keys)
            logger.info(f"Unlocked {len(seat_ids)} seats for show {show_id}")
        except Exception as e:
            logger.error(f"Error unlocking seats: {e}")

    async def extend_lock(self, show_id: int, seat_id: int) -> bool:
        """
        Extend the lock duration for a seat
        
        Args:
            show_id: Show ID
            seat_id: Seat ID
            
        Returns:
            True if lock was extended, False otherwise
        """
        lock_key = self._get_lock_key(show_id, seat_id)
        lock_duration_seconds = self.LOCK_DURATION_MINUTES * 60

        try:
            result = await self.redis.expire(lock_key, lock_duration_seconds)
            return bool(result)
        except Exception as e:
            logger.error(f"Error extending lock: {e}")
            return False

    async def is_locked(self, show_id: int, seat_id: int) -> bool:
        """
        Check if a seat is locked
        
        Args:
            show_id: Show ID
            seat_id: Seat ID
            
        Returns:
            True if seat is locked, False otherwise
        """
        lock_key = self._get_lock_key(show_id, seat_id)

        try:
            exists = await self.redis.exists(lock_key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Error checking lock status: {e}")
            return False
