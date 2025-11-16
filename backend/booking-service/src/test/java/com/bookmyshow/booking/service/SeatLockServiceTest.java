package com.bookmyshow.booking.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SeatLockServiceTest {

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @InjectMocks
    private SeatLockService seatLockService;

    @Captor
    private ArgumentCaptor<List<String>> keysCaptor;

    @Captor
    private ArgumentCaptor<Object[]> argsCaptor;

    private Long showId;
    private List<Long> seatIds;
    private Long userId;

    @BeforeEach
    void setUp() {
        showId = 100L;
        seatIds = Arrays.asList(1L, 2L, 3L);
        userId = 999L;
    }

    @Test
    void testLockSeatsSuccess() {
        when(redisTemplate.execute(
                any(RedisScript.class),
                anyList(),
                any(Object[].class)
        )).thenReturn(1L);

        boolean result = seatLockService.lockSeats(showId, seatIds, userId);

        assertTrue(result);
        verify(redisTemplate, times(1)).execute(
                any(RedisScript.class),
                anyList(),
                any(Object[].class)
        );
    }

    @Test
    void testLockSeatsFailed() {
        when(redisTemplate.execute(
                any(RedisScript.class),
                anyList(),
                any(Object[].class)
        )).thenReturn(0L);

        boolean result = seatLockService.lockSeats(showId, seatIds, userId);

        assertFalse(result);
    }

    @Test
    void testLockSeatsWithEmptyList() {
        boolean result = seatLockService.lockSeats(showId, Arrays.asList(), userId);

        assertFalse(result);
        verify(redisTemplate, never()).execute(
                any(RedisScript.class),
                anyList(),
                any(Object[].class)
        );
    }

    @Test
    void testUnlockSeats() {
        seatLockService.unlockSeats(showId, seatIds);

        verify(redisTemplate, times(3)).delete(anyString());
    }

    @Test
    void testUnlockSeatsWithEmptyList() {
        seatLockService.unlockSeats(showId, Arrays.asList());

        verify(redisTemplate, never()).delete(anyString());
    }

    @Test
    void testGetLockKey() {
        String lockKey = seatLockService.getLockKey(showId, 1L);

        assertNotNull(lockKey);
        assertEquals("seat:lock:100:1", lockKey);
    }

    @Test
    void testLockSeatsHandlesNullResponse() {
        when(redisTemplate.execute(
                any(RedisScript.class),
                anyList(),
                any(Object[].class)
        )).thenReturn(null);

        boolean result = seatLockService.lockSeats(showId, seatIds, userId);

        assertFalse(result);
    }

    @Test
    void testExtendLock() {
        when(redisTemplate.expire(anyString(), anyLong(), any())).thenReturn(true);

        boolean result = seatLockService.extendLock(showId, 1L);

        assertTrue(result);
        verify(redisTemplate, times(1)).expire(eq("seat:lock:100:1"), anyLong(), any());
    }

    @Test
    void testExtendLockFailed() {
        when(redisTemplate.expire(anyString(), anyLong(), any())).thenReturn(false);

        boolean result = seatLockService.extendLock(showId, 1L);

        assertFalse(result);
    }

    @Test
    void testIsLocked() {
        when(redisTemplate.hasKey(anyString())).thenReturn(true);

        boolean result = seatLockService.isLocked(showId, 1L);

        assertTrue(result);
        verify(redisTemplate, times(1)).hasKey("seat:lock:100:1");
    }

    @Test
    void testIsNotLocked() {
        when(redisTemplate.hasKey(anyString())).thenReturn(false);

        boolean result = seatLockService.isLocked(showId, 1L);

        assertFalse(result);
    }
}
