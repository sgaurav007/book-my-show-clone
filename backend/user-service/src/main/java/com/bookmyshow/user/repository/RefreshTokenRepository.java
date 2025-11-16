package com.bookmyshow.user.repository;

import com.bookmyshow.user.entity.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {

    Optional<RefreshToken> findByToken(String token);

    int deleteByToken(String token);

    int deleteByUserId(Long userId);

    int deleteByExpiresAtBefore(LocalDateTime dateTime);
}
