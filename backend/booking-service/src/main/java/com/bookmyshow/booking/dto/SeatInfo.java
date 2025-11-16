package com.bookmyshow.booking.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SeatInfo {
    @NotNull
    private Long seatId;

    @NotNull
    private String seatNumber;

    @NotNull
    private BigDecimal price;
}
