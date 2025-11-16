package com.bookmyshow.payment.gateway;

import com.bookmyshow.payment.dto.GatewayResponse;
import com.bookmyshow.payment.model.Payment;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Random;
import java.util.UUID;

@Component
@Slf4j
public class MockPaymentGatewayAdapter {

    private final double successRate;
    private final long processingTimeMs;
    private final Random random;

    public MockPaymentGatewayAdapter(
            @Value("${payment.gateway.mock.success-rate:0.9}") double successRate,
            @Value("${payment.gateway.mock.processing-time-ms:1000}") long processingTimeMs
    ) {
        this.successRate = successRate;
        this.processingTimeMs = processingTimeMs;
        this.random = new Random();
    }

    public GatewayResponse initiatePayment(String paymentReference, BigDecimal amount, Payment.PaymentMethod paymentMethod) {
        log.info("Initiating payment with gateway - Reference: {}, Amount: {}, Method: {}",
                paymentReference, amount, paymentMethod);

        simulateProcessingDelay();

        boolean isSuccess = random.nextDouble() < successRate;

        if (isSuccess) {
            String transactionId = "TXN_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
            String paymentUrl = "https://mock-gateway.com/pay/" + paymentReference;

            log.info("Payment initiated successfully - Transaction ID: {}", transactionId);

            return new GatewayResponse(
                    transactionId,
                    paymentUrl,
                    true,
                    "Payment initiated successfully"
            );
        } else {
            log.warn("Payment initiation failed for reference: {}", paymentReference);

            return new GatewayResponse(
                    null,
                    null,
                    false,
                    "Payment failed"
            );
        }
    }

    public GatewayResponse processRefund(String transactionId, BigDecimal refundAmount) {
        log.info("Processing refund - Transaction ID: {}, Amount: {}", transactionId, refundAmount);

        simulateProcessingDelay();

        String refundId = "REFUND_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);

        log.info("Refund processed successfully - Refund ID: {}", refundId);

        return new GatewayResponse(
                refundId,
                null,
                true,
                "Refund processed successfully"
        );
    }

    private void simulateProcessingDelay() {
        if (processingTimeMs > 0) {
            try {
                Thread.sleep(processingTimeMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                log.error("Processing delay interrupted", e);
            }
        }
    }
}
