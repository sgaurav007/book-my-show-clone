package com.bookmyshow.payment.service;

import com.bookmyshow.payment.dto.GatewayResponse;
import com.bookmyshow.payment.dto.RefundRequest;
import com.bookmyshow.payment.dto.RefundResponse;
import com.bookmyshow.payment.exception.InsufficientRefundAmountException;
import com.bookmyshow.payment.exception.InvalidPaymentStateException;
import com.bookmyshow.payment.exception.PaymentNotFoundException;
import com.bookmyshow.payment.gateway.MockPaymentGatewayAdapter;
import com.bookmyshow.payment.kafka.PaymentEventPublisher;
import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.model.Refund;
import com.bookmyshow.payment.repository.PaymentRepository;
import com.bookmyshow.payment.repository.RefundRepository;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Slf4j
@Transactional
public class RefundService {

    @Autowired
    private RefundRepository refundRepository;

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private MockPaymentGatewayAdapter gatewayAdapter;

    @Autowired
    private PaymentEventPublisher eventPublisher;

    public RefundResponse processRefund(RefundRequest request) {
        log.info("Processing refund for payment ID: {}", request.getPaymentId());

        Payment payment = paymentRepository.findById(request.getPaymentId())
                .orElseThrow(() -> new PaymentNotFoundException("Payment not found with id: " + request.getPaymentId()));

        if (payment.getPaymentStatus() != Payment.PaymentStatus.SUCCESS) {
            throw new InvalidPaymentStateException("Cannot refund payment that is not successful");
        }

        BigDecimal totalRefunded = refundRepository.getTotalRefundedAmount(payment.getId());
        BigDecimal remainingAmount = payment.getAmount().subtract(totalRefunded);

        if (request.getRefundAmount().compareTo(remainingAmount) > 0) {
            throw new InsufficientRefundAmountException(
                    String.format("Refund amount %.2f exceeds remaining amount %.2f",
                            request.getRefundAmount(), remainingAmount)
            );
        }

        Refund refund = new Refund();
        refund.setPaymentId(payment.getId());
        refund.setRefundAmount(request.getRefundAmount());
        refund.setRefundStatus(Refund.RefundStatus.INITIATED);
        refund.setRefundReference(generateRefundReference());
        refund.setReason(request.getReason());

        Refund savedRefund = refundRepository.save(refund);

        GatewayResponse gatewayResponse = gatewayAdapter.processRefund(
                payment.getGatewayTransactionId(),
                request.getRefundAmount()
        );

        if (gatewayResponse.isSuccess()) {
            savedRefund.setRefundStatus(Refund.RefundStatus.SUCCESS);
            savedRefund.setGatewayRefundId(gatewayResponse.getTransactionId());
        } else {
            savedRefund.setRefundStatus(Refund.RefundStatus.FAILED);
        }

        refundRepository.save(savedRefund);

        if (savedRefund.getRefundStatus() == Refund.RefundStatus.SUCCESS) {
            BigDecimal newTotalRefunded = totalRefunded.add(request.getRefundAmount());
            if (newTotalRefunded.compareTo(payment.getAmount()) == 0) {
                payment.setPaymentStatus(Payment.PaymentStatus.REFUNDED);
                paymentRepository.save(payment);
                log.info("Payment fully refunded: {}", payment.getPaymentReference());
            }

            eventPublisher.publishRefundProcessed(savedRefund, payment);
        }

        log.info("Refund processed: {} with status: {}", savedRefund.getRefundReference(), savedRefund.getRefundStatus());

        return RefundResponse.from(savedRefund);
    }

    public List<RefundResponse> getRefundsByPaymentId(Long paymentId) {
        List<Refund> refunds = refundRepository.findByPaymentId(paymentId);
        return refunds.stream()
                .map(RefundResponse::from)
                .collect(Collectors.toList());
    }

    private String generateRefundReference() {
        return "REFUND" + System.currentTimeMillis() + RandomStringUtils.randomAlphanumeric(6).toUpperCase();
    }
}
