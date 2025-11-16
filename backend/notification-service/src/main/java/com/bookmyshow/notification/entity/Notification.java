package com.bookmyshow.notification.entity;

import com.bookmyshow.common.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "notifications", indexes = {
        @Index(name = "idx_user_id", columnList = "user_id"),
        @Index(name = "idx_notification_type", columnList = "notification_type"),
        @Index(name = "idx_status", columnList = "status"),
        @Index(name = "idx_created_at", columnList = "created_at")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class Notification extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "notification_type", nullable = false, length = 50)
    private String notificationType;

    @Column(name = "channel", nullable = false, length = 20)
    private String channel;

    @Column(name = "recipient", length = 255)
    private String recipient;

    @Column(name = "subject", length = 500)
    private String subject;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "status", nullable = false, length = 20)
    private String status;

    @Column(name = "metadata", columnDefinition = "TEXT")
    private String metadata;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;
}
