package com.bookmyshow.payment.controller;

import com.bookmyshow.payment.dto.WebhookRequest;
import com.bookmyshow.payment.service.PaymentService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/payments")
@Slf4j
public class WebhookController {

    @Autowired
    private PaymentService paymentService;

    @PostMapping("/webhook")
    public ResponseEntity<Map<String, String>> handleWebhook(@RequestBody WebhookRequest request) {
        log.info("Received webhook for payment: {} with status: {}",
                request.getPaymentReference(), request.getStatus());

        if ("SUCCESS".equalsIgnoreCase(request.getStatus())) {
            paymentService.confirmPayment(request.getPaymentReference(), request.getGatewayTransactionId());
        } else if ("FAILED".equalsIgnoreCase(request.getStatus())) {
            paymentService.failPayment(request.getPaymentReference(), request.getFailureReason());
        }

        Map<String, String> response = new HashMap<>();
        response.put("message", "Webhook processed successfully");
        return ResponseEntity.ok(response);
    }
}
