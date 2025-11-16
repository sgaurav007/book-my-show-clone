package com.bookmyshow.booking.kafka;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class BookingConfirmedEvent {
    private Long bookingId;
    private String bookingReference;
    private Long userId;
    private Long showId;
    private Long paymentId;
    private BigDecimal totalAmount;
    private LocalDateTime confirmedAt;
}
