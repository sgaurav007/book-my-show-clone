package com.bookmyshow.notification.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class SmsServiceTest {

    @InjectMocks
    private SmsService smsService;

    @Test
    void testSendBookingConfirmationSms() {
        assertDoesNotThrow(() ->
                smsService.sendBookingConfirmationSms(
                        "+919876543210",
                        "BMS123456",
                        "Inception",
                        LocalDateTime.of(2024, 11, 16, 18, 0)
                )
        );
    }

    @Test
    void testSendBookingCancellationSms() {
        assertDoesNotThrow(() ->
                smsService.sendBookingCancellationSms(
                        "+919876543210",
                        "BMS123456",
                        "Inception",
                        new BigDecimal("900.00")
                )
        );
    }

    @Test
    void testSendPaymentSuccessSms() {
        assertDoesNotThrow(() ->
                smsService.sendPaymentSuccessSms(
                        "+919876543210",
                        "PAY123456",
                        new BigDecimal("900.00")
                )
        );
    }

    @Test
    void testSendPaymentFailureSms() {
        assertDoesNotThrow(() ->
                smsService.sendPaymentFailureSms(
                        "+919876543210",
                        "PAY789012",
                        new BigDecimal("900.00"),
                        "Insufficient funds"
                )
        );
    }

    @Test
    void testSendBookingConfirmationSmsWithNullValues() {
        assertDoesNotThrow(() ->
                smsService.sendBookingConfirmationSms(null, null, null, null)
        );
    }

    @Test
    void testSendPaymentSuccessSmsWithNullValues() {
        assertDoesNotThrow(() ->
                smsService.sendPaymentSuccessSms(null, null, null)
        );
    }

    @Test
    void testTruncateSms() {
        String longMessage = "This is a very long message that exceeds 160 characters. " +
                "It should be truncated to fit within the SMS limit of 160 characters. " +
                "This is additional text that should be cut off.";

        String truncated = smsService.truncateSms(longMessage);

        assertNotNull(truncated);
        assertTrue(truncated.length() <= 160);
    }

    @Test
    void testTruncateSmsWithShortMessage() {
        String shortMessage = "Short message";
        String truncated = smsService.truncateSms(shortMessage);

        assertEquals(shortMessage, truncated);
    }

    @Test
    void testTruncateSmsWithNullMessage() {
        String truncated = smsService.truncateSms(null);
        assertEquals("", truncated);
    }

    @Test
    void testFormatPhoneNumber() {
        String formatted = smsService.formatPhoneNumber("+919876543210");
        assertNotNull(formatted);
        assertTrue(formatted.contains("*"));
    }

    @Test
    void testFormatPhoneNumberWithNullValue() {
        String formatted = smsService.formatPhoneNumber(null);
        assertEquals("", formatted);
    }

    @Test
    void testFormatPhoneNumberWithShortNumber() {
        String formatted = smsService.formatPhoneNumber("+91123");
        assertEquals("+91123", formatted);
    }
}
