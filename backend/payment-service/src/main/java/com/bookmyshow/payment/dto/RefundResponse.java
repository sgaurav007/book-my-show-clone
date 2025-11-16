package com.bookmyshow.payment.dto;

import com.bookmyshow.payment.model.Refund;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RefundResponse {

    private Long id;
    private Long paymentId;
    private BigDecimal refundAmount;
    private Refund.RefundStatus status;
    private String refundReference;
    private String reason;
    private LocalDateTime createdAt;

    public static RefundResponse from(Refund refund) {
        RefundResponse response = new RefundResponse();
        response.setId(refund.getId());
        response.setPaymentId(refund.getPaymentId());
        response.setRefundAmount(refund.getRefundAmount());
        response.setStatus(refund.getRefundStatus());
        response.setRefundReference(refund.getRefundReference());
        response.setReason(refund.getReason());
        response.setCreatedAt(refund.getCreatedAt());
        return response;
    }
}
