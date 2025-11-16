package com.bookmyshow.gateway.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class JwtUtilTest {

    private JwtUtil jwtUtil;
    private String secret;
    private Long expiration;

    @BeforeEach
    void setUp() {
        jwtUtil = new JwtUtil();
        secret = "bookmyshow-super-secret-key-change-in-production-minimum-256-bits-required-for-hmac-sha256-algorithm";
        expiration = 86400000L;

        ReflectionTestUtils.setField(jwtUtil, "secret", secret);
        ReflectionTestUtils.setField(jwtUtil, "expiration", expiration);
    }

    private String generateTestToken(String subject, Long userId, String role, List<String> authorities, long expirationTime) {
        SecretKey key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));

        return Jwts.builder()
                .subject(subject)
                .claim("userId", userId)
                .claim("role", role)
                .claim("authorities", authorities)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expirationTime))
                .signWith(key)
                .compact();
    }

    @Test
    void testValidateToken_ValidToken() {
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", List.of("ROLE_USER"), expiration);

        boolean isValid = jwtUtil.validateToken(token);

        assertThat(isValid).isTrue();
    }

    @Test
    void testValidateToken_ExpiredToken() {
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", List.of("ROLE_USER"), -1000L);

        boolean isValid = jwtUtil.validateToken(token);

        assertThat(isValid).isFalse();
    }

    @Test
    void testValidateToken_InvalidToken() {
        String invalidToken = "invalid.token.here";

        boolean isValid = jwtUtil.validateToken(invalidToken);

        assertThat(isValid).isFalse();
    }

    @Test
    void testGetUsernameFromToken() {
        String username = "testuser@example.com";
        String token = generateTestToken(username, 1L, "CUSTOMER", List.of("ROLE_USER"), expiration);

        String extractedUsername = jwtUtil.getUsernameFromToken(token);

        assertThat(extractedUsername).isEqualTo(username);
    }

    @Test
    void testGetUserIdFromToken() {
        Long userId = 123L;
        String token = generateTestToken("testuser@example.com", userId, "CUSTOMER", List.of("ROLE_USER"), expiration);

        Long extractedUserId = jwtUtil.getUserIdFromToken(token);

        assertThat(extractedUserId).isEqualTo(userId);
    }

    @Test
    void testGetRoleFromToken() {
        String role = "ADMIN";
        String token = generateTestToken("admin@example.com", 1L, role, List.of("ROLE_ADMIN"), expiration);

        String extractedRole = jwtUtil.getRoleFromToken(token);

        assertThat(extractedRole).isEqualTo(role);
    }

    @Test
    void testGetAuthoritiesFromToken() {
        List<String> authorities = List.of("ROLE_USER", "ROLE_CUSTOMER");
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", authorities, expiration);

        List<String> extractedAuthorities = jwtUtil.getAuthoritiesFromToken(token);

        assertThat(extractedAuthorities).containsExactlyElementsOf(authorities);
    }

    @Test
    void testIsTokenExpired_NotExpired() {
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", List.of("ROLE_USER"), expiration);

        boolean isExpired = jwtUtil.isTokenExpired(token);

        assertThat(isExpired).isFalse();
    }

    @Test
    void testIsTokenExpired_Expired() {
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", List.of("ROLE_USER"), -1000L);

        boolean isExpired = jwtUtil.isTokenExpired(token);

        assertThat(isExpired).isTrue();
    }

    @Test
    void testGetAllClaimsFromToken() {
        String username = "testuser@example.com";
        Long userId = 1L;
        String role = "CUSTOMER";
        List<String> authorities = List.of("ROLE_USER");

        String token = generateTestToken(username, userId, role, authorities, expiration);

        Claims claims = jwtUtil.getAllClaimsFromToken(token);

        assertThat(claims.getSubject()).isEqualTo(username);
        assertThat(claims.get("userId", Long.class)).isEqualTo(userId);
        assertThat(claims.get("role", String.class)).isEqualTo(role);
        assertThat(claims.get("authorities", List.class)).containsExactlyElementsOf(authorities);
    }

    @Test
    void testGetExpirationDateFromToken() {
        String token = generateTestToken("testuser@example.com", 1L, "CUSTOMER", List.of("ROLE_USER"), expiration);

        Date expirationDate = jwtUtil.getExpirationDateFromToken(token);

        assertThat(expirationDate).isNotNull();
        assertThat(expirationDate).isAfter(new Date());
    }
}
