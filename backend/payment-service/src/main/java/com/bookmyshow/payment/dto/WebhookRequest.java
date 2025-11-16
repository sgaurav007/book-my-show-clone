package com.bookmyshow.payment.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class WebhookRequest {

    private String paymentReference;
    private String gatewayTransactionId;
    private String status;
    private String failureReason;
}
