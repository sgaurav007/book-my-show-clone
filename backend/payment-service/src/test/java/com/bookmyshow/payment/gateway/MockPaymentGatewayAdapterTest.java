package com.bookmyshow.payment.gateway;

import com.bookmyshow.payment.dto.GatewayResponse;
import com.bookmyshow.payment.model.Payment;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

class MockPaymentGatewayAdapterTest {

    private MockPaymentGatewayAdapter gatewayAdapter;

    @BeforeEach
    void setUp() {
        gatewayAdapter = new MockPaymentGatewayAdapter(1.0, 0);
    }

    @Test
    void initiatePayment_ShouldReturnSuccessResponse() {
        GatewayResponse response = gatewayAdapter.initiatePayment(
                "PAY123456",
                new BigDecimal("900.00"),
                Payment.PaymentMethod.CARD
        );

        assertNotNull(response);
        assertTrue(response.isSuccess());
        assertNotNull(response.getTransactionId());
        assertNotNull(response.getPaymentUrl());
        assertTrue(response.getPaymentUrl().contains("PAY123456"));
        assertEquals("Payment initiated successfully", response.getMessage());
    }

    @Test
    void initiatePayment_ShouldGenerateUniqueTransactionId() {
        GatewayResponse response1 = gatewayAdapter.initiatePayment(
                "PAY123456",
                new BigDecimal("900.00"),
                Payment.PaymentMethod.CARD
        );

        GatewayResponse response2 = gatewayAdapter.initiatePayment(
                "PAY123457",
                new BigDecimal("800.00"),
                Payment.PaymentMethod.UPI
        );

        assertNotEquals(response1.getTransactionId(), response2.getTransactionId());
    }

    @Test
    void processRefund_ShouldReturnSuccessResponse() {
        GatewayResponse response = gatewayAdapter.processRefund(
                "TXN123456",
                new BigDecimal("900.00")
        );

        assertNotNull(response);
        assertTrue(response.isSuccess());
        assertNotNull(response.getTransactionId());
        assertTrue(response.getTransactionId().startsWith("REFUND_"));
        assertEquals("Refund processed successfully", response.getMessage());
    }

    @Test
    void processRefund_ShouldGenerateUniqueRefundId() {
        GatewayResponse response1 = gatewayAdapter.processRefund(
                "TXN123456",
                new BigDecimal("900.00")
        );

        GatewayResponse response2 = gatewayAdapter.processRefund(
                "TXN123457",
                new BigDecimal("800.00")
        );

        assertNotEquals(response1.getTransactionId(), response2.getTransactionId());
    }

    @Test
    void simulatePaymentWithLowSuccessRate_ShouldReturnFailure() {
        MockPaymentGatewayAdapter failureAdapter = new MockPaymentGatewayAdapter(0.0, 0);

        GatewayResponse response = failureAdapter.initiatePayment(
                "PAY123456",
                new BigDecimal("900.00"),
                Payment.PaymentMethod.CARD
        );

        assertNotNull(response);
        assertFalse(response.isSuccess());
        assertEquals("Payment failed", response.getMessage());
    }

    @Test
    void simulatePayment_ShouldRespectSuccessRate() {
        MockPaymentGatewayAdapter mixedAdapter = new MockPaymentGatewayAdapter(0.5, 0);

        int successCount = 0;
        int totalAttempts = 100;

        for (int i = 0; i < totalAttempts; i++) {
            GatewayResponse response = mixedAdapter.initiatePayment(
                    "PAY" + i,
                    new BigDecimal("900.00"),
                    Payment.PaymentMethod.CARD
            );
            if (response.isSuccess()) {
                successCount++;
            }
        }

        assertTrue(successCount >= 30 && successCount <= 70,
                "Success rate should be around 50%, but was " + (successCount * 100.0 / totalAttempts) + "%");
    }
}
