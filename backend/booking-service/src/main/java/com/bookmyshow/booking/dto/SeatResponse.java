package com.bookmyshow.booking.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SeatResponse {
    private Long seatId;
    private String seatNumber;
    private BigDecimal price;
}
