package com.bookmyshow.notification.integration;

import com.bookmyshow.notification.dto.BookingConfirmedEvent;
import com.bookmyshow.notification.dto.PaymentSuccessEvent;
import com.bookmyshow.notification.entity.Notification;
import com.bookmyshow.notification.repository.NotificationRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.test.context.EmbeddedKafka;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@EmbeddedKafka(
        partitions = 1,
        topics = {"booking.confirmed", "booking.cancelled", "payment.success", "payment.failed"},
        brokerProperties = {
                "listeners=PLAINTEXT://localhost:9092",
                "port=9092"
        }
)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
@ActiveProfiles("test")
class NotificationServiceIntegrationTest {

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    @Autowired
    private NotificationRepository notificationRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        notificationRepository.deleteAll();
    }

    @Test
    void testBookingConfirmedEventCreatesNotifications() {
        BookingConfirmedEvent.BookingData bookingData = BookingConfirmedEvent.BookingData.builder()
                .bookingId(123L)
                .bookingReference("BMS123456")
                .userId(1L)
                .userEmail("user@example.com")
                .userPhone("+919876543210")
                .movieTitle("Inception")
                .theaterName("PVR Phoenix")
                .showDateTime(LocalDateTime.of(2024, 11, 16, 18, 0))
                .seats(Arrays.asList("A1", "A2"))
                .totalAmount(new BigDecimal("600.00"))
                .build();

        BookingConfirmedEvent event = BookingConfirmedEvent.builder()
                .eventId("evt_123")
                .eventType("BOOKING_CONFIRMED")
                .timestamp(LocalDateTime.now())
                .data(bookingData)
                .build();

        kafkaTemplate.send("booking.confirmed", event);

        await().atMost(10, TimeUnit.SECONDS).untilAsserted(() -> {
            List<Notification> notifications = notificationRepository
                    .findByUserIdAndNotificationType(1L, "BOOKING_CONFIRMED");

            assertEquals(2, notifications.size());

            boolean hasEmail = notifications.stream()
                    .anyMatch(n -> "EMAIL".equals(n.getChannel()));
            boolean hasSms = notifications.stream()
                    .anyMatch(n -> "SMS".equals(n.getChannel()));

            assertTrue(hasEmail, "Should have email notification");
            assertTrue(hasSms, "Should have SMS notification");
        });
    }

    @Test
    void testPaymentSuccessEventCreatesNotifications() {
        PaymentSuccessEvent.PaymentData paymentData = PaymentSuccessEvent.PaymentData.builder()
                .paymentId(456L)
                .paymentReference("PAY123456")
                .bookingId(123L)
                .userId(2L)
                .userEmail("user2@example.com")
                .userPhone("+919876543211")
                .amount(new BigDecimal("900.00"))
                .currency("INR")
                .paymentMethod("CARD")
                .gatewayTransactionId("gateway_123")
                .build();

        PaymentSuccessEvent event = PaymentSuccessEvent.builder()
                .eventId("evt_456")
                .eventType("PAYMENT_SUCCESS")
                .timestamp(LocalDateTime.now())
                .data(paymentData)
                .build();

        kafkaTemplate.send("payment.success", event);

        await().atMost(10, TimeUnit.SECONDS).untilAsserted(() -> {
            List<Notification> notifications = notificationRepository
                    .findByUserIdAndNotificationType(2L, "PAYMENT_SUCCESS");

            assertEquals(2, notifications.size());

            boolean hasEmail = notifications.stream()
                    .anyMatch(n -> "EMAIL".equals(n.getChannel()) &&
                            "user2@example.com".equals(n.getRecipient()));
            boolean hasSms = notifications.stream()
                    .anyMatch(n -> "SMS".equals(n.getChannel()) &&
                            "+919876543211".equals(n.getRecipient()));

            assertTrue(hasEmail, "Should have email notification");
            assertTrue(hasSms, "Should have SMS notification");
        });
    }

    @Test
    void testNotificationStatusIsSuccessful() {
        BookingConfirmedEvent.BookingData bookingData = BookingConfirmedEvent.BookingData.builder()
                .bookingId(999L)
                .bookingReference("BMS999")
                .userId(3L)
                .userEmail("test@example.com")
                .userPhone("+919999999999")
                .movieTitle("Test Movie")
                .theaterName("Test Theater")
                .showDateTime(LocalDateTime.now())
                .seats(Arrays.asList("B1"))
                .totalAmount(new BigDecimal("300.00"))
                .build();

        BookingConfirmedEvent event = BookingConfirmedEvent.builder()
                .eventId("evt_999")
                .eventType("BOOKING_CONFIRMED")
                .timestamp(LocalDateTime.now())
                .data(bookingData)
                .build();

        kafkaTemplate.send("booking.confirmed", event);

        await().atMost(10, TimeUnit.SECONDS).untilAsserted(() -> {
            List<Notification> notifications = notificationRepository
                    .findByUserIdAndNotificationType(3L, "BOOKING_CONFIRMED");

            assertFalse(notifications.isEmpty());
            notifications.forEach(notification -> {
                assertEquals("SUCCESS", notification.getStatus());
                assertNotNull(notification.getCreatedAt());
                assertNotNull(notification.getUpdatedAt());
            });
        });
    }

    @Test
    void testNotificationMetadataContainsEventData() {
        PaymentSuccessEvent.PaymentData paymentData = PaymentSuccessEvent.PaymentData.builder()
                .paymentId(777L)
                .paymentReference("PAY777")
                .bookingId(777L)
                .userId(4L)
                .userEmail("metadata@example.com")
                .userPhone("+917777777777")
                .amount(new BigDecimal("1200.00"))
                .currency("INR")
                .paymentMethod("UPI")
                .gatewayTransactionId("gateway_777")
                .build();

        PaymentSuccessEvent event = PaymentSuccessEvent.builder()
                .eventId("evt_777")
                .eventType("PAYMENT_SUCCESS")
                .timestamp(LocalDateTime.now())
                .data(paymentData)
                .build();

        kafkaTemplate.send("payment.success", event);

        await().atMost(10, TimeUnit.SECONDS).untilAsserted(() -> {
            List<Notification> notifications = notificationRepository
                    .findByUserIdAndNotificationType(4L, "PAYMENT_SUCCESS");

            assertFalse(notifications.isEmpty());
            notifications.forEach(notification -> {
                assertNotNull(notification.getMetadata());
                assertTrue(notification.getMetadata().contains("PAY777"));
            });
        });
    }
}
