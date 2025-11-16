package com.bookmyshow.notification.entity;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class NotificationTest {

    @Test
    void testNotificationCreation() {
        Notification notification = new Notification();
        notification.setUserId(1L);
        notification.setNotificationType("BOOKING_CONFIRMED");
        notification.setChannel("EMAIL");
        notification.setRecipient("user@example.com");
        notification.setSubject("Booking Confirmation");
        notification.setContent("Your booking is confirmed");
        notification.setStatus("SUCCESS");

        assertEquals(1L, notification.getUserId());
        assertEquals("BOOKING_CONFIRMED", notification.getNotificationType());
        assertEquals("EMAIL", notification.getChannel());
        assertEquals("user@example.com", notification.getRecipient());
        assertEquals("Booking Confirmation", notification.getSubject());
        assertEquals("Your booking is confirmed", notification.getContent());
        assertEquals("SUCCESS", notification.getStatus());
    }

    @Test
    void testNotificationBuilder() {
        Notification notification = Notification.builder()
                .userId(2L)
                .notificationType("PAYMENT_SUCCESS")
                .channel("SMS")
                .recipient("+919876543210")
                .subject("Payment Received")
                .content("Payment of Rs. 900 received")
                .status("SUCCESS")
                .metadata("{\"paymentId\": 123}")
                .build();

        assertEquals(2L, notification.getUserId());
        assertEquals("PAYMENT_SUCCESS", notification.getNotificationType());
        assertEquals("SMS", notification.getChannel());
        assertEquals("+919876543210", notification.getRecipient());
        assertEquals("Payment Received", notification.getSubject());
        assertEquals("Payment of Rs. 900 received", notification.getContent());
        assertEquals("SUCCESS", notification.getStatus());
        assertEquals("{\"paymentId\": 123}", notification.getMetadata());
    }

    @Test
    void testNotificationEquality() {
        Notification notification1 = Notification.builder()
                .userId(1L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .status("SUCCESS")
                .build();

        Notification notification2 = Notification.builder()
                .userId(1L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .status("SUCCESS")
                .build();

        assertEquals(notification1, notification2);
    }

    @Test
    void testNotificationToString() {
        Notification notification = Notification.builder()
                .userId(1L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .recipient("user@example.com")
                .status("SUCCESS")
                .build();

        String notificationString = notification.toString();
        assertTrue(notificationString.contains("userId=1"));
        assertTrue(notificationString.contains("notificationType=BOOKING_CONFIRMED"));
        assertTrue(notificationString.contains("channel=EMAIL"));
    }

    @Test
    void testNotificationStatusTransition() {
        Notification notification = new Notification();
        notification.setStatus("PENDING");
        assertEquals("PENDING", notification.getStatus());

        notification.setStatus("SUCCESS");
        assertEquals("SUCCESS", notification.getStatus());

        notification.setStatus("FAILED");
        assertEquals("FAILED", notification.getStatus());
    }

    @Test
    void testNotificationWithMetadata() {
        String metadata = "{\"bookingId\": 123, \"showTime\": \"2024-11-16T18:00:00\"}";
        Notification notification = Notification.builder()
                .userId(1L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .metadata(metadata)
                .build();

        assertEquals(metadata, notification.getMetadata());
    }

    @Test
    void testNotificationNullableFields() {
        Notification notification = new Notification();
        notification.setUserId(1L);
        notification.setNotificationType("TEST");
        notification.setChannel("EMAIL");
        notification.setStatus("PENDING");

        assertNull(notification.getRecipient());
        assertNull(notification.getSubject());
        assertNull(notification.getContent());
        assertNull(notification.getMetadata());
        assertNull(notification.getErrorMessage());
    }
}
