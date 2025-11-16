package com.bookmyshow.gateway.config;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/fallback")
public class FallbackController {

    @GetMapping("/user-service")
    public ResponseEntity<Map<String, Object>> userServiceFallback() {
        return createFallbackResponse("User Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/catalog-service")
    public ResponseEntity<Map<String, Object>> catalogServiceFallback() {
        return createFallbackResponse("Catalog Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/booking-service")
    public ResponseEntity<Map<String, Object>> bookingServiceFallback() {
        return createFallbackResponse("Booking Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/payment-service")
    public ResponseEntity<Map<String, Object>> paymentServiceFallback() {
        return createFallbackResponse("Payment Service is currently unavailable. Please try again later.");
    }

    private ResponseEntity<Map<String, Object>> createFallbackResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now());
        response.put("status", HttpStatus.SERVICE_UNAVAILABLE.value());
        response.put("error", "Service Unavailable");
        response.put("message", message);
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
    }
}
