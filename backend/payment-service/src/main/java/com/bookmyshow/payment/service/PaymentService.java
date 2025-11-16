package com.bookmyshow.payment.service;

import com.bookmyshow.payment.dto.GatewayResponse;
import com.bookmyshow.payment.dto.PaymentRequest;
import com.bookmyshow.payment.dto.PaymentResponse;
import com.bookmyshow.payment.exception.PaymentAlreadyProcessedException;
import com.bookmyshow.payment.exception.PaymentNotFoundException;
import com.bookmyshow.payment.gateway.MockPaymentGatewayAdapter;
import com.bookmyshow.payment.kafka.PaymentEventPublisher;
import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.model.PaymentAuditLog;
import com.bookmyshow.payment.repository.PaymentAuditLogRepository;
import com.bookmyshow.payment.repository.PaymentRepository;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
@Transactional
public class PaymentService {

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private PaymentAuditLogRepository auditLogRepository;

    @Autowired
    private MockPaymentGatewayAdapter gatewayAdapter;

    @Autowired
    private PaymentEventPublisher eventPublisher;

    public PaymentResponse initiatePayment(PaymentRequest request) {
        log.info("Initiating payment for booking ID: {}", request.getBookingId());

        if (paymentRepository.existsByBookingId(request.getBookingId())) {
            throw new PaymentAlreadyProcessedException("Payment already exists for this booking");
        }

        Payment payment = new Payment();
        payment.setPaymentReference(generatePaymentReference());
        payment.setBookingId(request.getBookingId());
        payment.setUserId(request.getUserId());
        payment.setAmount(request.getAmount());
        payment.setCurrency("INR");
        payment.setPaymentMethod(request.getPaymentMethod());
        payment.setPaymentStatus(Payment.PaymentStatus.INITIATED);
        payment.setGatewayName(request.getGatewayName());

        Payment savedPayment = paymentRepository.save(payment);

        GatewayResponse gatewayResponse = gatewayAdapter.initiatePayment(
                savedPayment.getPaymentReference(),
                savedPayment.getAmount(),
                request.getPaymentMethod()
        );

        savedPayment.setGatewayTransactionId(gatewayResponse.getTransactionId());
        paymentRepository.save(savedPayment);

        logAuditEvent(savedPayment.getId(), "PAYMENT_INITIATED", Map.of(
                "paymentReference", savedPayment.getPaymentReference(),
                "amount", savedPayment.getAmount().toString(),
                "gatewayTransactionId", gatewayResponse.getTransactionId() != null ? gatewayResponse.getTransactionId() : "N/A"
        ));

        eventPublisher.publishPaymentInitiated(savedPayment);

        log.info("Payment initiated successfully: {}", savedPayment.getPaymentReference());

        PaymentResponse response = PaymentResponse.from(savedPayment);
        response.setPaymentUrl(gatewayResponse.getPaymentUrl());
        return response;
    }

    public void confirmPayment(String paymentReference, String gatewayTransactionId) {
        log.info("Confirming payment: {}", paymentReference);

        Payment payment = paymentRepository.findByPaymentReference(paymentReference)
                .orElseThrow(() -> new PaymentNotFoundException("Payment not found: " + paymentReference));

        if (payment.getPaymentStatus() == Payment.PaymentStatus.SUCCESS) {
            log.warn("Payment already confirmed: {}", paymentReference);
            return;
        }

        payment.setPaymentStatus(Payment.PaymentStatus.SUCCESS);
        payment.setGatewayTransactionId(gatewayTransactionId);
        paymentRepository.save(payment);

        logAuditEvent(payment.getId(), "PAYMENT_CONFIRMED", Map.of(
                "paymentReference", paymentReference,
                "gatewayTransactionId", gatewayTransactionId
        ));

        eventPublisher.publishPaymentSuccess(payment);

        log.info("Payment confirmed successfully: {}", paymentReference);
    }

    public void failPayment(String paymentReference, String failureReason) {
        log.info("Failing payment: {}", paymentReference);

        Payment payment = paymentRepository.findByPaymentReference(paymentReference)
                .orElseThrow(() -> new PaymentNotFoundException("Payment not found: " + paymentReference));

        payment.setPaymentStatus(Payment.PaymentStatus.FAILED);
        payment.setFailureReason(failureReason);
        paymentRepository.save(payment);

        logAuditEvent(payment.getId(), "PAYMENT_FAILED", Map.of(
                "paymentReference", paymentReference,
                "failureReason", failureReason
        ));

        eventPublisher.publishPaymentFailed(payment);

        log.error("Payment failed: {}, reason: {}", paymentReference, failureReason);
    }

    public PaymentResponse getPaymentById(Long id) {
        Payment payment = paymentRepository.findById(id)
                .orElseThrow(() -> new PaymentNotFoundException("Payment not found with id: " + id));
        return PaymentResponse.from(payment);
    }

    public PaymentResponse getPaymentByBookingId(Long bookingId) {
        Payment payment = paymentRepository.findByBookingId(bookingId)
                .orElseThrow(() -> new PaymentNotFoundException("Payment not found for booking: " + bookingId));
        return PaymentResponse.from(payment);
    }

    private String generatePaymentReference() {
        return "PAY" + System.currentTimeMillis() + RandomStringUtils.randomAlphanumeric(8).toUpperCase();
    }

    private void logAuditEvent(Long paymentId, String eventType, Map<String, Object> eventData) {
        PaymentAuditLog auditLog = new PaymentAuditLog();
        auditLog.setPaymentId(paymentId);
        auditLog.setEventType(eventType);
        auditLog.setEventData(new HashMap<>(eventData));
        auditLogRepository.save(auditLog);
    }
}
