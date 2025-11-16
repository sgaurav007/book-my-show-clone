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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RefundServiceTest {

    @Mock
    private RefundRepository refundRepository;

    @Mock
    private PaymentRepository paymentRepository;

    @Mock
    private MockPaymentGatewayAdapter gatewayAdapter;

    @Mock
    private PaymentEventPublisher eventPublisher;

    @InjectMocks
    private RefundService refundService;

    private Payment payment;
    private RefundRequest refundRequest;

    @BeforeEach
    void setUp() {
        payment = new Payment();
        payment.setId(1L);
        payment.setPaymentReference("PAY123456");
        payment.setBookingId(1L);
        payment.setUserId(100L);
        payment.setAmount(new BigDecimal("900.00"));
        payment.setCurrency("INR");
        payment.setPaymentStatus(Payment.PaymentStatus.SUCCESS);
        payment.setGatewayTransactionId("TXN123456");

        refundRequest = new RefundRequest();
        refundRequest.setPaymentId(1L);
        refundRequest.setRefundAmount(new BigDecimal("900.00"));
        refundRequest.setReason("Booking cancelled by user");
    }

    @Test
    void processRefund_ShouldCreateRefundAndReturnResponse() {
        GatewayResponse gatewayResponse = new GatewayResponse(
                "REFUND123",
                null,
                true,
                "Refund processed successfully"
        );

        Refund savedRefund = new Refund();
        savedRefund.setId(1L);
        savedRefund.setPaymentId(1L);
        savedRefund.setRefundAmount(new BigDecimal("900.00"));
        savedRefund.setRefundStatus(Refund.RefundStatus.INITIATED);
        savedRefund.setRefundReference("REFUND123456");
        savedRefund.setReason("Booking cancelled by user");

        when(paymentRepository.findById(1L)).thenReturn(Optional.of(payment));
        when(refundRepository.getTotalRefundedAmount(1L)).thenReturn(BigDecimal.ZERO);
        when(refundRepository.save(any(Refund.class))).thenReturn(savedRefund);
        when(gatewayAdapter.processRefund(anyString(), any(BigDecimal.class))).thenReturn(gatewayResponse);

        RefundResponse response = refundService.processRefund(refundRequest);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals(1L, response.getPaymentId());
        assertEquals(new BigDecimal("900.00"), response.getRefundAmount());
        assertEquals("Booking cancelled by user", response.getReason());

        verify(refundRepository, times(2)).save(any(Refund.class));
        verify(gatewayAdapter, times(1)).processRefund(anyString(), any(BigDecimal.class));
        verify(paymentRepository, times(1)).save(any(Payment.class));
        verify(eventPublisher, times(1)).publishRefundProcessed(any(Refund.class), any(Payment.class));
    }

    @Test
    void processRefund_ShouldThrowException_WhenPaymentNotFound() {
        when(paymentRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(PaymentNotFoundException.class, () -> {
            refundService.processRefund(refundRequest);
        });

        verify(refundRepository, never()).save(any(Refund.class));
    }

    @Test
    void processRefund_ShouldThrowException_WhenPaymentNotSuccessful() {
        payment.setPaymentStatus(Payment.PaymentStatus.FAILED);
        when(paymentRepository.findById(1L)).thenReturn(Optional.of(payment));

        assertThrows(InvalidPaymentStateException.class, () -> {
            refundService.processRefund(refundRequest);
        });

        verify(refundRepository, never()).save(any(Refund.class));
    }

    @Test
    void processRefund_ShouldThrowException_WhenRefundAmountExceedsRemaining() {
        when(paymentRepository.findById(1L)).thenReturn(Optional.of(payment));
        when(refundRepository.getTotalRefundedAmount(1L)).thenReturn(new BigDecimal("500.00"));

        refundRequest.setRefundAmount(new BigDecimal("500.00"));

        assertThrows(InsufficientRefundAmountException.class, () -> {
            refundService.processRefund(refundRequest);
        });

        verify(refundRepository, never()).save(any(Refund.class));
    }

    @Test
    void processRefund_ShouldAllowPartialRefund() {
        GatewayResponse gatewayResponse = new GatewayResponse(
                "REFUND123",
                null,
                true,
                "Refund processed successfully"
        );

        Refund savedRefund = new Refund();
        savedRefund.setId(1L);
        savedRefund.setPaymentId(1L);
        savedRefund.setRefundAmount(new BigDecimal("450.00"));
        savedRefund.setRefundStatus(Refund.RefundStatus.SUCCESS);

        when(paymentRepository.findById(1L)).thenReturn(Optional.of(payment));
        when(refundRepository.getTotalRefundedAmount(1L)).thenReturn(BigDecimal.ZERO);
        when(refundRepository.save(any(Refund.class))).thenReturn(savedRefund);
        when(gatewayAdapter.processRefund(anyString(), any(BigDecimal.class))).thenReturn(gatewayResponse);

        refundRequest.setRefundAmount(new BigDecimal("450.00"));

        RefundResponse response = refundService.processRefund(refundRequest);

        assertNotNull(response);
        assertEquals(new BigDecimal("450.00"), response.getRefundAmount());
        verify(paymentRepository, never()).save(payment);
    }

    @Test
    void getRefundsByPaymentId_ShouldReturnRefunds() {
        Refund refund1 = new Refund();
        refund1.setId(1L);
        refund1.setPaymentId(1L);
        refund1.setRefundAmount(new BigDecimal("450.00"));

        Refund refund2 = new Refund();
        refund2.setId(2L);
        refund2.setPaymentId(1L);
        refund2.setRefundAmount(new BigDecimal("450.00"));

        when(refundRepository.findByPaymentId(1L)).thenReturn(Arrays.asList(refund1, refund2));

        List<RefundResponse> responses = refundService.getRefundsByPaymentId(1L);

        assertNotNull(responses);
        assertEquals(2, responses.size());
        assertEquals(1L, responses.get(0).getId());
        assertEquals(2L, responses.get(1).getId());
    }
}
