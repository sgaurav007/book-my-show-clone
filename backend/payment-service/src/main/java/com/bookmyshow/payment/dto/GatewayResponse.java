package com.bookmyshow.payment.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GatewayResponse {

    private String transactionId;
    private String paymentUrl;
    private boolean success;
    private String message;
}
