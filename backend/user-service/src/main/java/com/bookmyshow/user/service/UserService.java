package com.bookmyshow.user.service;

import com.bookmyshow.common.exception.ResourceAlreadyExistsException;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import com.bookmyshow.user.dto.RegisterRequest;
import com.bookmyshow.user.dto.UpdateProfileRequest;
import com.bookmyshow.user.dto.UserProfileResponse;
import com.bookmyshow.user.entity.User;
import com.bookmyshow.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Transactional
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserProfileResponse registerUser(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new ResourceAlreadyExistsException(
                "User with email " + request.getEmail() + " already exists"
            );
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setRole("CUSTOMER");
        user.setIsActive(true);
        user.setIsEmailVerified(false);

        User savedUser = userRepository.save(user);
        return mapToUserProfileResponse(savedUser);
    }

    public UserProfileResponse getUserProfile(Long userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
        return mapToUserProfileResponse(user);
    }

    public User getUserByEmail(String email) {
        return userRepository.findByEmail(email)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + email));
    }

    public User getUserById(Long userId) {
        return userRepository.findById(userId)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
    }

    public UserProfileResponse updateUserProfile(Long userId, UpdateProfileRequest request) {
        User user = getUserById(userId);

        if (request.getFirstName() != null) {
            user.setFirstName(request.getFirstName());
        }
        if (request.getLastName() != null) {
            user.setLastName(request.getLastName());
        }
        if (request.getPhoneNumber() != null) {
            user.setPhoneNumber(request.getPhoneNumber());
        }

        User updatedUser = userRepository.save(user);
        return mapToUserProfileResponse(updatedUser);
    }

    public void updateLastLogin(Long userId) {
        User user = getUserById(userId);
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);
    }

    private UserProfileResponse mapToUserProfileResponse(User user) {
        return new UserProfileResponse(
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
    }
}
