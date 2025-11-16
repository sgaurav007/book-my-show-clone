package com.bookmyshow.payment.integration;

import com.bookmyshow.payment.dto.PaymentRequest;
import com.bookmyshow.payment.dto.PaymentResponse;
import com.bookmyshow.payment.dto.RefundRequest;
import com.bookmyshow.payment.dto.RefundResponse;
import com.bookmyshow.payment.model.Payment;
import com.bookmyshow.payment.model.Refund;
import com.bookmyshow.payment.repository.PaymentRepository;
import com.bookmyshow.payment.repository.RefundRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class PaymentIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private RefundRepository refundRepository;

    @BeforeEach
    void setUp() {
        paymentRepository.deleteAll();
        refundRepository.deleteAll();
    }

    @Test
    void testFullPaymentFlow() throws Exception {
        PaymentRequest paymentRequest = new PaymentRequest();
        paymentRequest.setBookingId(1L);
        paymentRequest.setUserId(100L);
        paymentRequest.setAmount(new BigDecimal("900.00"));
        paymentRequest.setPaymentMethod(Payment.PaymentMethod.CARD);
        paymentRequest.setGatewayName("MOCK_GATEWAY");

        String response = mockMvc.perform(post("/api/payments/initiate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(paymentRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.paymentReference").exists())
                .andExpect(jsonPath("$.status").value("INITIATED"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        PaymentResponse paymentResponse = objectMapper.readValue(response, PaymentResponse.class);

        assertEquals(1, paymentRepository.count());
        Payment savedPayment = paymentRepository.findById(paymentResponse.getId()).orElseThrow();
        assertEquals(Payment.PaymentStatus.INITIATED, savedPayment.getPaymentStatus());
        assertEquals(new BigDecimal("900.00"), savedPayment.getAmount());

        mockMvc.perform(get("/api/payments/" + paymentResponse.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(paymentResponse.getId()))
                .andExpect(jsonPath("$.paymentReference").value(paymentResponse.getPaymentReference()));

        mockMvc.perform(get("/api/payments/booking/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.bookingId").value(1));
    }

    @Test
    void testPaymentAndRefundFlow() throws Exception {
        Payment payment = new Payment();
        payment.setPaymentReference("PAY123456");
        payment.setBookingId(2L);
        payment.setUserId(100L);
        payment.setAmount(new BigDecimal("900.00"));
        payment.setCurrency("INR");
        payment.setPaymentMethod(Payment.PaymentMethod.CARD);
        payment.setPaymentStatus(Payment.PaymentStatus.SUCCESS);
        payment.setGatewayTransactionId("TXN123456");
        payment.setGatewayName("MOCK_GATEWAY");
        payment = paymentRepository.save(payment);

        RefundRequest refundRequest = new RefundRequest();
        refundRequest.setPaymentId(payment.getId());
        refundRequest.setRefundAmount(new BigDecimal("450.00"));
        refundRequest.setReason("Partial cancellation");

        String response = mockMvc.perform(post("/api/payments/refund")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(refundRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.refundAmount").value(450.00))
                .andReturn()
                .getResponse()
                .getContentAsString();

        RefundResponse refundResponse = objectMapper.readValue(response, RefundResponse.class);

        assertEquals(1, refundRepository.count());
        Refund savedRefund = refundRepository.findById(refundResponse.getId()).orElseThrow();
        assertEquals(Refund.RefundStatus.SUCCESS, savedRefund.getRefundStatus());

        mockMvc.perform(get("/api/payments/" + payment.getId() + "/refunds"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(refundResponse.getId()));
    }

    @Test
    void testFullRefundUpdatesPaymentStatus() throws Exception {
        Payment payment = new Payment();
        payment.setPaymentReference("PAY789456");
        payment.setBookingId(3L);
        payment.setUserId(100L);
        payment.setAmount(new BigDecimal("900.00"));
        payment.setCurrency("INR");
        payment.setPaymentMethod(Payment.PaymentMethod.UPI);
        payment.setPaymentStatus(Payment.PaymentStatus.SUCCESS);
        payment.setGatewayTransactionId("TXN789456");
        payment.setGatewayName("MOCK_GATEWAY");
        payment = paymentRepository.save(payment);

        RefundRequest refundRequest = new RefundRequest();
        refundRequest.setPaymentId(payment.getId());
        refundRequest.setRefundAmount(new BigDecimal("900.00"));
        refundRequest.setReason("Full cancellation");

        mockMvc.perform(post("/api/payments/refund")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(refundRequest)))
                .andExpect(status().isOk());

        Payment updatedPayment = paymentRepository.findById(payment.getId()).orElseThrow();
        assertEquals(Payment.PaymentStatus.REFUNDED, updatedPayment.getPaymentStatus());
    }

    @Test
    void testDuplicatePaymentForSameBooking() throws Exception {
        Payment payment = new Payment();
        payment.setPaymentReference("PAY111222");
        payment.setBookingId(4L);
        payment.setUserId(100L);
        payment.setAmount(new BigDecimal("900.00"));
        payment.setCurrency("INR");
        payment.setPaymentStatus(Payment.PaymentStatus.INITIATED);
        paymentRepository.save(payment);

        PaymentRequest paymentRequest = new PaymentRequest();
        paymentRequest.setBookingId(4L);
        paymentRequest.setUserId(100L);
        paymentRequest.setAmount(new BigDecimal("900.00"));
        paymentRequest.setPaymentMethod(Payment.PaymentMethod.CARD);

        mockMvc.perform(post("/api/payments/initiate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(paymentRequest)))
                .andExpect(status().isConflict());
    }
}
