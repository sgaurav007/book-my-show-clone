package com.bookmyshow.payment.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RefundRequest {

    @NotNull(message = "Payment ID is required")
    private Long paymentId;

    @NotNull(message = "Refund amount is required")
    @Positive(message = "Refund amount must be positive")
    private BigDecimal refundAmount;

    private String reason;
}
