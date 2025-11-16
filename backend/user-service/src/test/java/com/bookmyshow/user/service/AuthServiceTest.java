package com.bookmyshow.user.service;

import com.bookmyshow.common.exception.InvalidTokenException;
import com.bookmyshow.user.dto.LoginRequest;
import com.bookmyshow.user.dto.LoginResponse;
import com.bookmyshow.user.entity.RefreshToken;
import com.bookmyshow.user.entity.User;
import com.bookmyshow.user.repository.RefreshTokenRepository;
import com.bookmyshow.user.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @Mock
    private UserService userService;

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @InjectMocks
    private AuthService authService;

    private LoginRequest loginRequest;
    private User user;
    private Authentication authentication;

    @BeforeEach
    void setUp() {
        loginRequest = new LoginRequest("test@example.com", "Password@123");

        user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        user.setFirstName("John");
        user.setLastName("Doe");
        user.setRole("CUSTOMER");
        user.setIsActive(true);

        authentication = mock(Authentication.class);
    }

    @Test
    void login_Success() {
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
            .thenReturn(authentication);
        when(userService.getUserByEmail("test@example.com")).thenReturn(user);
        when(jwtTokenProvider.generateAccessToken(anyString(), anyLong())).thenReturn("accessToken");
        when(jwtTokenProvider.generateRefreshToken()).thenReturn("refreshToken");
        when(jwtTokenProvider.getAccessTokenExpiration()).thenReturn(3600000L);
        when(jwtTokenProvider.getRefreshTokenExpiration()).thenReturn(86400000L);
        when(refreshTokenRepository.save(any(RefreshToken.class))).thenReturn(new RefreshToken());

        LoginResponse response = authService.login(loginRequest);

        assertNotNull(response);
        assertEquals("accessToken", response.getAccessToken());
        assertEquals("refreshToken", response.getRefreshToken());
        assertEquals("Bearer", response.getTokenType());
        assertNotNull(response.getUser());

        verify(authenticationManager).authenticate(any(UsernamePasswordAuthenticationToken.class));
        verify(userService).getUserByEmail("test@example.com");
        verify(userService).updateLastLogin(1L);
        verify(refreshTokenRepository).save(any(RefreshToken.class));
    }

    @Test
    void login_InvalidCredentials() {
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
            .thenThrow(new BadCredentialsException("Invalid credentials"));

        assertThrows(BadCredentialsException.class, () -> authService.login(loginRequest));

        verify(authenticationManager).authenticate(any(UsernamePasswordAuthenticationToken.class));
        verify(userService, never()).getUserByEmail(anyString());
    }

    @Test
    void refreshAccessToken_Success() {
        String refreshTokenString = "validRefreshToken";
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.setId(1L);
        refreshToken.setUserId(1L);
        refreshToken.setToken(refreshTokenString);
        refreshToken.setExpiresAt(LocalDateTime.now().plusDays(1));

        when(refreshTokenRepository.findByToken(refreshTokenString))
            .thenReturn(Optional.of(refreshToken));
        when(userService.getUserById(1L)).thenReturn(user);
        when(jwtTokenProvider.generateAccessToken(anyString(), anyLong())).thenReturn("newAccessToken");
        when(jwtTokenProvider.getAccessTokenExpiration()).thenReturn(3600000L);

        LoginResponse response = authService.refreshAccessToken(refreshTokenString);

        assertNotNull(response);
        assertEquals("newAccessToken", response.getAccessToken());
        assertEquals(refreshTokenString, response.getRefreshToken());

        verify(refreshTokenRepository).findByToken(refreshTokenString);
        verify(userService).getUserById(1L);
    }

    @Test
    void refreshAccessToken_InvalidToken() {
        when(refreshTokenRepository.findByToken(anyString())).thenReturn(Optional.empty());

        assertThrows(InvalidTokenException.class,
            () -> authService.refreshAccessToken("invalidToken"));

        verify(refreshTokenRepository).findByToken("invalidToken");
    }

    @Test
    void refreshAccessToken_ExpiredToken() {
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.setExpiresAt(LocalDateTime.now().minusDays(1));

        when(refreshTokenRepository.findByToken(anyString())).thenReturn(Optional.of(refreshToken));

        assertThrows(InvalidTokenException.class,
            () -> authService.refreshAccessToken("expiredToken"));

        verify(refreshTokenRepository).findByToken("expiredToken");
        verify(refreshTokenRepository).delete(refreshToken);
    }

    @Test
    void logout_Success() {
        when(refreshTokenRepository.deleteByToken(anyString())).thenReturn(1);

        authService.logout("refreshToken");

        verify(refreshTokenRepository).deleteByToken("refreshToken");
    }
}
