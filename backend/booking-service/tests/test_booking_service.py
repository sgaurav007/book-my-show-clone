import pytest
from decimal import Decimal
from app.models.booking import BookingStatus
from app.services.booking_service import BookingService
from app.services.seat_lock_service import SeatLockService
from app.schemas.booking import LockSeatsRequest, SeatInfo
from common.exceptions import ResourceNotFoundException


@pytest.mark.asyncio
async def test_lock_seats_creates_booking(test_session, fake_redis, mock_kafka_producer):
    """Test that lock_seats creates a booking"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    request = LockSeatsRequest(
        user_id=1,
        show_id=1,
        seats=[
            SeatInfo(seat_id=1, seat_number="A1", price=Decimal("100.00")),
            SeatInfo(seat_id=2, seat_number="A2", price=Decimal("150.00"))
        ]
    )
    
    response = await service.lock_seats(request)
    
    assert response.user_id == 1
    assert response.show_id == 1
    assert response.total_amount == Decimal("250.00")
    assert response.booking_status == BookingStatus.PENDING
    assert len(response.seats) == 2
    assert response.booking_reference.startswith("BK")
    assert response.expires_at is not None


@pytest.mark.asyncio
async def test_confirm_booking(test_session, fake_redis, mock_kafka_producer):
    """Test confirming a pending booking"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    # Create booking
    request = LockSeatsRequest(
        user_id=1,
        show_id=1,
        seats=[SeatInfo(seat_id=1, seat_number="A1", price=Decimal("100.00"))]
    )
    booking_response = await service.lock_seats(request)
    
    # Confirm booking
    confirmed = await service.confirm_booking(booking_response.id, payment_id=999)
    
    assert confirmed.id == booking_response.id
    assert confirmed.booking_status == BookingStatus.CONFIRMED
    assert confirmed.payment_id == 999


@pytest.mark.asyncio
async def test_confirm_booking_not_found(test_session, fake_redis, mock_kafka_producer):
    """Test confirming a non-existent booking"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    with pytest.raises(ResourceNotFoundException):
        await service.confirm_booking(99999, payment_id=999)


@pytest.mark.asyncio
async def test_cancel_booking(test_session, fake_redis, mock_kafka_producer):
    """Test cancelling a booking"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    # Create booking
    request = LockSeatsRequest(
        user_id=1,
        show_id=1,
        seats=[SeatInfo(seat_id=1, seat_number="A1", price=Decimal("100.00"))]
    )
    booking_response = await service.lock_seats(request)
    
    # Cancel booking
    await service.cancel_booking(booking_response.id)
    
    # Verify booking is cancelled
    cancelled = await service.get_booking_by_id(booking_response.id)
    assert cancelled.booking_status == BookingStatus.CANCELLED
    
    # Verify seats are unlocked
    assert await seat_lock_service.is_locked(1, 1) is False


@pytest.mark.asyncio
async def test_get_booking_by_id(test_session, fake_redis, mock_kafka_producer):
    """Test getting a booking by ID"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    # Create booking
    request = LockSeatsRequest(
        user_id=1,
        show_id=1,
        seats=[SeatInfo(seat_id=1, seat_number="A1", price=Decimal("100.00"))]
    )
    created = await service.lock_seats(request)
    
    # Get booking
    retrieved = await service.get_booking_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.booking_reference == created.booking_reference


@pytest.mark.asyncio
async def test_get_bookings_by_user_id(test_session, fake_redis, mock_kafka_producer):
    """Test getting all bookings for a user"""
    seat_lock_service = SeatLockService(fake_redis)
    service = BookingService(test_session, seat_lock_service, mock_kafka_producer)
    
    # Create multiple bookings
    for i in range(3):
        request = LockSeatsRequest(
            user_id=1,
            show_id=i + 1,
            seats=[SeatInfo(seat_id=i + 1, seat_number=f"A{i + 1}", price=Decimal("100.00"))]
        )
        await service.lock_seats(request)
    
    # Get all bookings for user
    bookings = await service.get_bookings_by_user_id(1)
    
    assert len(bookings) == 3


@pytest.mark.asyncio
async def test_calculate_total_amount():
    """Test total amount calculation"""
    from app.services.booking_service import BookingService
    
    seats = [
        SeatInfo(seat_id=1, seat_number="A1", price=Decimal("100.00")),
        SeatInfo(seat_id=2, seat_number="A2", price=Decimal("150.00")),
        SeatInfo(seat_id=3, seat_number="A3", price=Decimal("200.00"))
    ]
    
    # Create a temporary service instance just to test the method
    service = BookingService(None, None, None)
    total = service._calculate_total_amount(seats)
    
    assert total == Decimal("450.00")


@pytest.mark.asyncio
async def test_generate_booking_reference():
    """Test booking reference generation"""
    from app.services.booking_service import BookingService
    
    service = BookingService(None, None, None)
    ref = service._generate_booking_reference()
    
    assert ref.startswith("BK")
    assert len(ref) == 14  # BK + 12 characters
