package com.bookmyshow.booking.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@Slf4j
public class SeatLockService {

    private final RedisTemplate<String, Object> redisTemplate;
    private static final int LOCK_DURATION_MINUTES = 15;
    private static final String LOCK_KEY_PREFIX = "seat:lock";

    public SeatLockService(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public boolean lockSeats(Long showId, List<Long> seatIds, Long userId) {
        if (seatIds == null || seatIds.isEmpty()) {
            log.warn("Cannot lock empty seat list");
            return false;
        }

        List<String> lockKeys = seatIds.stream()
                .map(seatId -> getLockKey(showId, seatId))
                .collect(Collectors.toList());

        String luaScript =
                "for i, key in ipairs(KEYS) do " +
                "  if redis.call('EXISTS', key) == 1 then " +
                "    return 0 " +
                "  end " +
                "end " +
                "for i, key in ipairs(KEYS) do " +
                "  redis.call('SETEX', key, ARGV[1], ARGV[2]) " +
                "end " +
                "return 1";

        DefaultRedisScript<Long> script = new DefaultRedisScript<>(luaScript, Long.class);

        Long result = redisTemplate.execute(
                script,
                lockKeys,
                String.valueOf(LOCK_DURATION_MINUTES * 60),
                userId.toString()
        );

        boolean locked = result != null && result == 1L;
        if (locked) {
            log.info("Successfully locked {} seats for show {} by user {}", seatIds.size(), showId, userId);
        } else {
            log.warn("Failed to lock seats for show {} by user {}", showId, userId);
        }

        return locked;
    }

    public void unlockSeats(Long showId, List<Long> seatIds) {
        if (seatIds == null || seatIds.isEmpty()) {
            return;
        }

        seatIds.forEach(seatId -> {
            String lockKey = getLockKey(showId, seatId);
            redisTemplate.delete(lockKey);
        });

        log.info("Unlocked {} seats for show {}", seatIds.size(), showId);
    }

    public boolean extendLock(Long showId, Long seatId) {
        String lockKey = getLockKey(showId, seatId);
        Boolean result = redisTemplate.expire(lockKey, LOCK_DURATION_MINUTES, TimeUnit.MINUTES);
        return result != null && result;
    }

    public boolean isLocked(Long showId, Long seatId) {
        String lockKey = getLockKey(showId, seatId);
        Boolean exists = redisTemplate.hasKey(lockKey);
        return exists != null && exists;
    }

    public String getLockKey(Long showId, Long seatId) {
        return String.format("%s:%d:%d", LOCK_KEY_PREFIX, showId, seatId);
    }
}
