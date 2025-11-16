package com.bookmyshow.user.service;

import com.bookmyshow.common.exception.ResourceAlreadyExistsException;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import com.bookmyshow.user.dto.RegisterRequest;
import com.bookmyshow.user.dto.UpdateProfileRequest;
import com.bookmyshow.user.dto.UserProfileResponse;
import com.bookmyshow.user.entity.User;
import com.bookmyshow.user.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    private RegisterRequest registerRequest;
    private User user;

    @BeforeEach
    void setUp() {
        registerRequest = new RegisterRequest(
            "test@example.com",
            "Password@123",
            "John",
            "Doe",
            "+1234567890"
        );

        user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        user.setPasswordHash("hashedPassword");
        user.setFirstName("John");
        user.setLastName("Doe");
        user.setPhoneNumber("+1234567890");
        user.setRole("CUSTOMER");
        user.setIsActive(true);
        user.setIsEmailVerified(false);
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());
    }

    @Test
    void registerUser_Success() {
        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(passwordEncoder.encode(anyString())).thenReturn("hashedPassword");
        when(userRepository.save(any(User.class))).thenReturn(user);

        UserProfileResponse response = userService.registerUser(registerRequest);

        assertNotNull(response);
        assertEquals("test@example.com", response.getEmail());
        assertEquals("John", response.getFirstName());
        assertEquals("Doe", response.getLastName());
        assertEquals("CUSTOMER", response.getRole());

        verify(userRepository).existsByEmail("test@example.com");
        verify(passwordEncoder).encode("Password@123");
        verify(userRepository).save(any(User.class));
    }

    @Test
    void registerUser_EmailAlreadyExists() {
        when(userRepository.existsByEmail(anyString())).thenReturn(true);

        assertThrows(ResourceAlreadyExistsException.class,
            () -> userService.registerUser(registerRequest));

        verify(userRepository).existsByEmail("test@example.com");
        verify(userRepository, never()).save(any(User.class));
    }

    @Test
    void getUserProfile_Success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        UserProfileResponse response = userService.getUserProfile(1L);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("test@example.com", response.getEmail());

        verify(userRepository).findById(1L);
    }

    @Test
    void getUserProfile_UserNotFound() {
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
            () -> userService.getUserProfile(1L));

        verify(userRepository).findById(1L);
    }

    @Test
    void getUserByEmail_Success() {
        when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.of(user));

        User foundUser = userService.getUserByEmail("test@example.com");

        assertNotNull(foundUser);
        assertEquals("test@example.com", foundUser.getEmail());

        verify(userRepository).findByEmail("test@example.com");
    }

    @Test
    void getUserByEmail_UserNotFound() {
        when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
            () -> userService.getUserByEmail("test@example.com"));

        verify(userRepository).findByEmail("test@example.com");
    }

    @Test
    void updateUserProfile_Success() {
        UpdateProfileRequest updateRequest = new UpdateProfileRequest(
            "Jane",
            "Smith",
            "+9876543210"
        );

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(userRepository.save(any(User.class))).thenReturn(user);

        UserProfileResponse response = userService.updateUserProfile(1L, updateRequest);

        assertNotNull(response);
        verify(userRepository).findById(1L);
        verify(userRepository).save(any(User.class));
    }

    @Test
    void updateLastLogin_Success() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(userRepository.save(any(User.class))).thenReturn(user);

        userService.updateLastLogin(1L);

        verify(userRepository).findById(1L);
        verify(userRepository).save(any(User.class));
        assertNotNull(user.getLastLoginAt());
    }
}
