package com.bookmyshow.payment.kafka;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentEvent {
    private String eventId;
    private String eventType;
    private LocalDateTime timestamp;
    private PaymentEventData data;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PaymentEventData {
        private Long paymentId;
        private String paymentReference;
        private Long bookingId;
        private Long userId;
        private BigDecimal amount;
        private String currency;
        private String paymentMethod;
        private String gatewayTransactionId;
        private String status;
        private String failureReason;
    }
}
