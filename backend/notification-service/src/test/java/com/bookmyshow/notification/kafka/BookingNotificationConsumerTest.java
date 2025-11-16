package com.bookmyshow.notification.kafka;

import com.bookmyshow.notification.dto.BookingCancelledEvent;
import com.bookmyshow.notification.dto.BookingConfirmedEvent;
import com.bookmyshow.notification.entity.Notification;
import com.bookmyshow.notification.service.EmailService;
import com.bookmyshow.notification.service.NotificationService;
import com.bookmyshow.notification.service.SmsService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingNotificationConsumerTest {

    @Mock
    private EmailService emailService;

    @Mock
    private SmsService smsService;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private BookingNotificationConsumer bookingNotificationConsumer;

    private BookingConfirmedEvent bookingConfirmedEvent;
    private BookingCancelledEvent bookingCancelledEvent;

    @BeforeEach
    void setUp() {
        BookingConfirmedEvent.BookingData bookingData = BookingConfirmedEvent.BookingData.builder()
                .bookingId(123L)
                .bookingReference("BMS123456")
                .userId(1L)
                .userEmail("user@example.com")
                .userPhone("+919876543210")
                .movieTitle("Inception")
                .theaterName("PVR Phoenix")
                .showDateTime(LocalDateTime.of(2024, 11, 16, 18, 0))
                .seats(Arrays.asList("A1", "A2", "A3"))
                .totalAmount(new BigDecimal("900.00"))
                .build();

        bookingConfirmedEvent = BookingConfirmedEvent.builder()
                .eventId("evt_123")
                .eventType("BOOKING_CONFIRMED")
                .timestamp(LocalDateTime.now())
                .data(bookingData)
                .build();

        BookingCancelledEvent.BookingCancellationData cancellationData =
                BookingCancelledEvent.BookingCancellationData.builder()
                        .bookingId(123L)
                        .bookingReference("BMS123456")
                        .userId(1L)
                        .userEmail("user@example.com")
                        .userPhone("+919876543210")
                        .movieTitle("Inception")
                        .theaterName("PVR Phoenix")
                        .showDateTime(LocalDateTime.of(2024, 11, 16, 18, 0))
                        .seats(Arrays.asList("A1", "A2", "A3"))
                        .refundAmount(new BigDecimal("900.00"))
                        .cancellationReason("User requested")
                        .build();

        bookingCancelledEvent = BookingCancelledEvent.builder()
                .eventId("evt_456")
                .eventType("BOOKING_CANCELLED")
                .timestamp(LocalDateTime.now())
                .data(cancellationData)
                .build();
    }

    @Test
    void testHandleBookingConfirmed_Success() {
        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        bookingNotificationConsumer.handleBookingConfirmed(bookingConfirmedEvent);

        verify(emailService, times(1)).sendBookingConfirmationEmail(
                eq("user@example.com"),
                eq("BMS123456"),
                eq("Inception"),
                eq("PVR Phoenix"),
                any(LocalDateTime.class),
                eq(Arrays.asList("A1", "A2", "A3")),
                eq(new BigDecimal("900.00"))
        );

        verify(smsService, times(1)).sendBookingConfirmationSms(
                eq("+919876543210"),
                eq("BMS123456"),
                eq("Inception"),
                any(LocalDateTime.class)
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CONFIRMED"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CONFIRMED"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );
    }

    @Test
    void testHandleBookingConfirmed_EmailServiceFailure() {
        doThrow(new RuntimeException("Email service unavailable"))
                .when(emailService).sendBookingConfirmationEmail(
                        anyString(), anyString(), anyString(), anyString(),
                        any(LocalDateTime.class), any(), any(BigDecimal.class)
                );

        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        bookingNotificationConsumer.handleBookingConfirmed(bookingConfirmedEvent);

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CONFIRMED"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("FAILED"),
                anyString()
        );

        verify(smsService, times(1)).sendBookingConfirmationSms(
                anyString(), anyString(), anyString(), any(LocalDateTime.class)
        );
    }

    @Test
    void testHandleBookingCancelled_Success() {
        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        bookingNotificationConsumer.handleBookingCancelled(bookingCancelledEvent);

        verify(emailService, times(1)).sendBookingCancellationEmail(
                eq("user@example.com"),
                eq("BMS123456"),
                eq("Inception"),
                eq("PVR Phoenix"),
                any(LocalDateTime.class),
                eq(Arrays.asList("A1", "A2", "A3")),
                eq(new BigDecimal("900.00"))
        );

        verify(smsService, times(1)).sendBookingCancellationSms(
                eq("+919876543210"),
                eq("BMS123456"),
                eq("Inception"),
                eq(new BigDecimal("900.00"))
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CANCELLED"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CANCELLED"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );
    }

    @Test
    void testHandleBookingCancelled_SmsServiceFailure() {
        doThrow(new RuntimeException("SMS service unavailable"))
                .when(smsService).sendBookingCancellationSms(
                        anyString(), anyString(), anyString(), any(BigDecimal.class)
                );

        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        bookingNotificationConsumer.handleBookingCancelled(bookingCancelledEvent);

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("BOOKING_CANCELLED"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("FAILED"),
                anyString()
        );

        verify(emailService, times(1)).sendBookingCancellationEmail(
                anyString(), anyString(), anyString(), anyString(),
                any(LocalDateTime.class), any(), any(BigDecimal.class)
        );
    }

    @Test
    void testHandleBookingConfirmed_NullEvent() {
        bookingNotificationConsumer.handleBookingConfirmed(null);

        verify(emailService, never()).sendBookingConfirmationEmail(
                anyString(), anyString(), anyString(), anyString(),
                any(), any(), any()
        );
        verify(smsService, never()).sendBookingConfirmationSms(
                anyString(), anyString(), anyString(), any()
        );
    }

    @Test
    void testHandleBookingCancelled_NullEvent() {
        bookingNotificationConsumer.handleBookingCancelled(null);

        verify(emailService, never()).sendBookingCancellationEmail(
                anyString(), anyString(), anyString(), anyString(),
                any(), any(), any()
        );
        verify(smsService, never()).sendBookingCancellationSms(
                anyString(), anyString(), anyString(), any()
        );
    }
}
