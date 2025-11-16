import pytest
from app.services.seat_lock_service import SeatLockService


@pytest.mark.asyncio
async def test_lock_seats_success(fake_redis):
    """Test successfully locking seats"""
    service = SeatLockService(fake_redis)
    
    result = await service.lock_seats(show_id=1, seat_ids=[1, 2, 3], user_id=100)
    
    assert result is True
    
    # Verify locks exist
    assert await service.is_locked(1, 1) is True
    assert await service.is_locked(1, 2) is True
    assert await service.is_locked(1, 3) is True


@pytest.mark.asyncio
async def test_lock_seats_already_locked(fake_redis):
    """Test locking seats that are already locked"""
    service = SeatLockService(fake_redis)
    
    # First lock
    result1 = await service.lock_seats(show_id=1, seat_ids=[1, 2], user_id=100)
    assert result1 is True
    
    # Try to lock again
    result2 = await service.lock_seats(show_id=1, seat_ids=[1, 2], user_id=200)
    assert result2 is False


@pytest.mark.asyncio
async def test_lock_seats_partial_conflict(fake_redis):
    """Test locking seats when some are already locked"""
    service = SeatLockService(fake_redis)
    
    # Lock seat 1
    result1 = await service.lock_seats(show_id=1, seat_ids=[1], user_id=100)
    assert result1 is True
    
    # Try to lock seats 1 and 2 (1 is already locked)
    result2 = await service.lock_seats(show_id=1, seat_ids=[1, 2], user_id=200)
    assert result2 is False
    
    # Seat 2 should not be locked
    assert await service.is_locked(1, 2) is False


@pytest.mark.asyncio
async def test_unlock_seats(fake_redis):
    """Test unlocking seats"""
    service = SeatLockService(fake_redis)
    
    # Lock seats
    await service.lock_seats(show_id=1, seat_ids=[1, 2], user_id=100)
    
    # Unlock seats
    await service.unlock_seats(show_id=1, seat_ids=[1, 2])
    
    # Verify locks are removed
    assert await service.is_locked(1, 1) is False
    assert await service.is_locked(1, 2) is False


@pytest.mark.asyncio
async def test_lock_key_generation(fake_redis):
    """Test lock key generation"""
    service = SeatLockService(fake_redis)
    
    key = service._get_lock_key(show_id=123, seat_id=456)
    assert key == "seat:lock:123:456"


@pytest.mark.asyncio
async def test_lock_empty_seat_list(fake_redis):
    """Test locking with empty seat list"""
    service = SeatLockService(fake_redis)
    
    result = await service.lock_seats(show_id=1, seat_ids=[], user_id=100)
    assert result is False


@pytest.mark.asyncio
async def test_extend_lock(fake_redis):
    """Test extending lock duration"""
    service = SeatLockService(fake_redis)
    
    # Lock a seat
    await service.lock_seats(show_id=1, seat_ids=[1], user_id=100)
    
    # Extend the lock
    result = await service.extend_lock(show_id=1, seat_id=1)
    assert result is True


@pytest.mark.asyncio
async def test_extend_lock_nonexistent(fake_redis):
    """Test extending a non-existent lock"""
    service = SeatLockService(fake_redis)
    
    # Try to extend a lock that doesn't exist
    result = await service.extend_lock(show_id=1, seat_id=1)
    assert result is False
