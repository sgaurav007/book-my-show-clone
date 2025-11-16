package com.bookmyshow.booking.service;

import com.bookmyshow.booking.dto.BookingResponse;
import com.bookmyshow.booking.dto.LockSeatsRequest;
import com.bookmyshow.booking.dto.SeatInfo;
import com.bookmyshow.booking.dto.SeatResponse;
import com.bookmyshow.booking.kafka.BookingEventPublisher;
import com.bookmyshow.booking.model.Booking;
import com.bookmyshow.booking.model.BookingSeat;
import com.bookmyshow.booking.model.BookingStatus;
import com.bookmyshow.booking.repository.BookingRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@Slf4j
public class BookingService {

    private final BookingRepository bookingRepository;
    private final SeatLockService seatLockService;
    private final BookingEventPublisher eventPublisher;

    private static final int BOOKING_EXPIRY_MINUTES = 15;

    public BookingService(BookingRepository bookingRepository,
                         SeatLockService seatLockService,
                         BookingEventPublisher eventPublisher) {
        this.bookingRepository = bookingRepository;
        this.seatLockService = seatLockService;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public BookingResponse lockSeats(LockSeatsRequest request) {
        List<Long> seatIds = request.getSeats().stream()
                .map(SeatInfo::getSeatId)
                .collect(Collectors.toList());

        boolean locked = seatLockService.lockSeats(request.getShowId(), seatIds, request.getUserId());

        if (!locked) {
            throw new RuntimeException("Unable to lock seats. Some seats may already be locked.");
        }

        Booking booking = new Booking();
        booking.setBookingReference(generateBookingReference());
        booking.setUserId(request.getUserId());
        booking.setShowId(request.getShowId());
        booking.setTotalAmount(calculateTotalAmount(request.getSeats()));
        booking.setBookingStatus(BookingStatus.PENDING);
        booking.setExpiresAt(LocalDateTime.now().plusMinutes(BOOKING_EXPIRY_MINUTES));

        List<BookingSeat> bookingSeats = request.getSeats().stream()
                .map(seatInfo -> {
                    BookingSeat bookingSeat = new BookingSeat();
                    bookingSeat.setBooking(booking);
                    bookingSeat.setSeatId(seatInfo.getSeatId());
                    bookingSeat.setSeatNumber(seatInfo.getSeatNumber());
                    bookingSeat.setPrice(seatInfo.getPrice());
                    return bookingSeat;
                })
                .collect(Collectors.toList());

        booking.setSeats(bookingSeats);

        Booking savedBooking = bookingRepository.save(booking);
        log.info("Booking created: {} for user: {}", savedBooking.getBookingReference(), request.getUserId());

        eventPublisher.publishBookingCreated(
                savedBooking.getId(),
                savedBooking.getBookingReference(),
                savedBooking.getUserId(),
                savedBooking.getShowId(),
                savedBooking.getTotalAmount(),
                seatIds,
                savedBooking.getCreatedAt(),
                savedBooking.getExpiresAt()
        );

        return toBookingResponse(savedBooking);
    }

    @Transactional
    public BookingResponse confirmBooking(Long bookingId, Long paymentId) {
        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Booking not found with id: " + bookingId));

        if (booking.getBookingStatus() != BookingStatus.PENDING) {
            throw new RuntimeException("Booking is already " + booking.getBookingStatus());
        }

        booking.setBookingStatus(BookingStatus.CONFIRMED);
        booking.setPaymentId(paymentId);

        Booking confirmedBooking = bookingRepository.save(booking);
        log.info("Booking confirmed: {} with payment: {}", confirmedBooking.getBookingReference(), paymentId);

        eventPublisher.publishBookingConfirmed(
                confirmedBooking.getId(),
                confirmedBooking.getBookingReference(),
                confirmedBooking.getUserId(),
                confirmedBooking.getShowId(),
                paymentId,
                confirmedBooking.getTotalAmount(),
                LocalDateTime.now()
        );

        return toBookingResponse(confirmedBooking);
    }

    @Transactional
    public void cancelBooking(Long bookingId) {
        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Booking not found with id: " + bookingId));

        if (booking.getBookingStatus() == BookingStatus.CANCELLED) {
            throw new RuntimeException("Booking is already cancelled");
        }

        if (booking.getBookingStatus() == BookingStatus.CONFIRMED) {
            throw new RuntimeException("Booking is already confirmed and cannot be cancelled");
        }

        booking.setBookingStatus(BookingStatus.CANCELLED);
        bookingRepository.save(booking);

        List<Long> seatIds = booking.getSeats().stream()
                .map(BookingSeat::getSeatId)
                .collect(Collectors.toList());

        seatLockService.unlockSeats(booking.getShowId(), seatIds);
        log.info("Booking cancelled: {}", booking.getBookingReference());

        eventPublisher.publishBookingCancelled(
                booking.getId(),
                booking.getBookingReference(),
                booking.getUserId(),
                booking.getShowId(),
                seatIds,
                "User cancelled",
                LocalDateTime.now()
        );
    }

    public BookingResponse getBookingById(Long bookingId) {
        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Booking not found with id: " + bookingId));

        return toBookingResponse(booking);
    }

    public List<BookingResponse> getBookingsByUserId(Long userId) {
        List<Booking> bookings = bookingRepository.findByUserId(userId);
        return bookings.stream()
                .map(this::toBookingResponse)
                .collect(Collectors.toList());
    }

    public BigDecimal calculateTotalAmount(List<SeatInfo> seats) {
        return seats.stream()
                .map(SeatInfo::getPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public String generateBookingReference() {
        return "BK" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase();
    }

    private BookingResponse toBookingResponse(Booking booking) {
        List<SeatResponse> seats = booking.getSeats().stream()
                .map(seat -> new SeatResponse(seat.getSeatId(), seat.getSeatNumber(), seat.getPrice()))
                .collect(Collectors.toList());

        return new BookingResponse(
                booking.getId(),
                booking.getBookingReference(),
                booking.getUserId(),
                booking.getShowId(),
                booking.getTotalAmount(),
                booking.getBookingStatus(),
                booking.getPaymentId(),
                booking.getExpiresAt(),
                booking.getCreatedAt(),
                booking.getUpdatedAt(),
                seats
        );
    }
}
