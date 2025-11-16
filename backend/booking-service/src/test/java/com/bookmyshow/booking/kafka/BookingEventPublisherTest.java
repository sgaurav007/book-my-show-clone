package com.bookmyshow.booking.kafka;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.core.KafkaTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingEventPublisherTest {

    @Mock
    private KafkaTemplate<String, Object> kafkaTemplate;

    @InjectMocks
    private BookingEventPublisher bookingEventPublisher;

    @Captor
    private ArgumentCaptor<BookingCreatedEvent> createdEventCaptor;

    @Captor
    private ArgumentCaptor<BookingConfirmedEvent> confirmedEventCaptor;

    @Captor
    private ArgumentCaptor<BookingCancelledEvent> cancelledEventCaptor;

    @BeforeEach
    void setUp() {
        bookingEventPublisher = new BookingEventPublisher(kafkaTemplate);
    }

    @Test
    void testPublishBookingCreatedEvent() {
        Long bookingId = 1L;
        String bookingReference = "BK123456";
        Long userId = 100L;
        Long showId = 200L;
        BigDecimal totalAmount = new BigDecimal("500.00");
        List<Long> seatIds = Arrays.asList(1L, 2L);
        LocalDateTime createdAt = LocalDateTime.now();
        LocalDateTime expiresAt = createdAt.plusMinutes(15);

        bookingEventPublisher.publishBookingCreated(
                bookingId, bookingReference, userId, showId, totalAmount, seatIds, createdAt, expiresAt
        );

        verify(kafkaTemplate, times(1)).send(
                eq("booking-created"),
                createdEventCaptor.capture()
        );

        BookingCreatedEvent event = createdEventCaptor.getValue();
        assertEquals(bookingId, event.getBookingId());
        assertEquals(bookingReference, event.getBookingReference());
        assertEquals(userId, event.getUserId());
        assertEquals(showId, event.getShowId());
        assertEquals(totalAmount, event.getTotalAmount());
        assertEquals(seatIds, event.getSeatIds());
        assertEquals(createdAt, event.getCreatedAt());
        assertEquals(expiresAt, event.getExpiresAt());
    }

    @Test
    void testPublishBookingConfirmedEvent() {
        Long bookingId = 1L;
        String bookingReference = "BK123456";
        Long userId = 100L;
        Long showId = 200L;
        Long paymentId = 999L;
        BigDecimal totalAmount = new BigDecimal("500.00");
        LocalDateTime confirmedAt = LocalDateTime.now();

        bookingEventPublisher.publishBookingConfirmed(
                bookingId, bookingReference, userId, showId, paymentId, totalAmount, confirmedAt
        );

        verify(kafkaTemplate, times(1)).send(
                eq("booking-confirmed"),
                confirmedEventCaptor.capture()
        );

        BookingConfirmedEvent event = confirmedEventCaptor.getValue();
        assertEquals(bookingId, event.getBookingId());
        assertEquals(bookingReference, event.getBookingReference());
        assertEquals(userId, event.getUserId());
        assertEquals(showId, event.getShowId());
        assertEquals(paymentId, event.getPaymentId());
        assertEquals(totalAmount, event.getTotalAmount());
        assertEquals(confirmedAt, event.getConfirmedAt());
    }

    @Test
    void testPublishBookingCancelledEvent() {
        Long bookingId = 1L;
        String bookingReference = "BK123456";
        Long userId = 100L;
        Long showId = 200L;
        List<Long> seatIds = Arrays.asList(1L, 2L);
        String reason = "User cancelled";
        LocalDateTime cancelledAt = LocalDateTime.now();

        bookingEventPublisher.publishBookingCancelled(
                bookingId, bookingReference, userId, showId, seatIds, reason, cancelledAt
        );

        verify(kafkaTemplate, times(1)).send(
                eq("booking-cancelled"),
                cancelledEventCaptor.capture()
        );

        BookingCancelledEvent event = cancelledEventCaptor.getValue();
        assertEquals(bookingId, event.getBookingId());
        assertEquals(bookingReference, event.getBookingReference());
        assertEquals(userId, event.getUserId());
        assertEquals(showId, event.getShowId());
        assertEquals(seatIds, event.getSeatIds());
        assertEquals(reason, event.getReason());
        assertEquals(cancelledAt, event.getCancelledAt());
    }

    @Test
    void testPublishBookingCreatedEventWithNullValues() {
        bookingEventPublisher.publishBookingCreated(
                null, null, null, null, null, null, null, null
        );

        verify(kafkaTemplate, times(1)).send(
                eq("booking-created"),
                any(BookingCreatedEvent.class)
        );
    }
}
