package com.bookmyshow.notification.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@Slf4j
public class SmsService {

    private static final int SMS_MAX_LENGTH = 160;
    private static final DateTimeFormatter DATE_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("dd MMM, hh:mm a");

    public void sendBookingConfirmationSms(String phoneNumber, String bookingReference,
                                          String movieTitle, LocalDateTime showDateTime) {
        String message = String.format(
                "BookMyShow: Booking confirmed! Ref: %s, Movie: %s, Time: %s. Show this SMS at counter.",
                bookingReference, movieTitle, formatDateTime(showDateTime)
        );

        String truncatedMessage = truncateSms(message);

        log.info("==========================================================");
        log.info("SENDING BOOKING CONFIRMATION SMS");
        log.info("==========================================================");
        log.info("To: {}", formatPhoneNumber(phoneNumber));
        log.info("Message: {}", truncatedMessage);
        log.info("==========================================================");
    }

    public void sendBookingCancellationSms(String phoneNumber, String bookingReference,
                                          String movieTitle, BigDecimal refundAmount) {
        String message = String.format(
                "BookMyShow: Booking %s cancelled. Movie: %s. Refund of Rs. %s will be processed in 5-7 days.",
                bookingReference, movieTitle, refundAmount
        );

        String truncatedMessage = truncateSms(message);

        log.info("==========================================================");
        log.info("SENDING BOOKING CANCELLATION SMS");
        log.info("==========================================================");
        log.info("To: {}", formatPhoneNumber(phoneNumber));
        log.info("Message: {}", truncatedMessage);
        log.info("==========================================================");
    }

    public void sendPaymentSuccessSms(String phoneNumber, String paymentReference,
                                     BigDecimal amount) {
        String message = String.format(
                "BookMyShow: Payment of Rs. %s received successfully. Ref: %s. Thank you!",
                amount, paymentReference
        );

        String truncatedMessage = truncateSms(message);

        log.info("==========================================================");
        log.info("SENDING PAYMENT SUCCESS SMS");
        log.info("==========================================================");
        log.info("To: {}", formatPhoneNumber(phoneNumber));
        log.info("Message: {}", truncatedMessage);
        log.info("==========================================================");
    }

    public void sendPaymentFailureSms(String phoneNumber, String paymentReference,
                                     BigDecimal amount, String failureReason) {
        String message = String.format(
                "BookMyShow: Payment of Rs. %s failed. Ref: %s. Reason: %s. Please try again.",
                amount, paymentReference, failureReason
        );

        String truncatedMessage = truncateSms(message);

        log.info("==========================================================");
        log.info("SENDING PAYMENT FAILURE SMS");
        log.info("==========================================================");
        log.info("To: {}", formatPhoneNumber(phoneNumber));
        log.info("Message: {}", truncatedMessage);
        log.info("==========================================================");
    }

    public String truncateSms(String message) {
        if (message == null) {
            return "";
        }
        if (message.length() <= SMS_MAX_LENGTH) {
            return message;
        }
        return message.substring(0, SMS_MAX_LENGTH - 3) + "...";
    }

    public String formatPhoneNumber(String phoneNumber) {
        if (phoneNumber == null) {
            return "";
        }
        if (phoneNumber.length() <= 6) {
            return phoneNumber;
        }
        int visibleDigits = 4;
        int maskedLength = phoneNumber.length() - visibleDigits;
        return "*".repeat(maskedLength) + phoneNumber.substring(maskedLength);
    }

    private String formatDateTime(LocalDateTime dateTime) {
        if (dateTime == null) {
            return "";
        }
        return dateTime.format(DATE_TIME_FORMATTER);
    }
}
