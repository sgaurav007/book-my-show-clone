import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.schemas.booking import (
    LockSeatsRequest,
    ConfirmBookingRequest,
    BookingResponse,
)
from app.services.booking_service import BookingService
from app.services.seat_lock_service import SeatLockService
from app.events.kafka_producer import KafkaProducer
from app.dependencies import get_db, get_redis, get_kafka_producer
from common.api_response import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def get_booking_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
) -> BookingService:
    """Dependency to create BookingService"""
    seat_lock_service = SeatLockService(redis)
    return BookingService(db, seat_lock_service, kafka_producer)


@router.post(
    "/lock-seats",
    response_model=ApiResponse[BookingResponse],
    status_code=status.HTTP_200_OK,
)
async def lock_seats(
    request: LockSeatsRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Lock seats and create a pending booking
    """
    logger.info(
        f"Lock seats request for user: {request.user_id} and show: {request.show_id}"
    )
    response = await booking_service.lock_seats(request)
    return ApiResponse.success("Seats locked successfully", response)


@router.post(
    "/{booking_id}/confirm",
    response_model=ApiResponse[BookingResponse],
    status_code=status.HTTP_200_OK,
)
async def confirm_booking(
    booking_id: int,
    request: ConfirmBookingRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Confirm a pending booking with payment
    """
    logger.info(
        f"Confirm booking request for booking: {booking_id} with payment: {request.payment_id}"
    )
    response = await booking_service.confirm_booking(booking_id, request.payment_id)
    return ApiResponse.success("Booking confirmed successfully", response)


@router.get(
    "/{booking_id}",
    response_model=ApiResponse[BookingResponse],
    status_code=status.HTTP_200_OK,
)
async def get_booking_by_id(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Get booking by ID
    """
    logger.info(f"Get booking request for id: {booking_id}")
    response = await booking_service.get_booking_by_id(booking_id)
    return ApiResponse.success(data=response)


@router.delete(
    "/{booking_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
)
async def cancel_booking(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Cancel a booking
    """
    logger.info(f"Cancel booking request for id: {booking_id}")
    await booking_service.cancel_booking(booking_id)
    return ApiResponse.success("Booking cancelled successfully", None)


@router.get(
    "/user/{user_id}",
    response_model=ApiResponse[List[BookingResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_bookings_by_user_id(
    user_id: int,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Get all bookings for a user
    """
    logger.info(f"Get bookings request for user: {user_id}")
    responses = await booking_service.get_bookings_by_user_id(user_id)
    return ApiResponse.success(data=responses)
