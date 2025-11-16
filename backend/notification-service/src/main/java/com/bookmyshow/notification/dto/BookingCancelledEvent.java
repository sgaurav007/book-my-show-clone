package com.bookmyshow.notification.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BookingCancelledEvent {

    @JsonProperty("eventId")
    private String eventId;

    @JsonProperty("eventType")
    private String eventType;

    @JsonProperty("timestamp")
    private LocalDateTime timestamp;

    @JsonProperty("data")
    private BookingCancellationData data;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class BookingCancellationData {
        @JsonProperty("bookingId")
        private Long bookingId;

        @JsonProperty("bookingReference")
        private String bookingReference;

        @JsonProperty("userId")
        private Long userId;

        @JsonProperty("userEmail")
        private String userEmail;

        @JsonProperty("userPhone")
        private String userPhone;

        @JsonProperty("movieTitle")
        private String movieTitle;

        @JsonProperty("theaterName")
        private String theaterName;

        @JsonProperty("showDateTime")
        private LocalDateTime showDateTime;

        @JsonProperty("seats")
        private List<String> seats;

        @JsonProperty("refundAmount")
        private BigDecimal refundAmount;

        @JsonProperty("cancellationReason")
        private String cancellationReason;
    }
}
