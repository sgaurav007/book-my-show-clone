package com.bookmyshow.booking.model;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

class BookingSeatTest {

    @Test
    void testCreateBookingSeat() {
        BookingSeat seat = new BookingSeat();
        seat.setId(1L);
        seat.setSeatId(100L);
        seat.setSeatNumber("A1");
        seat.setPrice(new BigDecimal("250.00"));

        assertEquals(1L, seat.getId());
        assertEquals(100L, seat.getSeatId());
        assertEquals("A1", seat.getSeatNumber());
        assertEquals(new BigDecimal("250.00"), seat.getPrice());
    }

    @Test
    void testBookingSeatWithBooking() {
        Booking booking = new Booking();
        booking.setId(1L);

        BookingSeat seat = new BookingSeat();
        seat.setBooking(booking);
        seat.setSeatId(100L);

        assertNotNull(seat.getBooking());
        assertEquals(1L, seat.getBooking().getId());
    }

    @Test
    void testBookingSeatEquality() {
        BookingSeat seat1 = new BookingSeat();
        seat1.setId(1L);
        seat1.setSeatId(100L);

        BookingSeat seat2 = new BookingSeat();
        seat2.setId(1L);
        seat2.setSeatId(100L);

        assertEquals(seat1.getId(), seat2.getId());
        assertEquals(seat1.getSeatId(), seat2.getSeatId());
    }

    @Test
    void testBookingSeatPriceNotNull() {
        BookingSeat seat = new BookingSeat();
        seat.setPrice(new BigDecimal("300.00"));

        assertNotNull(seat.getPrice());
        assertTrue(seat.getPrice().compareTo(BigDecimal.ZERO) > 0);
    }
}
