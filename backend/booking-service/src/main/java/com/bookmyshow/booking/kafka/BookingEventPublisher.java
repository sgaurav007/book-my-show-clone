package com.bookmyshow.booking.kafka;

import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Slf4j
public class BookingEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String BOOKING_CREATED_TOPIC = "booking-created";
    private static final String BOOKING_CONFIRMED_TOPIC = "booking-confirmed";
    private static final String BOOKING_CANCELLED_TOPIC = "booking-cancelled";

    public BookingEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishBookingCreated(Long bookingId, String bookingReference, Long userId,
                                      Long showId, BigDecimal totalAmount, List<Long> seatIds,
                                      LocalDateTime createdAt, LocalDateTime expiresAt) {
        BookingCreatedEvent event = new BookingCreatedEvent(
                bookingId, bookingReference, userId, showId, totalAmount, seatIds, createdAt, expiresAt
        );

        kafkaTemplate.send(BOOKING_CREATED_TOPIC, event);
        log.info("Published BookingCreatedEvent for booking: {}", bookingReference);
    }

    public void publishBookingConfirmed(Long bookingId, String bookingReference, Long userId,
                                        Long showId, Long paymentId, BigDecimal totalAmount,
                                        LocalDateTime confirmedAt) {
        BookingConfirmedEvent event = new BookingConfirmedEvent(
                bookingId, bookingReference, userId, showId, paymentId, totalAmount, confirmedAt
        );

        kafkaTemplate.send(BOOKING_CONFIRMED_TOPIC, event);
        log.info("Published BookingConfirmedEvent for booking: {}", bookingReference);
    }

    public void publishBookingCancelled(Long bookingId, String bookingReference, Long userId,
                                        Long showId, List<Long> seatIds, String reason,
                                        LocalDateTime cancelledAt) {
        BookingCancelledEvent event = new BookingCancelledEvent(
                bookingId, bookingReference, userId, showId, seatIds, reason, cancelledAt
        );

        kafkaTemplate.send(BOOKING_CANCELLED_TOPIC, event);
        log.info("Published BookingCancelledEvent for booking: {}", bookingReference);
    }
}
