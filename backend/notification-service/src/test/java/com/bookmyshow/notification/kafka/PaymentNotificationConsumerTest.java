package com.bookmyshow.notification.kafka;

import com.bookmyshow.notification.dto.PaymentFailedEvent;
import com.bookmyshow.notification.dto.PaymentSuccessEvent;
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

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentNotificationConsumerTest {

    @Mock
    private EmailService emailService;

    @Mock
    private SmsService smsService;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private PaymentNotificationConsumer paymentNotificationConsumer;

    private PaymentSuccessEvent paymentSuccessEvent;
    private PaymentFailedEvent paymentFailedEvent;

    @BeforeEach
    void setUp() {
        PaymentSuccessEvent.PaymentData paymentData = PaymentSuccessEvent.PaymentData.builder()
                .paymentId(456L)
                .paymentReference("PAY123456")
                .bookingId(123L)
                .userId(1L)
                .userEmail("user@example.com")
                .userPhone("+919876543210")
                .amount(new BigDecimal("900.00"))
                .currency("INR")
                .paymentMethod("CARD")
                .gatewayTransactionId("gateway_123")
                .build();

        paymentSuccessEvent = PaymentSuccessEvent.builder()
                .eventId("evt_789")
                .eventType("PAYMENT_SUCCESS")
                .timestamp(LocalDateTime.now())
                .data(paymentData)
                .build();

        PaymentFailedEvent.PaymentFailureData paymentFailureData =
                PaymentFailedEvent.PaymentFailureData.builder()
                        .paymentId(789L)
                        .paymentReference("PAY789012")
                        .bookingId(123L)
                        .userId(1L)
                        .userEmail("user@example.com")
                        .userPhone("+919876543210")
                        .amount(new BigDecimal("900.00"))
                        .currency("INR")
                        .paymentMethod("CARD")
                        .failureReason("Insufficient funds")
                        .errorCode("ERR_001")
                        .build();

        paymentFailedEvent = PaymentFailedEvent.builder()
                .eventId("evt_101")
                .eventType("PAYMENT_FAILED")
                .timestamp(LocalDateTime.now())
                .data(paymentFailureData)
                .build();
    }

    @Test
    void testHandlePaymentSuccess_Success() {
        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        paymentNotificationConsumer.handlePaymentSuccess(paymentSuccessEvent);

        verify(emailService, times(1)).sendPaymentReceiptEmail(
                eq("user@example.com"),
                eq("PAY123456"),
                eq(new BigDecimal("900.00")),
                eq("INR"),
                eq("CARD")
        );

        verify(smsService, times(1)).sendPaymentSuccessSms(
                eq("+919876543210"),
                eq("PAY123456"),
                eq(new BigDecimal("900.00"))
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_SUCCESS"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_SUCCESS"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );
    }

    @Test
    void testHandlePaymentSuccess_EmailServiceFailure() {
        doThrow(new RuntimeException("Email service unavailable"))
                .when(emailService).sendPaymentReceiptEmail(
                        anyString(), anyString(), any(BigDecimal.class),
                        anyString(), anyString()
                );

        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        paymentNotificationConsumer.handlePaymentSuccess(paymentSuccessEvent);

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_SUCCESS"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("FAILED"),
                anyString()
        );

        verify(smsService, times(1)).sendPaymentSuccessSms(
                anyString(), anyString(), any(BigDecimal.class)
        );
    }

    @Test
    void testHandlePaymentFailed_Success() {
        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        paymentNotificationConsumer.handlePaymentFailed(paymentFailedEvent);

        verify(emailService, times(1)).sendPaymentFailureEmail(
                eq("user@example.com"),
                eq("PAY789012"),
                eq(new BigDecimal("900.00")),
                eq("Insufficient funds")
        );

        verify(smsService, times(1)).sendPaymentFailureSms(
                eq("+919876543210"),
                eq("PAY789012"),
                eq(new BigDecimal("900.00")),
                eq("Insufficient funds")
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_FAILED"),
                eq("EMAIL"),
                eq("user@example.com"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_FAILED"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("SUCCESS"),
                anyString()
        );
    }

    @Test
    void testHandlePaymentFailed_SmsServiceFailure() {
        doThrow(new RuntimeException("SMS service unavailable"))
                .when(smsService).sendPaymentFailureSms(
                        anyString(), anyString(), any(BigDecimal.class), anyString()
                );

        Notification mockNotification = Notification.builder().id(1L).build();
        when(notificationService.createNotificationWithMetadata(
                any(Long.class), anyString(), anyString(), anyString(),
                anyString(), anyString(), anyString(), anyString()
        )).thenReturn(mockNotification);

        paymentNotificationConsumer.handlePaymentFailed(paymentFailedEvent);

        verify(notificationService, times(1)).createNotificationWithMetadata(
                eq(1L),
                eq("PAYMENT_FAILED"),
                eq("SMS"),
                eq("+919876543210"),
                anyString(),
                anyString(),
                eq("FAILED"),
                anyString()
        );

        verify(emailService, times(1)).sendPaymentFailureEmail(
                anyString(), anyString(), any(BigDecimal.class), anyString()
        );
    }

    @Test
    void testHandlePaymentSuccess_NullEvent() {
        paymentNotificationConsumer.handlePaymentSuccess(null);

        verify(emailService, never()).sendPaymentReceiptEmail(
                anyString(), anyString(), any(), anyString(), anyString()
        );
        verify(smsService, never()).sendPaymentSuccessSms(
                anyString(), anyString(), any()
        );
    }

    @Test
    void testHandlePaymentFailed_NullEvent() {
        paymentNotificationConsumer.handlePaymentFailed(null);

        verify(emailService, never()).sendPaymentFailureEmail(
                anyString(), anyString(), any(), anyString()
        );
        verify(smsService, never()).sendPaymentFailureSms(
                anyString(), anyString(), any(), anyString()
        );
    }
}
