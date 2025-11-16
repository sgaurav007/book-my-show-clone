package com.bookmyshow.user.controller;

import com.bookmyshow.user.dto.*;
import com.bookmyshow.user.service.AuthService;
import com.bookmyshow.user.service.UserService;
import com.bookmyshow.user.security.JwtTokenProvider;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private UserService userService;

    @MockBean
    private AuthService authService;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    private RegisterRequest registerRequest;
    private LoginRequest loginRequest;
    private UserProfileResponse userProfileResponse;
    private LoginResponse loginResponse;

    @BeforeEach
    void setUp() {
        registerRequest = new RegisterRequest(
            "test@example.com",
            "Password@123",
            "John",
            "Doe",
            "+1234567890"
        );

        loginRequest = new LoginRequest("test@example.com", "Password@123");

        userProfileResponse = new UserProfileResponse(
            1L,
            "test@example.com",
            "John",
            "Doe",
            "+1234567890",
            "CUSTOMER",
            true,
            false,
            LocalDateTime.now(),
            null
        );

        loginResponse = new LoginResponse(
            "accessToken",
            "refreshToken",
            3600000L,
            userProfileResponse
        );
    }

    @Test
    void register_Success() throws Exception {
        when(userService.registerUser(any(RegisterRequest.class)))
            .thenReturn(userProfileResponse);

        mockMvc.perform(post("/api/users/register")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(registerRequest)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.email").value("test@example.com"))
            .andExpect(jsonPath("$.data.firstName").value("John"));
    }

    @Test
    void register_InvalidEmail() throws Exception {
        registerRequest.setEmail("invalid-email");

        mockMvc.perform(post("/api/users/register")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(registerRequest)))
            .andExpect(status().isBadRequest());
    }

    @Test
    void login_Success() throws Exception {
        when(authService.login(any(LoginRequest.class))).thenReturn(loginResponse);

        mockMvc.perform(post("/api/users/login")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginRequest)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.accessToken").value("accessToken"))
            .andExpect(jsonPath("$.data.refreshToken").value("refreshToken"));
    }

    @Test
    @WithMockUser(username = "1")
    void getProfile_Success() throws Exception {
        when(userService.getUserProfile(anyLong())).thenReturn(userProfileResponse);

        mockMvc.perform(get("/api/users/profile")
                .with(csrf()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.email").value("test@example.com"));
    }

    @Test
    @WithMockUser(username = "1")
    void updateProfile_Success() throws Exception {
        UpdateProfileRequest updateRequest = new UpdateProfileRequest(
            "Jane",
            "Smith",
            "+9876543210"
        );

        when(userService.updateUserProfile(anyLong(), any(UpdateProfileRequest.class)))
            .thenReturn(userProfileResponse);

        mockMvc.perform(put("/api/users/profile")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updateRequest)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true));
    }

    @Test
    void refreshToken_Success() throws Exception {
        RefreshTokenRequest refreshTokenRequest = new RefreshTokenRequest("refreshToken");

        when(authService.refreshAccessToken(any(String.class))).thenReturn(loginResponse);

        mockMvc.perform(post("/api/users/refresh-token")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(refreshTokenRequest)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.accessToken").value("accessToken"));
    }
}
