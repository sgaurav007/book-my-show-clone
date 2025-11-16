package com.bookmyshow.payment.dto;

import com.bookmyshow.payment.model.Payment;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentResponse {

    private Long id;
    private String paymentReference;
    private Long bookingId;
    private Long userId;
    private BigDecimal amount;
    private String currency;
    private Payment.PaymentStatus status;
    private String gatewayTransactionId;
    private String paymentUrl;
    private LocalDateTime createdAt;

    public static PaymentResponse from(Payment payment) {
        PaymentResponse response = new PaymentResponse();
        response.setId(payment.getId());
        response.setPaymentReference(payment.getPaymentReference());
        response.setBookingId(payment.getBookingId());
        response.setUserId(payment.getUserId());
        response.setAmount(payment.getAmount());
        response.setCurrency(payment.getCurrency());
        response.setStatus(payment.getPaymentStatus());
        response.setGatewayTransactionId(payment.getGatewayTransactionId());
        response.setCreatedAt(payment.getCreatedAt());
        return response;
    }
}
