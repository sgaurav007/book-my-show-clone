package com.bookmyshow.booking.service;

import com.bookmyshow.booking.dto.BookingResponse;
import com.bookmyshow.booking.dto.LockSeatsRequest;
import com.bookmyshow.booking.dto.SeatInfo;
import com.bookmyshow.booking.kafka.BookingEventPublisher;
import com.bookmyshow.booking.model.Booking;
import com.bookmyshow.booking.model.BookingSeat;
import com.bookmyshow.booking.model.BookingStatus;
import com.bookmyshow.booking.repository.BookingRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingServiceTest {

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private SeatLockService seatLockService;

    @Mock
    private BookingEventPublisher eventPublisher;

    @InjectMocks
    private BookingService bookingService;

    private LockSeatsRequest lockRequest;
    private Booking booking;

    @BeforeEach
    void setUp() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        SeatInfo seat2 = new SeatInfo(2L, "A2", new BigDecimal("250.00"));
        lockRequest = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1, seat2));

        booking = new Booking();
        booking.setId(1L);
        booking.setBookingReference("BK123456");
        booking.setUserId(100L);
        booking.setShowId(200L);
        booking.setTotalAmount(new BigDecimal("500.00"));
        booking.setBookingStatus(BookingStatus.PENDING);
        booking.setExpiresAt(LocalDateTime.now().plusMinutes(15));
    }

    @Test
    void testLockSeatsSuccess() {
        when(seatLockService.lockSeats(anyLong(), anyList(), anyLong())).thenReturn(true);
        when(bookingRepository.save(any(Booking.class))).thenReturn(booking);

        BookingResponse response = bookingService.lockSeats(lockRequest);

        assertNotNull(response);
        assertEquals(booking.getId(), response.getId());
        assertEquals(booking.getBookingReference(), response.getBookingReference());
        assertEquals(BookingStatus.PENDING, response.getBookingStatus());

        verify(seatLockService, times(1)).lockSeats(eq(200L), anyList(), eq(100L));
        verify(bookingRepository, times(1)).save(any(Booking.class));
        verify(eventPublisher, times(1)).publishBookingCreated(
                anyLong(), anyString(), anyLong(), anyLong(), any(BigDecimal.class),
                anyList(), any(LocalDateTime.class), any(LocalDateTime.class)
        );
    }

    @Test
    void testLockSeatsFailedDueToRedisLock() {
        when(seatLockService.lockSeats(anyLong(), anyList(), anyLong())).thenReturn(false);

        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            bookingService.lockSeats(lockRequest);
        });

        assertTrue(exception.getMessage().contains("seat"));
        verify(bookingRepository, never()).save(any(Booking.class));
        verify(eventPublisher, never()).publishBookingCreated(
                anyLong(), anyString(), anyLong(), anyLong(), any(BigDecimal.class),
                anyList(), any(LocalDateTime.class), any(LocalDateTime.class)
        );
    }

    @Test
    void testConfirmBookingSuccess() {
        booking.setSeats(Arrays.asList(
                new BookingSeat(1L, booking, 1L, "A1", new BigDecimal("250.00")),
                new BookingSeat(2L, booking, 2L, "A2", new BigDecimal("250.00"))
        ));

        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));
        when(bookingRepository.save(any(Booking.class))).thenReturn(booking);

        BookingResponse response = bookingService.confirmBooking(1L, 999L);

        assertNotNull(response);
        assertEquals(BookingStatus.CONFIRMED, response.getBookingStatus());
        assertEquals(999L, response.getPaymentId());

        verify(bookingRepository, times(1)).findById(1L);
        verify(bookingRepository, times(1)).save(any(Booking.class));
        verify(eventPublisher, times(1)).publishBookingConfirmed(
                anyLong(), anyString(), anyLong(), anyLong(), anyLong(),
                any(BigDecimal.class), any(LocalDateTime.class)
        );
    }

    @Test
    void testConfirmBookingNotFound() {
        when(bookingRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            bookingService.confirmBooking(1L, 999L);
        });

        verify(bookingRepository, never()).save(any(Booking.class));
    }

    @Test
    void testConfirmBookingAlreadyConfirmed() {
        booking.setBookingStatus(BookingStatus.CONFIRMED);
        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));

        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            bookingService.confirmBooking(1L, 999L);
        });

        assertTrue(exception.getMessage().contains("already"));
        verify(bookingRepository, never()).save(any(Booking.class));
    }

    @Test
    void testCancelBookingSuccess() {
        booking.setSeats(Arrays.asList(
                new BookingSeat(1L, booking, 1L, "A1", new BigDecimal("250.00")),
                new BookingSeat(2L, booking, 2L, "A2", new BigDecimal("250.00"))
        ));

        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));
        when(bookingRepository.save(any(Booking.class))).thenReturn(booking);

        bookingService.cancelBooking(1L);

        ArgumentCaptor<Booking> bookingCaptor = ArgumentCaptor.forClass(Booking.class);
        verify(bookingRepository, times(1)).save(bookingCaptor.capture());

        Booking savedBooking = bookingCaptor.getValue();
        assertEquals(BookingStatus.CANCELLED, savedBooking.getBookingStatus());

        verify(seatLockService, times(1)).unlockSeats(eq(200L), anyList());
        verify(eventPublisher, times(1)).publishBookingCancelled(
                anyLong(), anyString(), anyLong(), anyLong(), anyList(),
                anyString(), any(LocalDateTime.class)
        );
    }

    @Test
    void testCancelBookingNotFound() {
        when(bookingRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            bookingService.cancelBooking(1L);
        });
    }

    @Test
    void testCancelBookingAlreadyCancelled() {
        booking.setBookingStatus(BookingStatus.CANCELLED);
        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));

        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            bookingService.cancelBooking(1L);
        });

        assertTrue(exception.getMessage().contains("already"));
    }

    @Test
    void testGetBookingByIdSuccess() {
        booking.setSeats(Arrays.asList(
                new BookingSeat(1L, booking, 1L, "A1", new BigDecimal("250.00"))
        ));

        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));

        BookingResponse response = bookingService.getBookingById(1L);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("BK123456", response.getBookingReference());
    }

    @Test
    void testGetBookingByIdNotFound() {
        when(bookingRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            bookingService.getBookingById(1L);
        });
    }

    @Test
    void testGetBookingsByUserId() {
        Booking booking2 = new Booking();
        booking2.setId(2L);
        booking2.setBookingReference("BK789012");
        booking2.setUserId(100L);
        booking2.setShowId(201L);
        booking2.setTotalAmount(new BigDecimal("300.00"));
        booking2.setBookingStatus(BookingStatus.CONFIRMED);

        when(bookingRepository.findByUserId(100L)).thenReturn(Arrays.asList(booking, booking2));

        List<BookingResponse> responses = bookingService.getBookingsByUserId(100L);

        assertNotNull(responses);
        assertEquals(2, responses.size());
        verify(bookingRepository, times(1)).findByUserId(100L);
    }

    @Test
    void testCalculateTotalAmount() {
        BigDecimal total = bookingService.calculateTotalAmount(lockRequest.getSeats());

        assertEquals(new BigDecimal("500.00"), total);
    }

    @Test
    void testGenerateBookingReference() {
        String reference = bookingService.generateBookingReference();

        assertNotNull(reference);
        assertTrue(reference.startsWith("BK"));
        assertEquals(14, reference.length());
    }
}
