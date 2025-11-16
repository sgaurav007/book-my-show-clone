package com.bookmyshow.booking.integration;

import com.bookmyshow.booking.dto.BookingResponse;
import com.bookmyshow.booking.dto.LockSeatsRequest;
import com.bookmyshow.booking.dto.SeatInfo;
import com.bookmyshow.booking.model.Booking;
import com.bookmyshow.booking.model.BookingStatus;
import com.bookmyshow.booking.repository.BookingRepository;
import com.bookmyshow.booking.service.BookingService;
import com.bookmyshow.booking.service.SeatLockService;
import com.redis.testcontainers.RedisContainer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@SpringBootTest
@Testcontainers
class BookingServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("booking_db")
            .withUsername("postgres")
            .withPassword("postgres");

    @Container
    static RedisContainer redis = new RedisContainer(DockerImageName.parse("redis:7-alpine"))
            .withExposedPorts(6379);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.data.redis.host", redis::getHost);
        registry.add("spring.data.redis.port", () -> redis.getMappedPort(6379));
    }

    @Autowired
    private BookingService bookingService;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private SeatLockService seatLockService;

    @MockBean
    private KafkaTemplate<String, Object> kafkaTemplate;

    @BeforeEach
    void setUp() {
        bookingRepository.deleteAll();
        when(kafkaTemplate.send(anyString(), any())).thenReturn(null);
    }

    @Test
    void testLockSeatsIntegration() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        SeatInfo seat2 = new SeatInfo(2L, "A2", new BigDecimal("250.00"));
        LockSeatsRequest request = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1, seat2));

        BookingResponse response = bookingService.lockSeats(request);

        assertNotNull(response);
        assertNotNull(response.getId());
        assertNotNull(response.getBookingReference());
        assertTrue(response.getBookingReference().startsWith("BK"));
        assertEquals(BookingStatus.PENDING, response.getBookingStatus());
        assertEquals(new BigDecimal("500.00"), response.getTotalAmount());
        assertEquals(2, response.getSeats().size());

        assertTrue(seatLockService.isLocked(200L, 1L));
        assertTrue(seatLockService.isLocked(200L, 2L));
    }

    @Test
    void testConfirmBookingIntegration() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        LockSeatsRequest request = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1));

        BookingResponse lockedBooking = bookingService.lockSeats(request);

        BookingResponse confirmed = bookingService.confirmBooking(lockedBooking.getId(), 999L);

        assertNotNull(confirmed);
        assertEquals(BookingStatus.CONFIRMED, confirmed.getBookingStatus());
        assertEquals(999L, confirmed.getPaymentId());
    }

    @Test
    void testCancelBookingIntegration() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        LockSeatsRequest request = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1));

        BookingResponse lockedBooking = bookingService.lockSeats(request);
        assertTrue(seatLockService.isLocked(200L, 1L));

        bookingService.cancelBooking(lockedBooking.getId());

        Booking cancelled = bookingRepository.findById(lockedBooking.getId()).orElseThrow();
        assertEquals(BookingStatus.CANCELLED, cancelled.getBookingStatus());

        assertFalse(seatLockService.isLocked(200L, 1L));
    }

    @Test
    void testGetBookingsByUserIdIntegration() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        LockSeatsRequest request1 = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1));
        bookingService.lockSeats(request1);

        SeatInfo seat2 = new SeatInfo(2L, "A2", new BigDecimal("300.00"));
        LockSeatsRequest request2 = new LockSeatsRequest(100L, 201L, Arrays.asList(seat2));
        bookingService.lockSeats(request2);

        List<BookingResponse> bookings = bookingService.getBookingsByUserId(100L);

        assertEquals(2, bookings.size());
    }

    @Test
    void testRedisLockPreventsDoubleBooking() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        LockSeatsRequest request1 = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1));

        BookingResponse booking1 = bookingService.lockSeats(request1);
        assertNotNull(booking1);

        LockSeatsRequest request2 = new LockSeatsRequest(101L, 200L, Arrays.asList(seat1));

        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            bookingService.lockSeats(request2);
        });

        assertTrue(exception.getMessage().contains("lock"));
    }

    @Test
    void testBookingExpiryTime() {
        SeatInfo seat1 = new SeatInfo(1L, "A1", new BigDecimal("250.00"));
        LockSeatsRequest request = new LockSeatsRequest(100L, 200L, Arrays.asList(seat1));

        BookingResponse response = bookingService.lockSeats(request);

        assertNotNull(response.getExpiresAt());
        assertTrue(response.getExpiresAt().isAfter(response.getCreatedAt()));
    }
}
