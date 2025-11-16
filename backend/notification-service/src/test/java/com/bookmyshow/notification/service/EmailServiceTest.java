package com.bookmyshow.notification.service;

import com.bookmyshow.notification.dto.BookingCancelledEvent;
import com.bookmyshow.notification.dto.BookingConfirmedEvent;
import com.bookmyshow.notification.dto.PaymentFailedEvent;
import com.bookmyshow.notification.dto.PaymentSuccessEvent;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class EmailServiceTest {

    @InjectMocks
    private EmailService emailService;

    private BookingConfirmedEvent.BookingData bookingData;
    private PaymentSuccessEvent.PaymentData paymentData;
    private PaymentFailedEvent.PaymentFailureData paymentFailureData;
    private BookingCancelledEvent.BookingCancellationData cancellationData;

    @BeforeEach
    void setUp() {
        bookingData = BookingConfirmedEvent.BookingData.builder()
                .bookingId(123L)
                .bookingReference("BMS123456")
                .userId(1L)
                .userEmail("user@example.com")
                .userPhone("+919876543210")
                .movieTitle("Inception")
                .theaterName("PVR Phoenix")
                .showDateTime(LocalDateTime.of(2024, 11, 16, 18, 0))
                .seats(Arrays.asList("A1", "A2", "A3"))
                .totalAmount(new BigDecimal("900.00"))
                .build();

        paymentData = PaymentSuccessEvent.PaymentData.builder()
                .paymentId(456L)
                .paymentReference("PAY123456")
                .userId(1L)
                .userEmail("user@example.com")
                .amount(new BigDecimal("900.00"))
                .currency("INR")
                .paymentMethod("CARD")
                .build();

        paymentFailureData = PaymentFailedEvent.PaymentFailureData.builder()
                .paymentId(789L)
                .paymentReference("PAY789012")
                .userId(1L)
                .userEmail("user@example.com")
                .amount(new BigDecimal("900.00"))
                .failureReason("Insufficient funds")
                .errorCode("ERR_001")
                .build();

        cancellationData = BookingCancelledEvent.BookingCancellationData.builder()
                .bookingId(123L)
                .bookingReference("BMS123456")
                .userId(1L)
                .userEmail("user@example.com")
                .movieTitle("Inception")
                .theaterName("PVR Phoenix")
                .showDateTime(LocalDateTime.of(2024, 11, 16, 18, 0))
                .seats(Arrays.asList("A1", "A2", "A3"))
                .refundAmount(new BigDecimal("900.00"))
                .cancellationReason("User requested")
                .build();
    }

    @Test
    void testSendBookingConfirmationEmail() {
        assertDoesNotThrow(() ->
                emailService.sendBookingConfirmationEmail(
                        bookingData.getUserEmail(),
                        bookingData.getBookingReference(),
                        bookingData.getMovieTitle(),
                        bookingData.getTheaterName(),
                        bookingData.getShowDateTime(),
                        bookingData.getSeats(),
                        bookingData.getTotalAmount()
                )
        );
    }

    @Test
    void testSendBookingCancellationEmail() {
        assertDoesNotThrow(() ->
                emailService.sendBookingCancellationEmail(
                        cancellationData.getUserEmail(),
                        cancellationData.getBookingReference(),
                        cancellationData.getMovieTitle(),
                        cancellationData.getTheaterName(),
                        cancellationData.getShowDateTime(),
                        cancellationData.getSeats(),
                        cancellationData.getRefundAmount()
                )
        );
    }

    @Test
    void testSendPaymentReceiptEmail() {
        assertDoesNotThrow(() ->
                emailService.sendPaymentReceiptEmail(
                        paymentData.getUserEmail(),
                        paymentData.getPaymentReference(),
                        paymentData.getAmount(),
                        paymentData.getCurrency(),
                        paymentData.getPaymentMethod()
                )
        );
    }

    @Test
    void testSendPaymentFailureEmail() {
        assertDoesNotThrow(() ->
                emailService.sendPaymentFailureEmail(
                        paymentFailureData.getUserEmail(),
                        paymentFailureData.getPaymentReference(),
                        paymentFailureData.getAmount(),
                        paymentFailureData.getFailureReason()
                )
        );
    }

    @Test
    void testSendBookingConfirmationEmailWithNullValues() {
        assertDoesNotThrow(() ->
                emailService.sendBookingConfirmationEmail(
                        null, null, null, null, null, null, null
                )
        );
    }

    @Test
    void testSendPaymentReceiptEmailWithNullValues() {
        assertDoesNotThrow(() ->
                emailService.sendPaymentReceiptEmail(
                        null, null, null, null, null
                )
        );
    }

    @Test
    void testFormatSeats() {
        String formatted = emailService.formatSeats(Arrays.asList("A1", "A2", "A3"));
        assertEquals("A1, A2, A3", formatted);
    }

    @Test
    void testFormatSeatsWithEmptyList() {
        String formatted = emailService.formatSeats(Arrays.asList());
        assertEquals("", formatted);
    }

    @Test
    void testFormatSeatsWithNullList() {
        String formatted = emailService.formatSeats(null);
        assertEquals("", formatted);
    }

    @Test
    void testFormatAmount() {
        String formatted = emailService.formatAmount(new BigDecimal("900.00"));
        assertTrue(formatted.contains("900"));
    }

    @Test
    void testFormatAmountWithNull() {
        String formatted = emailService.formatAmount(null);
        assertEquals("0.00", formatted);
    }

    @Test
    void testFormatDateTime() {
        LocalDateTime dateTime = LocalDateTime.of(2024, 11, 16, 18, 30);
        String formatted = emailService.formatDateTime(dateTime);
        assertNotNull(formatted);
        assertTrue(formatted.length() > 0);
    }

    @Test
    void testFormatDateTimeWithNull() {
        String formatted = emailService.formatDateTime(null);
        assertEquals("", formatted);
    }
}
