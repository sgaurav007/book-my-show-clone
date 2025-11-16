package com.bookmyshow.payment.service;

import com.bookmyshow.payment.dto.GatewayResponse;
import com.bookmyshow.payment.dto.PaymentRequest;
import com.bookmyshow.payment.dto.PaymentResponse;
import com.bookmyshow.payment.exception.PaymentAlreadyProcessedException;
import com.bookmyshow.payment.exception.PaymentNotFoundException;
import com.bookmyshow.payment.gateway.MockPaymentGatewayAdapter;
import com.bookmyshow.payment.kafka.PaymentEventPublisher;
import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.repository.PaymentAuditLogRepository;
import com.bookmyshow.payment.repository.PaymentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {

    @Mock
    private PaymentRepository paymentRepository;

    @Mock
    private PaymentAuditLogRepository auditLogRepository;

    @Mock
    private MockPaymentGatewayAdapter gatewayAdapter;

    @Mock
    private PaymentEventPublisher eventPublisher;

    @InjectMocks
    private PaymentService paymentService;

    private PaymentRequest paymentRequest;
    private Payment payment;

    @BeforeEach
    void setUp() {
        paymentRequest = new PaymentRequest();
        paymentRequest.setBookingId(1L);
        paymentRequest.setUserId(100L);
        paymentRequest.setAmount(new BigDecimal("900.00"));
        paymentRequest.setPaymentMethod(Payment.PaymentMethod.CARD);
        paymentRequest.setGatewayName("MOCK_GATEWAY");

        payment = new Payment();
        payment.setId(1L);
        payment.setPaymentReference("PAY123456");
        payment.setBookingId(1L);
        payment.setUserId(100L);
        payment.setAmount(new BigDecimal("900.00"));
        payment.setCurrency("INR");
        payment.setPaymentMethod(Payment.PaymentMethod.CARD);
        payment.setPaymentStatus(Payment.PaymentStatus.INITIATED);
        payment.setGatewayName("MOCK_GATEWAY");
    }

    @Test
    void initiatePayment_ShouldCreatePaymentAndReturnResponse() {
        GatewayResponse gatewayResponse = new GatewayResponse(
                "TXN123456",
                "https://gateway.com/pay/123",
                true,
                "Payment initiated successfully"
        );

        when(paymentRepository.existsByBookingId(1L)).thenReturn(false);
        when(paymentRepository.save(any(Payment.class))).thenReturn(payment);
        when(gatewayAdapter.initiatePayment(anyString(), any(BigDecimal.class), any(Payment.PaymentMethod.class)))
                .thenReturn(gatewayResponse);

        PaymentResponse response = paymentService.initiatePayment(paymentRequest);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("PAY123456", response.getPaymentReference());
        assertEquals(1L, response.getBookingId());
        assertEquals(new BigDecimal("900.00"), response.getAmount());
        assertEquals(Payment.PaymentStatus.INITIATED, response.getStatus());
        assertEquals("https://gateway.com/pay/123", response.getPaymentUrl());

        verify(paymentRepository, times(2)).save(any(Payment.class));
        verify(gatewayAdapter, times(1)).initiatePayment(anyString(), any(BigDecimal.class), any(Payment.PaymentMethod.class));
        verify(eventPublisher, times(1)).publishPaymentInitiated(any(Payment.class));
        verify(auditLogRepository, times(1)).save(any());
    }

    @Test
    void initiatePayment_ShouldThrowException_WhenBookingAlreadyHasPayment() {
        when(paymentRepository.existsByBookingId(1L)).thenReturn(true);

        assertThrows(PaymentAlreadyProcessedException.class, () -> {
            paymentService.initiatePayment(paymentRequest);
        });

        verify(paymentRepository, never()).save(any(Payment.class));
    }

    @Test
    void confirmPayment_ShouldUpdatePaymentStatusToSuccess() {
        payment.setPaymentStatus(Payment.PaymentStatus.INITIATED);
        when(paymentRepository.findByPaymentReference("PAY123456")).thenReturn(Optional.of(payment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(payment);

        paymentService.confirmPayment("PAY123456", "TXN123456");

        assertEquals(Payment.PaymentStatus.SUCCESS, payment.getPaymentStatus());
        assertEquals("TXN123456", payment.getGatewayTransactionId());

        verify(paymentRepository, times(1)).save(payment);
        verify(eventPublisher, times(1)).publishPaymentSuccess(payment);
        verify(auditLogRepository, times(1)).save(any());
    }

    @Test
    void confirmPayment_ShouldBeIdempotent_WhenAlreadyConfirmed() {
        payment.setPaymentStatus(Payment.PaymentStatus.SUCCESS);
        when(paymentRepository.findByPaymentReference("PAY123456")).thenReturn(Optional.of(payment));

        paymentService.confirmPayment("PAY123456", "TXN123456");

        verify(paymentRepository, never()).save(any(Payment.class));
        verify(eventPublisher, never()).publishPaymentSuccess(any(Payment.class));
    }

    @Test
    void confirmPayment_ShouldThrowException_WhenPaymentNotFound() {
        when(paymentRepository.findByPaymentReference("PAY123456")).thenReturn(Optional.empty());

        assertThrows(PaymentNotFoundException.class, () -> {
            paymentService.confirmPayment("PAY123456", "TXN123456");
        });
    }

    @Test
    void failPayment_ShouldUpdatePaymentStatusToFailed() {
        payment.setPaymentStatus(Payment.PaymentStatus.INITIATED);
        when(paymentRepository.findByPaymentReference("PAY123456")).thenReturn(Optional.of(payment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(payment);

        paymentService.failPayment("PAY123456", "Insufficient funds");

        assertEquals(Payment.PaymentStatus.FAILED, payment.getPaymentStatus());
        assertEquals("Insufficient funds", payment.getFailureReason());

        verify(paymentRepository, times(1)).save(payment);
        verify(eventPublisher, times(1)).publishPaymentFailed(payment);
        verify(auditLogRepository, times(1)).save(any());
    }

    @Test
    void getPaymentById_ShouldReturnPayment_WhenExists() {
        when(paymentRepository.findById(1L)).thenReturn(Optional.of(payment));

        PaymentResponse response = paymentService.getPaymentById(1L);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("PAY123456", response.getPaymentReference());
    }

    @Test
    void getPaymentById_ShouldThrowException_WhenNotFound() {
        when(paymentRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(PaymentNotFoundException.class, () -> {
            paymentService.getPaymentById(1L);
        });
    }

    @Test
    void getPaymentByBookingId_ShouldReturnPayment_WhenExists() {
        when(paymentRepository.findByBookingId(1L)).thenReturn(Optional.of(payment));

        PaymentResponse response = paymentService.getPaymentByBookingId(1L);

        assertNotNull(response);
        assertEquals(1L, response.getBookingId());
    }

    @Test
    void getPaymentByBookingId_ShouldThrowException_WhenNotFound() {
        when(paymentRepository.findByBookingId(1L)).thenReturn(Optional.empty());

        assertThrows(PaymentNotFoundException.class, () -> {
            paymentService.getPaymentByBookingId(1L);
        });
    }
}
