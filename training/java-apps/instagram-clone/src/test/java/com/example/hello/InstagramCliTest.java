package com.example.hello;

import com.example.instagram.model.User;
import com.example.instagram.repository.InMemoryUserRepository;
import com.example.instagram.repository.UserRepository;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class InstagramCliTest {
    private UserService userService;
    private AuthenticationService authService;
    
    @BeforeEach
    void setUp() {
        UserRepository userRepository = new InMemoryUserRepository();
        userService = new UserService(userRepository);
        authService = new AuthenticationService(userRepository);
    }
    
    @Test
    void canCreateInstagramCliInstance() {
        InstagramCli cli = new InstagramCli();
        assertNotNull(cli);
    }
    
    @Test
    void registrationAndLoginFlow() {
        User user = userService.register("testuser", "test@example.com", "password123");
        assertNotNull(user);
        assertEquals("testuser", user.username());
        assertEquals("test@example.com", user.email());
        
        Optional<String> sessionId = authService.login("testuser", "password123");
        assertTrue(sessionId.isPresent());
        
        Optional<User> currentUser = authService.getCurrentUser(sessionId.get());
        assertTrue(currentUser.isPresent());
        assertEquals("testuser", currentUser.get().username());
        
        authService.logout(sessionId.get());
        assertFalse(authService.isAuthenticated(sessionId.get()));
    }
    
    @Test
    void loginWithEmail() {
        userService.register("testuser", "test@example.com", "password123");
        
        Optional<String> sessionId = authService.login("test@example.com", "password123");
        assertTrue(sessionId.isPresent());
        
        Optional<User> currentUser = authService.getCurrentUser(sessionId.get());
        assertTrue(currentUser.isPresent());
        assertEquals("testuser", currentUser.get().username());
    }
    
    @Test
    void loginFailsWithInvalidCredentials() {
        userService.register("testuser", "test@example.com", "password123");
        
        Optional<String> sessionId = authService.login("testuser", "wrongpassword");
        assertTrue(sessionId.isEmpty());
    }
}