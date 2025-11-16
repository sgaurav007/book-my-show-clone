package com.bookmyshow.notification.service;

import com.bookmyshow.notification.entity.Notification;
import com.bookmyshow.notification.repository.NotificationRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {

    @Mock
    private NotificationRepository notificationRepository;

    @InjectMocks
    private NotificationService notificationService;

    private Notification testNotification;

    @BeforeEach
    void setUp() {
        testNotification = Notification.builder()
                .id(1L)
                .userId(100L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .recipient("user@example.com")
                .subject("Booking Confirmation")
                .content("Your booking is confirmed")
                .status("SUCCESS")
                .build();
    }

    @Test
    void testSaveNotification() {
        when(notificationRepository.save(any(Notification.class))).thenReturn(testNotification);

        Notification saved = notificationService.saveNotification(testNotification);

        assertNotNull(saved);
        assertEquals(1L, saved.getId());
        assertEquals("BOOKING_CONFIRMED", saved.getNotificationType());
        verify(notificationRepository, times(1)).save(testNotification);
    }

    @Test
    void testCreateNotification() {
        when(notificationRepository.save(any(Notification.class))).thenReturn(testNotification);

        Notification created = notificationService.createNotification(
                100L, "BOOKING_CONFIRMED", "EMAIL", "user@example.com",
                "Booking Confirmation", "Your booking is confirmed", "SUCCESS"
        );

        assertNotNull(created);
        assertEquals(100L, created.getUserId());
        assertEquals("BOOKING_CONFIRMED", created.getNotificationType());
        assertEquals("EMAIL", created.getChannel());
        assertEquals("SUCCESS", created.getStatus());
        verify(notificationRepository, times(1)).save(any(Notification.class));
    }

    @Test
    void testCreateNotificationWithMetadata() {
        String metadata = "{\"bookingId\": 123}";
        when(notificationRepository.save(any(Notification.class))).thenReturn(testNotification);

        Notification created = notificationService.createNotificationWithMetadata(
                100L, "BOOKING_CONFIRMED", "EMAIL", "user@example.com",
                "Booking Confirmation", "Your booking is confirmed", "SUCCESS", metadata
        );

        assertNotNull(created);
        verify(notificationRepository, times(1)).save(any(Notification.class));
    }

    @Test
    void testGetUserNotifications() {
        List<Notification> notifications = Arrays.asList(testNotification);
        Page<Notification> page = new PageImpl<>(notifications);
        Pageable pageable = PageRequest.of(0, 10);

        when(notificationRepository.findByUserId(100L, pageable)).thenReturn(page);

        Page<Notification> result = notificationService.getUserNotifications(100L, pageable);

        assertEquals(1, result.getTotalElements());
        assertEquals(testNotification, result.getContent().get(0));
        verify(notificationRepository, times(1)).findByUserId(100L, pageable);
    }

    @Test
    void testGetUserNotificationsByType() {
        List<Notification> notifications = Arrays.asList(testNotification);

        when(notificationRepository.findByUserIdAndNotificationType(100L, "BOOKING_CONFIRMED"))
                .thenReturn(notifications);

        List<Notification> result = notificationService.getUserNotificationsByType(100L, "BOOKING_CONFIRMED");

        assertEquals(1, result.size());
        assertEquals(testNotification, result.get(0));
        verify(notificationRepository, times(1))
                .findByUserIdAndNotificationType(100L, "BOOKING_CONFIRMED");
    }

    @Test
    void testGetUserNotificationsByStatus() {
        List<Notification> notifications = Arrays.asList(testNotification);
        Page<Notification> page = new PageImpl<>(notifications);
        Pageable pageable = PageRequest.of(0, 10);

        when(notificationRepository.findByUserIdAndStatus(100L, "SUCCESS", pageable))
                .thenReturn(page);

        Page<Notification> result = notificationService.getUserNotificationsByStatus(100L, "SUCCESS", pageable);

        assertEquals(1, result.getTotalElements());
        verify(notificationRepository, times(1))
                .findByUserIdAndStatus(100L, "SUCCESS", pageable);
    }

    @Test
    void testGetNotificationsByStatus() {
        List<Notification> notifications = Arrays.asList(testNotification);

        when(notificationRepository.findByStatus("SUCCESS")).thenReturn(notifications);

        List<Notification> result = notificationService.getNotificationsByStatus("SUCCESS");

        assertEquals(1, result.size());
        assertEquals(testNotification, result.get(0));
        verify(notificationRepository, times(1)).findByStatus("SUCCESS");
    }

    @Test
    void testGetNotificationsByDateRange() {
        LocalDateTime start = LocalDateTime.now().minusDays(1);
        LocalDateTime end = LocalDateTime.now();
        List<Notification> notifications = Arrays.asList(testNotification);

        when(notificationRepository.findByCreatedAtBetween(start, end)).thenReturn(notifications);

        List<Notification> result = notificationService.getNotificationsByDateRange(start, end);

        assertEquals(1, result.size());
        verify(notificationRepository, times(1)).findByCreatedAtBetween(start, end);
    }

    @Test
    void testCountUserNotificationsByStatus() {
        when(notificationRepository.countByUserIdAndStatus(100L, "SUCCESS")).thenReturn(5L);

        long count = notificationService.countUserNotificationsByStatus(100L, "SUCCESS");

        assertEquals(5L, count);
        verify(notificationRepository, times(1)).countByUserIdAndStatus(100L, "SUCCESS");
    }

    @Test
    void testMarkAsSuccess() {
        Notification notification = Notification.builder()
                .id(1L)
                .userId(100L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .status("PENDING")
                .build();

        when(notificationRepository.save(any(Notification.class))).thenReturn(notification);

        Notification updated = notificationService.markAsSuccess(notification);

        assertEquals("SUCCESS", updated.getStatus());
        verify(notificationRepository, times(1)).save(notification);
    }

    @Test
    void testMarkAsFailed() {
        Notification notification = Notification.builder()
                .id(1L)
                .userId(100L)
                .notificationType("BOOKING_CONFIRMED")
                .channel("EMAIL")
                .status("PENDING")
                .build();

        String errorMessage = "Failed to send email";
        when(notificationRepository.save(any(Notification.class))).thenReturn(notification);

        Notification updated = notificationService.markAsFailed(notification, errorMessage);

        assertEquals("FAILED", updated.getStatus());
        assertEquals(errorMessage, updated.getErrorMessage());
        verify(notificationRepository, times(1)).save(notification);
    }
}
