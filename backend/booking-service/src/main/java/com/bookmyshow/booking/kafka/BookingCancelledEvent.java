package com.bookmyshow.booking.kafka;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class BookingCancelledEvent {
    private Long bookingId;
    private String bookingReference;
    private Long userId;
    private Long showId;
    private List<Long> seatIds;
    private String reason;
    private LocalDateTime cancelledAt;
}
