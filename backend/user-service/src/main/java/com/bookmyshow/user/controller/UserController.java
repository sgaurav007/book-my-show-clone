package com.bookmyshow.user.controller;

import com.bookmyshow.common.dto.ApiResponse;
import com.bookmyshow.user.dto.*;
import com.bookmyshow.user.service.AuthService;
import com.bookmyshow.user.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<UserProfileResponse>> register(
            @Valid @RequestBody RegisterRequest request) {
        UserProfileResponse user = userService.registerUser(request);
        return ResponseEntity.ok(ApiResponse.success("User registered successfully", user));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponse>> login(
            @Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success("Login successful", response));
    }

    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<UserProfileResponse>> getProfile(Authentication authentication) {
        Long userId = Long.parseLong(authentication.getName());
        UserProfileResponse user = userService.getUserProfile(userId);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    @PutMapping("/profile")
    public ResponseEntity<ApiResponse<UserProfileResponse>> updateProfile(
            Authentication authentication,
            @Valid @RequestBody UpdateProfileRequest request) {
        Long userId = Long.parseLong(authentication.getName());
        UserProfileResponse user = userService.updateUserProfile(userId, request);
        return ResponseEntity.ok(ApiResponse.success("Profile updated successfully", user));
    }

    @PostMapping("/refresh-token")
    public ResponseEntity<ApiResponse<LoginResponse>> refreshToken(
            @Valid @RequestBody RefreshTokenRequest request) {
        LoginResponse response = authService.refreshAccessToken(request.getRefreshToken());
        return ResponseEntity.ok(ApiResponse.success("Token refreshed successfully", response));
    }

    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout(@Valid @RequestBody RefreshTokenRequest request) {
        authService.logout(request.getRefreshToken());
        return ResponseEntity.ok(ApiResponse.success("Logout successful", null));
    }
}
