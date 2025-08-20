package com.example.instagram.service;

import com.example.instagram.model.User;
import com.example.instagram.repository.UserRepository;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.UUID;

public class AuthenticationService {
    private final UserRepository userRepository;
    private final Map<String, String> activeSessions;
    
    public AuthenticationService(UserRepository userRepository) {
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepository cannot be null");
        this.activeSessions = new ConcurrentHashMap<>();
    }
    
    public Optional<String> login(String usernameOrEmail, String password) {
        Objects.requireNonNull(usernameOrEmail, "Username/email cannot be null");
        Objects.requireNonNull(password, "Password cannot be null");
        
        if (usernameOrEmail.isBlank()) {
            return Optional.empty();
        }
        if (password.isBlank()) {
            return Optional.empty();
        }
        
        Optional<User> user = findUserByUsernameOrEmail(usernameOrEmail);
        
        if (user.isEmpty() || !user.get().password().equals(password)) {
            return Optional.empty();
        }
        
        String sessionId = UUID.randomUUID().toString();
        activeSessions.put(sessionId, user.get().id());
        
        return Optional.of(sessionId);
    }
    
    public void logout(String sessionId) {
        if (sessionId != null) {
            activeSessions.remove(sessionId);
        }
    }
    
    public Optional<User> getCurrentUser(String sessionId) {
        if (sessionId == null) {
            return Optional.empty();
        }
        
        String userId = activeSessions.get(sessionId);
        if (userId == null) {
            return Optional.empty();
        }
        
        return userRepository.findById(userId);
    }
    
    public boolean isAuthenticated(String sessionId) {
        return sessionId != null && activeSessions.containsKey(sessionId);
    }
    
    public void logoutAllSessions(String userId) {
        Objects.requireNonNull(userId, "User ID cannot be null");
        activeSessions.entrySet().removeIf(entry -> userId.equals(entry.getValue()));
    }
    
    private Optional<User> findUserByUsernameOrEmail(String usernameOrEmail) {
        if (usernameOrEmail.contains("@")) {
            return userRepository.findByEmail(usernameOrEmail);
        } else {
            return userRepository.findByUsername(usernameOrEmail);
        }
    }
}