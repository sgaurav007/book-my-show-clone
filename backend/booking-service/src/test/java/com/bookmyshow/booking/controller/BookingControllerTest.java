package com.bookmyshow.booking.controller;

import com.bookmyshow.booking.dto.BookingResponse;
import com.bookmyshow.booking.dto.ConfirmBookingRequest;
import com.bookmyshow.booking.dto.LockSeatsRequest;
import com.bookmyshow.booking.dto.SeatInfo;
import com.bookmyshow.booking.model.BookingStatus;
import com.bookmyshow.booking.service.BookingService;
import com.bookmyshow.common.exception.ResourceNotFoundException;
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
import java.util.Collections;
import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BookingController.class)
class BookingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private BookingService bookingService;

    private LockSeatsRequest lockRequest;
    private BookingResponse bookingResponse;

    @BeforeEach
    void setUp() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        SeatInfo seat2 = new SeatInfo(2L, "A2", new BigDecimal("250.00"));
        lockRequest = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1, seat2));

        bookingResponse = new BookingResponse();
        bookingResponse.setId(1L);
        bookingResponse.setBookingReference("BK123456");
        bookingResponse.setUserId(100L);
        bookingResponse.setShowId(200L);
        bookingResponse.setTotalAmount(new BigDecimal("500.00"));
        bookingResponse.setBookingStatus(BookingStatus.PENDING);
        bookingResponse.setExpiresAt(LocalDateTime.now().plusMinutes(15));
        bookingResponse.setCreatedAt(LocalDateTime.now());
        bookingResponse.setUpdatedAt(LocalDateTime.now());
        bookingResponse.setSeats(Collections.emptyList());
    }

    @Test
    void testLockSeatsSuccess() throws Exception {
        when(bookingService.lockSeats(any(LockSeatsRequest.class))).thenReturn(bookingResponse);

        mockMvc.perform(post("/api/bookings/lock-seats")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(lockRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(1))
                .andExpect(jsonPath("$.data.bookingReference").value("BK123456"))
                .andExpect(jsonPath("$.data.bookingStatus").value("PENDING"));

        verify(bookingService, times(1)).lockSeats(any(LockSeatsRequest.class));
    }

    @Test
    void testLockSeatsWithInvalidRequest() throws Exception {
        LockSeatsRequest invalidRequest = new LockSeatsRequest(null, null, null);

        mockMvc.perform(post("/api/bookings/lock-seats")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());

        verify(bookingService, never()).lockSeats(any(LockSeatsRequest.class));
    }

    @Test
    void testConfirmBookingSuccess() throws Exception {
        bookingResponse.setBookingStatus(BookingStatus.CONFIRMED);
        bookingResponse.setPaymentId(999L);

        when(bookingService.confirmBooking(1L, 999L)).thenReturn(bookingResponse);

        ConfirmBookingRequest confirmRequest = new ConfirmBookingRequest(999L);

        mockMvc.perform(post("/api/bookings/1/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(confirmRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.bookingStatus").value("CONFIRMED"))
                .andExpect(jsonPath("$.data.paymentId").value(999));

        verify(bookingService, times(1)).confirmBooking(1L, 999L);
    }

    @Test
    void testConfirmBookingNotFound() throws Exception {
        when(bookingService.confirmBooking(anyLong(), anyLong()))
                .thenThrow(new ResourceNotFoundException("Booking not found"));

        ConfirmBookingRequest confirmRequest = new ConfirmBookingRequest(999L);

        mockMvc.perform(post("/api/bookings/999/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(confirmRequest)))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetBookingByIdSuccess() throws Exception {
        when(bookingService.getBookingById(1L)).thenReturn(bookingResponse);

        mockMvc.perform(get("/api/bookings/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(1))
                .andExpect(jsonPath("$.data.bookingReference").value("BK123456"));

        verify(bookingService, times(1)).getBookingById(1L);
    }

    @Test
    void testGetBookingByIdNotFound() throws Exception {
        when(bookingService.getBookingById(999L))
                .thenThrow(new ResourceNotFoundException("Booking not found"));

        mockMvc.perform(get("/api/bookings/999"))
                .andExpect(status().isNotFound());
    }

    @Test
    void testCancelBookingSuccess() throws Exception {
        doNothing().when(bookingService).cancelBooking(1L);

        mockMvc.perform(delete("/api/bookings/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.message").value("Booking cancelled successfully"));

        verify(bookingService, times(1)).cancelBooking(1L);
    }

    @Test
    void testCancelBookingNotFound() throws Exception {
        doThrow(new ResourceNotFoundException("Booking not found"))
                .when(bookingService).cancelBooking(999L);

        mockMvc.perform(delete("/api/bookings/999"))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetBookingsByUserId() throws Exception {
        BookingResponse booking2 = new BookingResponse();
        booking2.setId(2L);
        booking2.setBookingReference("BK789012");
        booking2.setUserId(100L);

        List<BookingResponse> bookings = Arrays.asList(bookingResponse, booking2);

        when(bookingService.getBookingsByUserId(100L)).thenReturn(bookings);

        mockMvc.perform(get("/api/bookings/user/100"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.length()").value(2))
                .andExpect(jsonPath("$.data[0].bookingReference").value("BK123456"))
                .andExpect(jsonPath("$.data[1].bookingReference").value("BK789012"));

        verify(bookingService, times(1)).getBookingsByUserId(100L);
    }

    @Test
    void testGetBookingsByUserIdEmptyList() throws Exception {
        when(bookingService.getBookingsByUserId(100L)).thenReturn(Collections.emptyList());

        mockMvc.perform(get("/api/bookings/user/100"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.length()").value(0));
    }
}
