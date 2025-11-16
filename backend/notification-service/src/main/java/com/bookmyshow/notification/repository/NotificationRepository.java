package com.bookmyshow.notification.repository;

import com.bookmyshow.notification.entity.Notification;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface NotificationRepository extends JpaRepository<Notification, Long> {

    Page<Notification> findByUserId(Long userId, Pageable pageable);

    List<Notification> findByUserIdAndNotificationType(Long userId, String notificationType);

    Page<Notification> findByUserIdAndStatus(Long userId, String status, Pageable pageable);

    List<Notification> findByStatus(String status);

    List<Notification> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);

    long countByUserIdAndStatus(Long userId, String status);

    void deleteByUserId(Long userId);
}
