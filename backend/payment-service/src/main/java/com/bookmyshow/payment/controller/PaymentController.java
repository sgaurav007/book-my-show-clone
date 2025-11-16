package com.bookmyshow.payment.controller;

import com.bookmyshow.payment.dto.PaymentRequest;
import com.bookmyshow.payment.dto.PaymentResponse;
import com.bookmyshow.payment.dto.RefundRequest;
import com.bookmyshow.payment.dto.RefundResponse;
import com.bookmyshow.payment.service.PaymentService;
import com.bookmyshow.payment.service.RefundService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/payments")
@Slf4j
public class PaymentController {

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private RefundService refundService;

    @PostMapping("/initiate")
    public ResponseEntity<PaymentResponse> initiatePayment(@Valid @RequestBody PaymentRequest request) {
        log.info("Received payment initiation request for booking: {}", request.getBookingId());
        PaymentResponse response = paymentService.initiatePayment(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PaymentResponse> getPaymentById(@PathVariable Long id) {
        log.info("Fetching payment by id: {}", id);
        PaymentResponse response = paymentService.getPaymentById(id);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/booking/{bookingId}")
    public ResponseEntity<PaymentResponse> getPaymentByBookingId(@PathVariable Long bookingId) {
        log.info("Fetching payment by booking id: {}", bookingId);
        PaymentResponse response = paymentService.getPaymentByBookingId(bookingId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/refund")
    public ResponseEntity<RefundResponse> processRefund(@Valid @RequestBody RefundRequest request) {
        log.info("Received refund request for payment: {}", request.getPaymentId());
        RefundResponse response = refundService.processRefund(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{paymentId}/refunds")
    public ResponseEntity<List<RefundResponse>> getRefundsByPaymentId(@PathVariable Long paymentId) {
        log.info("Fetching refunds for payment: {}", paymentId);
        List<RefundResponse> refunds = refundService.getRefundsByPaymentId(paymentId);
        return ResponseEntity.ok(refunds);
    }
}
