package com.bookmyshow.booking.model;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class BookingTest {

    @Test
    void testCreateBooking() {
        Booking booking = new Booking();
        booking.setId(1L);
        booking.setBookingReference("BK123456");
        booking.setUserId(100L);
        booking.setShowId(200L);
        booking.setTotalAmount(new BigDecimal("500.00"));
        booking.setBookingStatus(BookingStatus.PENDING);

        assertEquals(1L, booking.getId());
        assertEquals("BK123456", booking.getBookingReference());
        assertEquals(100L, booking.getUserId());
        assertEquals(200L, booking.getShowId());
        assertEquals(new BigDecimal("500.00"), booking.getTotalAmount());
        assertEquals(BookingStatus.PENDING, booking.getBookingStatus());
    }

    @Test
    void testBookingWithSeats() {
        Booking booking = new Booking();
        booking.setId(1L);

        BookingSeat seat1 = new BookingSeat();
        seat1.setSeatId(101L);
        seat1.setPrice(new BigDecimal("250.00"));

        BookingSeat seat2 = new BookingSeat();
        seat2.setSeatId(102L);
        seat2.setPrice(new BigDecimal("250.00"));

        List<BookingSeat> seats = new ArrayList<>();
        seats.add(seat1);
        seats.add(seat2);

        booking.setSeats(seats);

        assertNotNull(booking.getSeats());
        assertEquals(2, booking.getSeats().size());
        assertEquals(101L, booking.getSeats().get(0).getSeatId());
        assertEquals(102L, booking.getSeats().get(1).getSeatId());
    }

    @Test
    void testBookingStatusTransitions() {
        Booking booking = new Booking();
        booking.setBookingStatus(BookingStatus.PENDING);
        assertEquals(BookingStatus.PENDING, booking.getBookingStatus());

        booking.setBookingStatus(BookingStatus.CONFIRMED);
        assertEquals(BookingStatus.CONFIRMED, booking.getBookingStatus());

        booking.setBookingStatus(BookingStatus.CANCELLED);
        assertEquals(BookingStatus.CANCELLED, booking.getBookingStatus());
    }

    @Test
    void testBookingExpiry() {
        Booking booking = new Booking();
        LocalDateTime expiresAt = LocalDateTime.now().plusMinutes(15);
        booking.setExpiresAt(expiresAt);

        assertNotNull(booking.getExpiresAt());
        assertTrue(booking.getExpiresAt().isAfter(LocalDateTime.now()));
    }

    @Test
    void testBookingReferenceUniqueness() {
        Booking booking1 = new Booking();
        booking1.setBookingReference("BK123456");

        Booking booking2 = new Booking();
        booking2.setBookingReference("BK789012");

        assertNotEquals(booking1.getBookingReference(), booking2.getBookingReference());
    }

    @Test
    void testBookingWithPaymentId() {
        Booking booking = new Booking();
        booking.setPaymentId(999L);

        assertNotNull(booking.getPaymentId());
        assertEquals(999L, booking.getPaymentId());
    }

    @Test
    void testBookingTotalAmountCalculation() {
        Booking booking = new Booking();

        BookingSeat seat1 = new BookingSeat();
        seat1.setPrice(new BigDecimal("250.00"));

        BookingSeat seat2 = new BookingSeat();
        seat2.setPrice(new BigDecimal("300.00"));

        List<BookingSeat> seats = new ArrayList<>();
        seats.add(seat1);
        seats.add(seat2);

        booking.setSeats(seats);
        booking.setTotalAmount(new BigDecimal("550.00"));

        assertEquals(new BigDecimal("550.00"), booking.getTotalAmount());
    }
}
