package com.bookmyshow.booking.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LockSeatsRequest {
    @NotNull
    private Long userId;

    @NotNull
    private Long showId;

    @NotEmpty
    private List<SeatInfo> seats;
}
