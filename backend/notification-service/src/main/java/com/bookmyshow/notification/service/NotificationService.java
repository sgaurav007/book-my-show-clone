package com.bookmyshow.notification.service;

import com.bookmyshow.notification.entity.Notification;
import com.bookmyshow.notification.repository.NotificationRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Slf4j
public class NotificationService {

    private final NotificationRepository notificationRepository;

    @Autowired
    public NotificationService(NotificationRepository notificationRepository) {
        this.notificationRepository = notificationRepository;
    }

    @Transactional
    public Notification saveNotification(Notification notification) {
        log.debug("Saving notification for user: {}", notification.getUserId());
        return notificationRepository.save(notification);
    }

    @Transactional
    public Notification createNotification(Long userId, String notificationType, String channel,
                                          String recipient, String subject, String content, String status) {
        Notification notification = Notification.builder()
                .userId(userId)
                .notificationType(notificationType)
                .channel(channel)
                .recipient(recipient)
                .subject(subject)
                .content(content)
                .status(status)
                .build();

        log.info("Creating notification for user {}: type={}, channel={}, status={}",
                userId, notificationType, channel, status);
        return notificationRepository.save(notification);
    }

    @Transactional
    public Notification createNotificationWithMetadata(Long userId, String notificationType, String channel,
                                                      String recipient, String subject, String content,
                                                      String status, String metadata) {
        Notification notification = Notification.builder()
                .userId(userId)
                .notificationType(notificationType)
                .channel(channel)
                .recipient(recipient)
                .subject(subject)
                .content(content)
                .status(status)
                .metadata(metadata)
                .build();

        log.info("Creating notification with metadata for user {}: type={}, channel={}, status={}",
                userId, notificationType, channel, status);
        return notificationRepository.save(notification);
    }

    @Transactional(readOnly = true)
    public Page<Notification> getUserNotifications(Long userId, Pageable pageable) {
        log.debug("Fetching notifications for user: {}", userId);
        return notificationRepository.findByUserId(userId, pageable);
    }

    @Transactional(readOnly = true)
    public List<Notification> getUserNotificationsByType(Long userId, String notificationType) {
        log.debug("Fetching notifications for user {} with type: {}", userId, notificationType);
        return notificationRepository.findByUserIdAndNotificationType(userId, notificationType);
    }

    @Transactional(readOnly = true)
    public Page<Notification> getUserNotificationsByStatus(Long userId, String status, Pageable pageable) {
        log.debug("Fetching notifications for user {} with status: {}", userId, status);
        return notificationRepository.findByUserIdAndStatus(userId, status, pageable);
    }

    @Transactional(readOnly = true)
    public List<Notification> getNotificationsByStatus(String status) {
        log.debug("Fetching all notifications with status: {}", status);
        return notificationRepository.findByStatus(status);
    }

    @Transactional(readOnly = true)
    public List<Notification> getNotificationsByDateRange(LocalDateTime start, LocalDateTime end) {
        log.debug("Fetching notifications between {} and {}", start, end);
        return notificationRepository.findByCreatedAtBetween(start, end);
    }

    @Transactional(readOnly = true)
    public long countUserNotificationsByStatus(Long userId, String status) {
        log.debug("Counting notifications for user {} with status: {}", userId, status);
        return notificationRepository.countByUserIdAndStatus(userId, status);
    }

    @Transactional
    public Notification markAsSuccess(Notification notification) {
        notification.setStatus("SUCCESS");
        log.info("Marking notification {} as SUCCESS", notification.getId());
        return notificationRepository.save(notification);
    }

    @Transactional
    public Notification markAsFailed(Notification notification, String errorMessage) {
        notification.setStatus("FAILED");
        notification.setErrorMessage(errorMessage);
        log.warn("Marking notification {} as FAILED: {}", notification.getId(), errorMessage);
        return notificationRepository.save(notification);
    }
}
