package com.bookmyshow.notification.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentFailedEvent {

    @JsonProperty("eventId")
    private String eventId;

    @JsonProperty("eventType")
    private String eventType;

    @JsonProperty("timestamp")
    private LocalDateTime timestamp;

    @JsonProperty("data")
    private PaymentFailureData data;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PaymentFailureData {
        @JsonProperty("paymentId")
        private Long paymentId;

        @JsonProperty("paymentReference")
        private String paymentReference;

        @JsonProperty("bookingId")
        private Long bookingId;

        @JsonProperty("userId")
        private Long userId;

        @JsonProperty("userEmail")
        private String userEmail;

        @JsonProperty("userPhone")
        private String userPhone;

        @JsonProperty("amount")
        private BigDecimal amount;

        @JsonProperty("currency")
        private String currency;

        @JsonProperty("paymentMethod")
        private String paymentMethod;

        @JsonProperty("failureReason")
        private String failureReason;

        @JsonProperty("errorCode")
        private String errorCode;
    }
}
