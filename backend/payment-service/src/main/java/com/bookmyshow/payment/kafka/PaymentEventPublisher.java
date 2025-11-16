package com.bookmyshow.payment.kafka;

import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.model.Refund;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.UUID;

@Component
@Slf4j
public class PaymentEventPublisher {

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    private static final String PAYMENT_INITIATED_TOPIC = "payment.initiated";
    private static final String PAYMENT_SUCCESS_TOPIC = "payment.success";
    private static final String PAYMENT_FAILED_TOPIC = "payment.failed";
    private static final String PAYMENT_REFUNDED_TOPIC = "payment.refunded";

    public void publishPaymentInitiated(Payment payment) {
        PaymentEvent event = createPaymentEvent("PAYMENT_INITIATED", payment);
        kafkaTemplate.send(PAYMENT_INITIATED_TOPIC, payment.getPaymentReference(), event);
        log.info("Published payment initiated event for: {}", payment.getPaymentReference());
    }

    public void publishPaymentSuccess(Payment payment) {
        PaymentEvent event = createPaymentEvent("PAYMENT_SUCCESS", payment);
        kafkaTemplate.send(PAYMENT_SUCCESS_TOPIC, payment.getPaymentReference(), event);
        log.info("Published payment success event for: {}", payment.getPaymentReference());
    }

    public void publishPaymentFailed(Payment payment) {
        PaymentEvent event = createPaymentEvent("PAYMENT_FAILED", payment);
        kafkaTemplate.send(PAYMENT_FAILED_TOPIC, payment.getPaymentReference(), event);
        log.info("Published payment failed event for: {}", payment.getPaymentReference());
    }

    public void publishRefundProcessed(Refund refund, Payment payment) {
        PaymentEvent.PaymentEventData data = new PaymentEvent.PaymentEventData(
                payment.getId(),
                payment.getPaymentReference(),
                payment.getBookingId(),
                payment.getUserId(),
                refund.getRefundAmount(),
                payment.getCurrency(),
                payment.getPaymentMethod() != null ? payment.getPaymentMethod().name() : null,
                payment.getGatewayTransactionId(),
                payment.getPaymentStatus().name(),
                null
        );

        PaymentEvent event = new PaymentEvent(
                UUID.randomUUID().toString(),
                "PAYMENT_REFUNDED",
                LocalDateTime.now(),
                data
        );

        kafkaTemplate.send(PAYMENT_REFUNDED_TOPIC, payment.getPaymentReference(), event);
        log.info("Published refund processed event for payment: {}", payment.getPaymentReference());
    }

    private PaymentEvent createPaymentEvent(String eventType, Payment payment) {
        PaymentEvent.PaymentEventData data = new PaymentEvent.PaymentEventData(
                payment.getId(),
                payment.getPaymentReference(),
                payment.getBookingId(),
                payment.getUserId(),
                payment.getAmount(),
                payment.getCurrency(),
                payment.getPaymentMethod() != null ? payment.getPaymentMethod().name() : null,
                payment.getGatewayTransactionId(),
                payment.getPaymentStatus().name(),
                payment.getFailureReason()
        );

        return new PaymentEvent(
                UUID.randomUUID().toString(),
                eventType,
                LocalDateTime.now(),
                data
        );
    }
}
