package com.bookmyshow.payment.controller;

import com.bookmyshow.payment.dto.PaymentRequest;
import com.bookmyshow.payment.dto.PaymentResponse;
import com.bookmyshow.payment.dto.RefundRequest;
import com.bookmyshow.payment.dto.RefundResponse;
import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.model.Refund;
import com.bookmyshow.payment.service.PaymentService;
import com.bookmyshow.payment.service.RefundService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PaymentController.class)
class PaymentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private PaymentService paymentService;

    @MockBean
    private RefundService refundService;

    private PaymentResponse paymentResponse;
    private RefundResponse refundResponse;

    @BeforeEach
    void setUp() {
        paymentResponse = new PaymentResponse();
        paymentResponse.setId(1L);
        paymentResponse.setPaymentReference("PAY123456");
        paymentResponse.setBookingId(1L);
        paymentResponse.setUserId(100L);
        paymentResponse.setAmount(new BigDecimal("900.00"));
        paymentResponse.setCurrency("INR");
        paymentResponse.setStatus(Payment.PaymentStatus.INITIATED);
        paymentResponse.setPaymentUrl("https://gateway.com/pay/123");
        paymentResponse.setCreatedAt(LocalDateTime.now());

        refundResponse = new RefundResponse();
        refundResponse.setId(1L);
        refundResponse.setPaymentId(1L);
        refundResponse.setRefundAmount(new BigDecimal("900.00"));
        refundResponse.setStatus(Refund.RefundStatus.SUCCESS);
        refundResponse.setRefundReference("REFUND123456");
        refundResponse.setCreatedAt(LocalDateTime.now());
    }

    @Test
    void initiatePayment_ShouldReturnPaymentResponse() throws Exception {
        PaymentRequest request = new PaymentRequest();
        request.setBookingId(1L);
        request.setUserId(100L);
        request.setAmount(new BigDecimal("900.00"));
        request.setPaymentMethod(Payment.PaymentMethod.CARD);
        request.setGatewayName("MOCK_GATEWAY");

        when(paymentService.initiatePayment(any(PaymentRequest.class))).thenReturn(paymentResponse);

        mockMvc.perform(post("/api/payments/initiate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.paymentReference").value("PAY123456"))
                .andExpect(jsonPath("$.bookingId").value(1))
                .andExpect(jsonPath("$.amount").value(900.00))
                .andExpect(jsonPath("$.status").value("INITIATED"))
                .andExpect(jsonPath("$.paymentUrl").value("https://gateway.com/pay/123"));
    }

    @Test
    void initiatePayment_ShouldReturnBadRequest_WhenInvalidData() throws Exception {
        PaymentRequest request = new PaymentRequest();
        request.setBookingId(null);
        request.setUserId(100L);

        mockMvc.perform(post("/api/payments/initiate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getPaymentById_ShouldReturnPayment() throws Exception {
        when(paymentService.getPaymentById(1L)).thenReturn(paymentResponse);

        mockMvc.perform(get("/api/payments/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.paymentReference").value("PAY123456"));
    }

    @Test
    void getPaymentByBookingId_ShouldReturnPayment() throws Exception {
        when(paymentService.getPaymentByBookingId(1L)).thenReturn(paymentResponse);

        mockMvc.perform(get("/api/payments/booking/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.bookingId").value(1));
    }

    @Test
    void processRefund_ShouldReturnRefundResponse() throws Exception {
        RefundRequest request = new RefundRequest();
        request.setPaymentId(1L);
        request.setRefundAmount(new BigDecimal("900.00"));
        request.setReason("Booking cancelled by user");

        when(refundService.processRefund(any(RefundRequest.class))).thenReturn(refundResponse);

        mockMvc.perform(post("/api/payments/refund")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.paymentId").value(1))
                .andExpect(jsonPath("$.refundAmount").value(900.00))
                .andExpect(jsonPath("$.status").value("SUCCESS"));
    }

    @Test
    void getRefundsByPaymentId_ShouldReturnRefunds() throws Exception {
        List<RefundResponse> refunds = Arrays.asList(refundResponse);

        when(refundService.getRefundsByPaymentId(anyLong())).thenReturn(refunds);

        mockMvc.perform(get("/api/payments/1/refunds"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(1))
                .andExpect(jsonPath("$[0].paymentId").value(1));
    }
}
