package com.bookmyshow.booking.kafka;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class BookingCreatedEvent {
    private Long bookingId;
    private String bookingReference;
    private Long userId;
    private Long showId;
    private BigDecimal totalAmount;
    private List<Long> seatIds;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;
}
