package com.bookmyshow.notification.kafka;

import com.bookmyshow.notification.dto.BookingCancelledEvent;
import com.bookmyshow.notification.dto.BookingConfirmedEvent;
import com.bookmyshow.notification.service.EmailService;
import com.bookmyshow.notification.service.NotificationService;
import com.bookmyshow.notification.service.SmsService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class BookingNotificationConsumer {

    private final EmailService emailService;
    private final SmsService smsService;
    private final NotificationService notificationService;
    private final ObjectMapper objectMapper;

    @Autowired
    public BookingNotificationConsumer(EmailService emailService,
                                      SmsService smsService,
                                      NotificationService notificationService,
                                      ObjectMapper objectMapper) {
        this.emailService = emailService;
        this.smsService = smsService;
        this.notificationService = notificationService;
        this.objectMapper = objectMapper;
    }

    @KafkaListener(topics = "booking.confirmed", groupId = "notification-service")
    public void handleBookingConfirmed(BookingConfirmedEvent event) {
        if (event == null || event.getData() == null) {
            log.warn("Received null booking confirmed event");
            return;
        }

        BookingConfirmedEvent.BookingData data = event.getData();
        log.info("Received booking confirmed event: bookingId={}, reference={}",
                data.getBookingId(), data.getBookingReference());

        try {
            emailService.sendBookingConfirmationEmail(
                    data.getUserEmail(),
                    data.getBookingReference(),
                    data.getMovieTitle(),
                    data.getTheaterName(),
                    data.getShowDateTime(),
                    data.getSeats(),
                    data.getTotalAmount()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CONFIRMED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Booking Confirmation - " + data.getBookingReference(),
                    "Your booking for " + data.getMovieTitle() + " has been confirmed",
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Booking confirmation email sent successfully for booking: {}",
                    data.getBookingReference());

        } catch (Exception e) {
            log.error("Failed to send booking confirmation email for booking: {}",
                    data.getBookingReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CONFIRMED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Booking Confirmation - " + data.getBookingReference(),
                    "Your booking for " + data.getMovieTitle() + " has been confirmed",
                    "FAILED",
                    serializeEventData(data)
            );
        }

        try {
            smsService.sendBookingConfirmationSms(
                    data.getUserPhone(),
                    data.getBookingReference(),
                    data.getMovieTitle(),
                    data.getShowDateTime()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CONFIRMED",
                    "SMS",
                    data.getUserPhone(),
                    "Booking Confirmation",
                    "Booking confirmed for " + data.getMovieTitle(),
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Booking confirmation SMS sent successfully for booking: {}",
                    data.getBookingReference());

        } catch (Exception e) {
            log.error("Failed to send booking confirmation SMS for booking: {}",
                    data.getBookingReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CONFIRMED",
                    "SMS",
                    data.getUserPhone(),
                    "Booking Confirmation",
                    "Booking confirmed for " + data.getMovieTitle(),
                    "FAILED",
                    serializeEventData(data)
            );
        }
    }

    @KafkaListener(topics = "booking.cancelled", groupId = "notification-service")
    public void handleBookingCancelled(BookingCancelledEvent event) {
        if (event == null || event.getData() == null) {
            log.warn("Received null booking cancelled event");
            return;
        }

        BookingCancelledEvent.BookingCancellationData data = event.getData();
        log.info("Received booking cancelled event: bookingId={}, reference={}",
                data.getBookingId(), data.getBookingReference());

        try {
            emailService.sendBookingCancellationEmail(
                    data.getUserEmail(),
                    data.getBookingReference(),
                    data.getMovieTitle(),
                    data.getTheaterName(),
                    data.getShowDateTime(),
                    data.getSeats(),
                    data.getRefundAmount()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CANCELLED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Booking Cancelled - " + data.getBookingReference(),
                    "Your booking for " + data.getMovieTitle() + " has been cancelled",
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Booking cancellation email sent successfully for booking: {}",
                    data.getBookingReference());

        } catch (Exception e) {
            log.error("Failed to send booking cancellation email for booking: {}",
                    data.getBookingReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CANCELLED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Booking Cancelled - " + data.getBookingReference(),
                    "Your booking for " + data.getMovieTitle() + " has been cancelled",
                    "FAILED",
                    serializeEventData(data)
            );
        }

        try {
            smsService.sendBookingCancellationSms(
                    data.getUserPhone(),
                    data.getBookingReference(),
                    data.getMovieTitle(),
                    data.getRefundAmount()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CANCELLED",
                    "SMS",
                    data.getUserPhone(),
                    "Booking Cancelled",
                    "Booking cancelled for " + data.getMovieTitle(),
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Booking cancellation SMS sent successfully for booking: {}",
                    data.getBookingReference());

        } catch (Exception e) {
            log.error("Failed to send booking cancellation SMS for booking: {}",
                    data.getBookingReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "BOOKING_CANCELLED",
                    "SMS",
                    data.getUserPhone(),
                    "Booking Cancelled",
                    "Booking cancelled for " + data.getMovieTitle(),
                    "FAILED",
                    serializeEventData(data)
            );
        }
    }

    private String serializeEventData(Object data) {
        try {
            return objectMapper.writeValueAsString(data);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize event data", e);
            return "{}";
        }
    }
}
