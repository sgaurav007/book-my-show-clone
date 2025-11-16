package com.bookmyshow.booking.dto;

import com.bookmyshow.booking.model.BookingStatus;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class BookingResponse {
    private Long id;
    private String bookingReference;
    private Long userId;
    private Long showId;
    private BigDecimal totalAmount;
    private BookingStatus bookingStatus;
    private Long paymentId;
    private LocalDateTime expiresAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<SeatResponse> seats;
}
