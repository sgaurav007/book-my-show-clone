package com.bookmyshow.booking.controller;

import com.bookmyshow.booking.dto.BookingResponse;
import com.bookmyshow.booking.dto.ConfirmBookingRequest;
import com.bookmyshow.booking.dto.LockSeatsRequest;
import com.bookmyshow.booking.service.BookingService;
import com.bookmyshow.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/bookings")
@Slf4j
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @PostMapping("/lock-seats")
    public ResponseEntity<ApiResponse<BookingResponse>> lockSeats(@Valid @RequestBody LockSeatsRequest request) {
        log.info("Lock seats request for user: {} and show: {}", request.getUserId(), request.getShowId());
        BookingResponse response = bookingService.lockSeats(request);
        return ResponseEntity.ok(ApiResponse.success("Seats locked successfully", response));
    }

    @PostMapping("/{id}/confirm")
    public ResponseEntity<ApiResponse<BookingResponse>> confirmBooking(
            @PathVariable Long id,
            @Valid @RequestBody ConfirmBookingRequest request) {
        log.info("Confirm booking request for booking: {} with payment: {}", id, request.getPaymentId());
        BookingResponse response = bookingService.confirmBooking(id, request.getPaymentId());
        return ResponseEntity.ok(ApiResponse.success("Booking confirmed successfully", response));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<BookingResponse>> getBookingById(@PathVariable Long id) {
        log.info("Get booking request for id: {}", id);
        BookingResponse response = bookingService.getBookingById(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> cancelBooking(@PathVariable Long id) {
        log.info("Cancel booking request for id: {}", id);
        bookingService.cancelBooking(id);
        return ResponseEntity.ok(ApiResponse.success("Booking cancelled successfully", null));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<BookingResponse>>> getBookingsByUserId(@PathVariable Long userId) {
        log.info("Get bookings request for user: {}", userId);
        List<BookingResponse> responses = bookingService.getBookingsByUserId(userId);
        return ResponseEntity.ok(ApiResponse.success(responses));
    }
}
