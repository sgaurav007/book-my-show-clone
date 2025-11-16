import logging
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking, BookingStatus
from app.models.booking_seat import BookingSeat
from app.repositories.booking_repository import BookingRepository
from app.services.seat_lock_service import SeatLockService
from app.events.kafka_producer import KafkaProducer
from app.schemas.booking import (
    LockSeatsRequest,
    BookingResponse,
    SeatResponse,
    BookingCreateEvent,
    BookingConfirmedEvent,
    BookingCancelledEvent,
)
from common.exceptions import ResourceNotFoundException

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing bookings"""

    BOOKING_EXPIRY_MINUTES = 15

    def __init__(
        self,
        session: AsyncSession,
        seat_lock_service: SeatLockService,
        kafka_producer: KafkaProducer,
    ):
        self.repository = BookingRepository(session)
        self.seat_lock_service = seat_lock_service
        self.kafka_producer = kafka_producer
        self.session = session

    async def lock_seats(self, request: LockSeatsRequest) -> BookingResponse:
        """
        Lock seats and create a pending booking
        
        Args:
            request: Lock seats request
            
        Returns:
            BookingResponse with pending booking
            
        Raises:
            RuntimeException: If seats cannot be locked
        """
        seat_ids = [seat.seat_id for seat in request.seats]

        # Try to lock seats in Redis
        locked = await self.seat_lock_service.lock_seats(
            request.show_id, seat_ids, request.user_id
        )

        if not locked:
            raise RuntimeError(
                "Unable to lock seats. Some seats may already be locked."
            )

        # Create booking
        booking = Booking(
            booking_reference=self._generate_booking_reference(),
            user_id=request.user_id,
            show_id=request.show_id,
            total_amount=self._calculate_total_amount(request.seats),
            booking_status=BookingStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(minutes=self.BOOKING_EXPIRY_MINUTES),
        )

        # Create booking seats
        booking_seats = [
            BookingSeat(
                booking=booking,
                seat_id=seat.seat_id,
                seat_number=seat.seat_number,
                price=seat.price,
            )
            for seat in request.seats
        ]
        booking.seats = booking_seats

        # Save booking
        saved_booking = await self.repository.create(booking)
        await self.session.commit()

        logger.info(
            f"Booking created: {saved_booking.booking_reference} for user: {request.user_id}"
        )

        # Publish Kafka event
        await self._publish_booking_created(saved_booking, seat_ids)

        return self._to_booking_response(saved_booking)

    async def confirm_booking(
        self, booking_id: int, payment_id: int
    ) -> BookingResponse:
        """
        Confirm a pending booking
        
        Args:
            booking_id: Booking ID
            payment_id: Payment ID
            
        Returns:
            BookingResponse with confirmed booking
            
        Raises:
            ResourceNotFoundException: If booking not found
            RuntimeException: If booking is not in PENDING status
        """
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Booking not found with id: {booking_id}")

        if booking.booking_status != BookingStatus.PENDING:
            raise RuntimeError(f"Booking is already {booking.booking_status.value}")

        booking.booking_status = BookingStatus.CONFIRMED
        booking.payment_id = payment_id
        booking.updated_at = datetime.utcnow()

        confirmed_booking = await self.repository.save(booking)
        await self.session.commit()

        logger.info(
            f"Booking confirmed: {confirmed_booking.booking_reference} with payment: {payment_id}"
        )

        # Publish Kafka event
        await self._publish_booking_confirmed(confirmed_booking)

        return self._to_booking_response(confirmed_booking)

    async def cancel_booking(self, booking_id: int) -> None:
        """
        Cancel a booking
        
        Args:
            booking_id: Booking ID
            
        Raises:
            ResourceNotFoundException: If booking not found
            RuntimeException: If booking is already cancelled or confirmed
        """
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Booking not found with id: {booking_id}")

        if booking.booking_status == BookingStatus.CANCELLED:
            raise RuntimeError("Booking is already cancelled")

        if booking.booking_status == BookingStatus.CONFIRMED:
            raise RuntimeError("Booking is already confirmed and cannot be cancelled")

        booking.booking_status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()

        await self.repository.save(booking)

        # Unlock seats
        seat_ids = [seat.seat_id for seat in booking.seats]
        await self.seat_lock_service.unlock_seats(booking.show_id, seat_ids)

        await self.session.commit()

        logger.info(f"Booking cancelled: {booking.booking_reference}")

        # Publish Kafka event
        await self._publish_booking_cancelled(booking, seat_ids)

    async def get_booking_by_id(self, booking_id: int) -> BookingResponse:
        """
        Get booking by ID
        
        Args:
            booking_id: Booking ID
            
        Returns:
            BookingResponse
            
        Raises:
            ResourceNotFoundException: If booking not found
        """
        booking = await self.repository.get_by_id(booking_id)
        if not booking:
            raise ResourceNotFoundException(f"Booking not found with id: {booking_id}")

        return self._to_booking_response(booking)

    async def get_bookings_by_user_id(self, user_id: int) -> List[BookingResponse]:
        """
        Get all bookings for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of BookingResponse
        """
        bookings = await self.repository.get_by_user_id(user_id)
        return [self._to_booking_response(booking) for booking in bookings]

    def _calculate_total_amount(self, seats) -> Decimal:
        """Calculate total amount from seats"""
        return sum((seat.price for seat in seats), Decimal("0"))

    def _generate_booking_reference(self) -> str:
        """Generate unique booking reference"""
        return "BK" + uuid.uuid4().hex[:12].upper()

    def _to_booking_response(self, booking: Booking) -> BookingResponse:
        """Convert Booking entity to BookingResponse"""
        seats = [
            SeatResponse(
                seat_id=seat.seat_id,
                seat_number=seat.seat_number,
                price=seat.price,
            )
            for seat in booking.seats
        ]

        return BookingResponse(
            id=booking.id,
            booking_reference=booking.booking_reference,
            user_id=booking.user_id,
            show_id=booking.show_id,
            total_amount=booking.total_amount,
            booking_status=booking.booking_status,
            payment_id=booking.payment_id,
            expires_at=booking.expires_at,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            seats=seats,
        )

    async def _publish_booking_created(
        self, booking: Booking, seat_ids: List[int]
    ) -> None:
        """Publish booking created event to Kafka"""
        event = BookingCreateEvent(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            user_id=booking.user_id,
            show_id=booking.show_id,
            total_amount=booking.total_amount,
            seat_ids=seat_ids,
            created_at=booking.created_at,
            expires_at=booking.expires_at,
        )
        await self.kafka_producer.publish_booking_created(event)

    async def _publish_booking_confirmed(self, booking: Booking) -> None:
        """Publish booking confirmed event to Kafka"""
        event = BookingConfirmedEvent(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            user_id=booking.user_id,
            show_id=booking.show_id,
            payment_id=booking.payment_id,
            total_amount=booking.total_amount,
            confirmed_at=datetime.utcnow(),
        )
        await self.kafka_producer.publish_booking_confirmed(event)

    async def _publish_booking_cancelled(
        self, booking: Booking, seat_ids: List[int]
    ) -> None:
        """Publish booking cancelled event to Kafka"""
        event = BookingCancelledEvent(
            booking_id=booking.id,
            booking_reference=booking.booking_reference,
            user_id=booking.user_id,
            show_id=booking.show_id,
            seat_ids=seat_ids,
            reason="User cancelled",
            cancelled_at=datetime.utcnow(),
        )
        await self.kafka_producer.publish_booking_cancelled(event)
