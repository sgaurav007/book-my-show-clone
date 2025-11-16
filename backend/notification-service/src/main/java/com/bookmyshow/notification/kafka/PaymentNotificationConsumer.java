package com.bookmyshow.notification.kafka;

import com.bookmyshow.notification.dto.PaymentFailedEvent;
import com.bookmyshow.notification.dto.PaymentSuccessEvent;
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
public class PaymentNotificationConsumer {

    private final EmailService emailService;
    private final SmsService smsService;
    private final NotificationService notificationService;
    private final ObjectMapper objectMapper;

    @Autowired
    public PaymentNotificationConsumer(EmailService emailService,
                                      SmsService smsService,
                                      NotificationService notificationService,
                                      ObjectMapper objectMapper) {
        this.emailService = emailService;
        this.smsService = smsService;
        this.notificationService = notificationService;
        this.objectMapper = objectMapper;
    }

    @KafkaListener(topics = "payment.success", groupId = "notification-service")
    public void handlePaymentSuccess(PaymentSuccessEvent event) {
        if (event == null || event.getData() == null) {
            log.warn("Received null payment success event");
            return;
        }

        PaymentSuccessEvent.PaymentData data = event.getData();
        log.info("Received payment success event: paymentId={}, reference={}",
                data.getPaymentId(), data.getPaymentReference());

        try {
            emailService.sendPaymentReceiptEmail(
                    data.getUserEmail(),
                    data.getPaymentReference(),
                    data.getAmount(),
                    data.getCurrency(),
                    data.getPaymentMethod()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_SUCCESS",
                    "EMAIL",
                    data.getUserEmail(),
                    "Payment Receipt - " + data.getPaymentReference(),
                    "Payment of " + data.getAmount() + " " + data.getCurrency() + " received successfully",
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Payment receipt email sent successfully for payment: {}",
                    data.getPaymentReference());

        } catch (Exception e) {
            log.error("Failed to send payment receipt email for payment: {}",
                    data.getPaymentReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_SUCCESS",
                    "EMAIL",
                    data.getUserEmail(),
                    "Payment Receipt - " + data.getPaymentReference(),
                    "Payment of " + data.getAmount() + " " + data.getCurrency() + " received successfully",
                    "FAILED",
                    serializeEventData(data)
            );
        }

        try {
            smsService.sendPaymentSuccessSms(
                    data.getUserPhone(),
                    data.getPaymentReference(),
                    data.getAmount()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_SUCCESS",
                    "SMS",
                    data.getUserPhone(),
                    "Payment Received",
                    "Payment received successfully",
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Payment success SMS sent successfully for payment: {}",
                    data.getPaymentReference());

        } catch (Exception e) {
            log.error("Failed to send payment success SMS for payment: {}",
                    data.getPaymentReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_SUCCESS",
                    "SMS",
                    data.getUserPhone(),
                    "Payment Received",
                    "Payment received successfully",
                    "FAILED",
                    serializeEventData(data)
            );
        }
    }

    @KafkaListener(topics = "payment.failed", groupId = "notification-service")
    public void handlePaymentFailed(PaymentFailedEvent event) {
        if (event == null || event.getData() == null) {
            log.warn("Received null payment failed event");
            return;
        }

        PaymentFailedEvent.PaymentFailureData data = event.getData();
        log.info("Received payment failed event: paymentId={}, reference={}",
                data.getPaymentId(), data.getPaymentReference());

        try {
            emailService.sendPaymentFailureEmail(
                    data.getUserEmail(),
                    data.getPaymentReference(),
                    data.getAmount(),
                    data.getFailureReason()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_FAILED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Payment Failed - " + data.getPaymentReference(),
                    "Payment of " + data.getAmount() + " failed: " + data.getFailureReason(),
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Payment failure email sent successfully for payment: {}",
                    data.getPaymentReference());

        } catch (Exception e) {
            log.error("Failed to send payment failure email for payment: {}",
                    data.getPaymentReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_FAILED",
                    "EMAIL",
                    data.getUserEmail(),
                    "Payment Failed - " + data.getPaymentReference(),
                    "Payment of " + data.getAmount() + " failed: " + data.getFailureReason(),
                    "FAILED",
                    serializeEventData(data)
            );
        }

        try {
            smsService.sendPaymentFailureSms(
                    data.getUserPhone(),
                    data.getPaymentReference(),
                    data.getAmount(),
                    data.getFailureReason()
            );

            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_FAILED",
                    "SMS",
                    data.getUserPhone(),
                    "Payment Failed",
                    "Payment failed: " + data.getFailureReason(),
                    "SUCCESS",
                    serializeEventData(data)
            );
            log.info("Payment failure SMS sent successfully for payment: {}",
                    data.getPaymentReference());

        } catch (Exception e) {
            log.error("Failed to send payment failure SMS for payment: {}",
                    data.getPaymentReference(), e);
            notificationService.createNotificationWithMetadata(
                    data.getUserId(),
                    "PAYMENT_FAILED",
                    "SMS",
                    data.getUserPhone(),
                    "Payment Failed",
                    "Payment failed: " + data.getFailureReason(),
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
