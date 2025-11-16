package com.bookmyshow.payment.controller;

import com.bookmyshow.payment.dto.WebhookRequest;
import com.bookmyshow.payment.service.PaymentService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(WebhookController.class)
class WebhookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private PaymentService paymentService;

    @Test
    void handleWebhook_ShouldConfirmPayment_WhenStatusIsSuccess() throws Exception {
        WebhookRequest request = new WebhookRequest();
        request.setPaymentReference("PAY123456");
        request.setGatewayTransactionId("TXN123456");
        request.setStatus("SUCCESS");

        doNothing().when(paymentService).confirmPayment(anyString(), anyString());

        mockMvc.perform(post("/api/payments/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Webhook processed successfully"));

        verify(paymentService, times(1)).confirmPayment("PAY123456", "TXN123456");
        verify(paymentService, never()).failPayment(anyString(), anyString());
    }

    @Test
    void handleWebhook_ShouldFailPayment_WhenStatusIsFailed() throws Exception {
        WebhookRequest request = new WebhookRequest();
        request.setPaymentReference("PAY123456");
        request.setGatewayTransactionId("TXN123456");
        request.setStatus("FAILED");
        request.setFailureReason("Insufficient funds");

        doNothing().when(paymentService).failPayment(anyString(), anyString());

        mockMvc.perform(post("/api/payments/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Webhook processed successfully"));

        verify(paymentService, times(1)).failPayment("PAY123456", "Insufficient funds");
        verify(paymentService, never()).confirmPayment(anyString(), anyString());
    }

    @Test
    void handleWebhook_ShouldHandleUnknownStatus() throws Exception {
        WebhookRequest request = new WebhookRequest();
        request.setPaymentReference("PAY123456");
        request.setGatewayTransactionId("TXN123456");
        request.setStatus("PENDING");

        mockMvc.perform(post("/api/payments/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Webhook processed successfully"));

        verify(paymentService, never()).confirmPayment(anyString(), anyString());
        verify(paymentService, never()).failPayment(anyString(), anyString());
    }
}
