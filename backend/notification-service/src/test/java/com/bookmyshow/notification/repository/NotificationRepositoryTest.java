package com.bookmyshow.notification.repository;

import com.bookmyshow.notification.entity.Notification;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@ActiveProfiles("test")
class NotificationRepositoryTest {

    @Autowired
    private NotificationRepository notificationRepository;

    @BeforeEach
    void setUp() {
        notificationRepository.deleteAll();
    }

    @Test
    void testSaveNotification() {
        Notification notification = Notification.builder()
                .userId(1L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .recipient("user@example.com")
                .subject("Booking Confirmation")
                .content("Your booking is confirmed")
                .status("SUCCESS")
                .build();

        Notification saved = notificationRepository.save(notification);

        assertNotNull(saved.getId());
        assertEquals(1L, saved.getUserId());
        assertEquals("BOOKING_CONFIRMED", saved.getNotificationType());
        assertEquals("SUCCESS", saved.getStatus());
    }

    @Test
    void testFindByUserId() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(1L, "PAYMENT_SUCCESS", "SUCCESS");
        Notification notification3 = createNotification(2L, "BOOKING_CONFIRMED", "SUCCESS");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        Page<Notification> userNotifications = notificationRepository.findByUserId(1L, PageRequest.of(0, 10));

        assertEquals(2, userNotifications.getTotalElements());
        assertTrue(userNotifications.getContent().stream()
                .allMatch(n -> n.getUserId().equals(1L)));
    }

    @Test
    void testFindByUserIdAndNotificationType() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(1L, "BOOKING_CONFIRMED", "FAILED");
        Notification notification3 = createNotification(1L, "PAYMENT_SUCCESS", "SUCCESS");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        List<Notification> bookingNotifications = notificationRepository
                .findByUserIdAndNotificationType(1L, "BOOKING_CONFIRMED");

        assertEquals(2, bookingNotifications.size());
        assertTrue(bookingNotifications.stream()
                .allMatch(n -> n.getNotificationType().equals("BOOKING_CONFIRMED")));
    }

    @Test
    void testFindByUserIdAndStatus() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(1L, "PAYMENT_SUCCESS", "FAILED");
        Notification notification3 = createNotification(1L, "BOOKING_CANCELLED", "SUCCESS");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        Page<Notification> successNotifications = notificationRepository
                .findByUserIdAndStatus(1L, "SUCCESS", PageRequest.of(0, 10));

        assertEquals(2, successNotifications.getTotalElements());
        assertTrue(successNotifications.getContent().stream()
                .allMatch(n -> n.getStatus().equals("SUCCESS")));
    }

    @Test
    void testFindByStatus() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(2L, "PAYMENT_SUCCESS", "FAILED");
        Notification notification3 = createNotification(3L, "BOOKING_CANCELLED", "SUCCESS");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        List<Notification> failedNotifications = notificationRepository.findByStatus("FAILED");

        assertEquals(1, failedNotifications.size());
        assertEquals("FAILED", failedNotifications.get(0).getStatus());
    }

    @Test
    void testFindByCreatedAtBetween() throws InterruptedException {
        LocalDateTime start = LocalDateTime.now().minusMinutes(1);

        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        notificationRepository.save(notification1);

        Thread.sleep(100);

        Notification notification2 = createNotification(2L, "PAYMENT_SUCCESS", "SUCCESS");
        notificationRepository.save(notification2);

        LocalDateTime end = LocalDateTime.now().plusMinutes(1);

        List<Notification> notifications = notificationRepository
                .findByCreatedAtBetween(start, end);

        assertEquals(2, notifications.size());
    }

    @Test
    void testCountByUserIdAndStatus() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(1L, "PAYMENT_SUCCESS", "SUCCESS");
        Notification notification3 = createNotification(1L, "BOOKING_CANCELLED", "FAILED");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        long successCount = notificationRepository.countByUserIdAndStatus(1L, "SUCCESS");
        long failedCount = notificationRepository.countByUserIdAndStatus(1L, "FAILED");

        assertEquals(2, successCount);
        assertEquals(1, failedCount);
    }

    @Test
    void testDeleteByUserId() {
        Notification notification1 = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification notification2 = createNotification(1L, "PAYMENT_SUCCESS", "SUCCESS");
        Notification notification3 = createNotification(2L, "BOOKING_CONFIRMED", "SUCCESS");

        notificationRepository.save(notification1);
        notificationRepository.save(notification2);
        notificationRepository.save(notification3);

        notificationRepository.deleteByUserId(1L);

        Page<Notification> user1Notifications = notificationRepository
                .findByUserId(1L, PageRequest.of(0, 10));
        Page<Notification> user2Notifications = notificationRepository
                .findByUserId(2L, PageRequest.of(0, 10));

        assertEquals(0, user1Notifications.getTotalElements());
        assertEquals(1, user2Notifications.getTotalElements());
    }

    @Test
    void testTimestampFields() {
        Notification notification = createNotification(1L, "BOOKING_CONFIRMED", "SUCCESS");
        Notification saved = notificationRepository.save(notification);

        assertNotNull(saved.getCreatedAt());
        assertNotNull(saved.getUpdatedAt());
        assertEquals(saved.getCreatedAt(), saved.getUpdatedAt());

        saved.setStatus("FAILED");
        Notification updated = notificationRepository.save(saved);

        assertNotNull(updated.getUpdatedAt());
        assertTrue(updated.getUpdatedAt().isAfter(updated.getCreatedAt()) ||
                updated.getUpdatedAt().isEqual(updated.getCreatedAt()));
    }

    private Notification createNotification(Long userId, String type, String status) {
        return Notification.builder()
                .userId(userId)
                .notificationType(type)
                .channel("EMAIL")
                .recipient("user" + userId + "@example.com")
                .subject("Test Subject")
                .content("Test Content")
                .status(status)
                .build();
    }
}
