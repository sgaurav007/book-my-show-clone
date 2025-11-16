package com.bookmyshow.notification.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@Slf4j
public class EmailService {

    private static final DateTimeFormatter DATE_TIME_FORMATTER =
            DateTimeFormatter.ofPattern("dd MMM yyyy, hh:mm a");

    public void sendBookingConfirmationEmail(String email, String bookingReference,
                                            String movieTitle, String theaterName,
                                            LocalDateTime showDateTime, List<String> seats,
                                            BigDecimal totalAmount) {
        log.info("==========================================================");
        log.info("SENDING BOOKING CONFIRMATION EMAIL");
        log.info("==========================================================");
        log.info("To: {}", email);
        log.info("Subject: Booking Confirmed - {}", bookingReference);
        log.info("");
        log.info("Dear Customer,");
        log.info("");
        log.info("Your booking has been confirmed!");
        log.info("");
        log.info("Booking Reference: {}", bookingReference);
        log.info("Movie: {}", movieTitle);
        log.info("Theater: {}", theaterName);
        log.info("Show Time: {}", formatDateTime(showDateTime));
        log.info("Seats: {}", formatSeats(seats));
        log.info("Total Amount: Rs. {}", formatAmount(totalAmount));
        log.info("");
        log.info("Please arrive 15 minutes before the show time.");
        log.info("Show this email or your booking reference at the counter.");
        log.info("");
        log.info("Thank you for choosing BookMyShow!");
        log.info("==========================================================");
    }

    public void sendBookingCancellationEmail(String email, String bookingReference,
                                            String movieTitle, String theaterName,
                                            LocalDateTime showDateTime, List<String> seats,
                                            BigDecimal refundAmount) {
        log.info("==========================================================");
        log.info("SENDING BOOKING CANCELLATION EMAIL");
        log.info("==========================================================");
        log.info("To: {}", email);
        log.info("Subject: Booking Cancelled - {}", bookingReference);
        log.info("");
        log.info("Dear Customer,");
        log.info("");
        log.info("Your booking has been cancelled.");
        log.info("");
        log.info("Booking Reference: {}", bookingReference);
        log.info("Movie: {}", movieTitle);
        log.info("Theater: {}", theaterName);
        log.info("Show Time: {}", formatDateTime(showDateTime));
        log.info("Seats: {}", formatSeats(seats));
        log.info("Refund Amount: Rs. {}", formatAmount(refundAmount));
        log.info("");
        log.info("The refund will be processed within 5-7 business days.");
        log.info("");
        log.info("We hope to serve you again soon!");
        log.info("==========================================================");
    }

    public void sendPaymentReceiptEmail(String email, String paymentReference,
                                       BigDecimal amount, String currency,
                                       String paymentMethod) {
        log.info("==========================================================");
        log.info("SENDING PAYMENT RECEIPT EMAIL");
        log.info("==========================================================");
        log.info("To: {}", email);
        log.info("Subject: Payment Receipt - {}", paymentReference);
        log.info("");
        log.info("Dear Customer,");
        log.info("");
        log.info("We have received your payment successfully.");
        log.info("");
        log.info("Payment Reference: {}", paymentReference);
        log.info("Amount: {} {}", formatAmount(amount), currency);
        log.info("Payment Method: {}", paymentMethod);
        log.info("Transaction Date: {}", formatDateTime(LocalDateTime.now()));
        log.info("");
        log.info("This is your official payment receipt.");
        log.info("Please keep it for your records.");
        log.info("");
        log.info("Thank you for your payment!");
        log.info("==========================================================");
    }

    public void sendPaymentFailureEmail(String email, String paymentReference,
                                       BigDecimal amount, String failureReason) {
        log.info("==========================================================");
        log.info("SENDING PAYMENT FAILURE EMAIL");
        log.info("==========================================================");
        log.info("To: {}", email);
        log.info("Subject: Payment Failed - {}", paymentReference);
        log.info("");
        log.info("Dear Customer,");
        log.info("");
        log.info("Unfortunately, your payment could not be processed.");
        log.info("");
        log.info("Payment Reference: {}", paymentReference);
        log.info("Amount: Rs. {}", formatAmount(amount));
        log.info("Failure Reason: {}", failureReason);
        log.info("");
        log.info("Please try again with a different payment method or contact your bank.");
        log.info("Your booking is still on hold and will expire in 15 minutes.");
        log.info("");
        log.info("For assistance, please contact our support team.");
        log.info("==========================================================");
    }

    public String formatSeats(List<String> seats) {
        if (seats == null || seats.isEmpty()) {
            return "";
        }
        return String.join(", ", seats);
    }

    public String formatAmount(BigDecimal amount) {
        if (amount == null) {
            return "0.00";
        }
        return amount.toString();
    }

    public String formatDateTime(LocalDateTime dateTime) {
        if (dateTime == null) {
            return "";
        }
        return dateTime.format(DATE_TIME_FORMATTER);
    }
}
