package com.bookmyshow.user.service;

import com.bookmyshow.common.exception.InvalidTokenException;
import com.bookmyshow.user.dto.LoginRequest;
import com.bookmyshow.user.dto.LoginResponse;
import com.bookmyshow.user.dto.UserProfileResponse;
import com.bookmyshow.user.entity.RefreshToken;
import com.bookmyshow.user.entity.User;
import com.bookmyshow.user.repository.RefreshTokenRepository;
import com.bookmyshow.user.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Transactional
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserService userService;
    private final RefreshTokenRepository refreshTokenRepository;

    public LoginResponse login(LoginRequest request) {
        authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        User user = userService.getUserByEmail(request.getEmail());

        String accessToken = jwtTokenProvider.generateAccessToken(user.getEmail(), user.getId());
        String refreshToken = jwtTokenProvider.generateRefreshToken();

        saveRefreshToken(user.getId(), refreshToken);
        userService.updateLastLogin(user.getId());

        UserProfileResponse userProfile = new UserProfileResponse(
            user.getId(),
            user.getEmail(),
            user.getFirstName(),
            user.getLastName(),
            user.getPhoneNumber(),
            user.getRole(),
            user.getIsActive(),
            user.getIsEmailVerified(),
            user.getCreatedAt(),
            user.getLastLoginAt()
        );

        return new LoginResponse(
            accessToken,
            refreshToken,
            jwtTokenProvider.getAccessTokenExpiration(),
            userProfile
        );
    }

    public LoginResponse refreshAccessToken(String refreshTokenString) {
        RefreshToken refreshToken = refreshTokenRepository.findByToken(refreshTokenString)
            .orElseThrow(() -> new InvalidTokenException("Invalid refresh token"));

        if (refreshToken.getExpiresAt().isBefore(LocalDateTime.now())) {
            refreshTokenRepository.delete(refreshToken);
            throw new InvalidTokenException("Refresh token has expired");
        }

        User user = userService.getUserById(refreshToken.getUserId());

        String newAccessToken = jwtTokenProvider.generateAccessToken(user.getEmail(), user.getId());

        UserProfileResponse userProfile = new UserProfileResponse(
            user.getId(),
            user.getEmail(),
            user.getFirstName(),
            user.getLastName(),
            user.getPhoneNumber(),
            user.getRole(),
            user.getIsActive(),
            user.getIsEmailVerified(),
            user.getCreatedAt(),
            user.getLastLoginAt()
        );

        return new LoginResponse(
            newAccessToken,
            refreshTokenString,
            jwtTokenProvider.getAccessTokenExpiration(),
            userProfile
        );
    }

    public void logout(String refreshToken) {
        refreshTokenRepository.deleteByToken(refreshToken);
    }

    private void saveRefreshToken(Long userId, String token) {
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.setUserId(userId);
        refreshToken.setToken(token);
        refreshToken.setExpiresAt(
            LocalDateTime.now().plusSeconds(jwtTokenProvider.getRefreshTokenExpiration() / 1000)
        );
        refreshTokenRepository.save(refreshToken);
    }
}
