package com.example.instagram.service;

import com.example.instagram.model.User;
import com.example.instagram.repository.InMemoryUserRepository;
import com.example.instagram.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class AuthenticationServiceTest {
    
    private AuthenticationService authService;
    private UserRepository userRepository;
    private User testUser;
    
    @BeforeEach
    void setUp() {
        userRepository = new InMemoryUserRepository();
        authService = new AuthenticationService(userRepository);
        testUser = new User("1", "testuser", "test@example.com", "password123");
        userRepository.save(testUser);
    }
    
    @Test
    void shouldReturnSessionIdWhenLoginWithValidUsername() {
        Optional<String> sessionId = authService.login("testuser", "password123");
        
        assertTrue(sessionId.isPresent());
        assertNotNull(sessionId.get());
        assertFalse(sessionId.get().isBlank());
    }
    
    @Test
    void shouldReturnSessionIdWhenLoginWithValidEmail() {
        Optional<String> sessionId = authService.login("test@example.com", "password123");
        
        assertTrue(sessionId.isPresent());
        assertNotNull(sessionId.get());
        assertFalse(sessionId.get().isBlank());
    }
    
    @Test
    void shouldReturnEmptyWhenLoginWithInvalidUsername() {
        Optional<String> sessionId = authService.login("wronguser", "password123");
        
        assertTrue(sessionId.isEmpty());
    }
    
    @Test
    void shouldReturnEmptyWhenLoginWithInvalidPassword() {
        Optional<String> sessionId = authService.login("testuser", "wrongpassword");
        
        assertTrue(sessionId.isEmpty());
    }
    
    @ParameterizedTest
    @CsvSource({
        "'', password123",
        "testuser, ''",
        "'   ', password123",
        "testuser, '   '"
    })
    void shouldReturnEmptyWhenLoginWithBlankCredentials(String username, String password) {
        Optional<String> sessionId = authService.login(username, password);
        
        assertTrue(sessionId.isEmpty());
    }
    
    @Test
    void shouldThrowExceptionWhenLoginWithNullCredentials() {
        assertThrows(NullPointerException.class, () -> authService.login(null, "password123"));
        assertThrows(NullPointerException.class, () -> authService.login("testuser", null));
    }
    
    @Test
    void shouldAuthenticateUserAfterSuccessfulLogin() {
        Optional<String> sessionId = authService.login("testuser", "password123");
        
        assertTrue(sessionId.isPresent());
        assertTrue(authService.isAuthenticated(sessionId.get()));
    }
    
    @Test
    void shouldReturnCurrentUserWhenAuthenticated() {
        Optional<String> sessionId = authService.login("testuser", "password123");
        
        assertTrue(sessionId.isPresent());
        Optional<User> currentUser = authService.getCurrentUser(sessionId.get());
        
        assertTrue(currentUser.isPresent());
        assertEquals(testUser, currentUser.get());
    }
    
    @Test
    void shouldLogoutSuccessfully() {
        Optional<String> sessionId = authService.login("testuser", "password123");
        assertTrue(sessionId.isPresent());
        assertTrue(authService.isAuthenticated(sessionId.get()));
        
        authService.logout(sessionId.get());
        
        assertFalse(authService.isAuthenticated(sessionId.get()));
        assertTrue(authService.getCurrentUser(sessionId.get()).isEmpty());
    }
    
    @Test
    void shouldHandleNullSessionIdInLogout() {
        assertDoesNotThrow(() -> authService.logout(null));
    }
    
    @Test
    void shouldReturnFalseForInvalidSessionId() {
        assertFalse(authService.isAuthenticated("invalid-session-id"));
        assertFalse(authService.isAuthenticated(null));
    }
    
    @Test
    void shouldReturnEmptyForInvalidSessionId() {
        assertTrue(authService.getCurrentUser("invalid-session-id").isEmpty());
        assertTrue(authService.getCurrentUser(null).isEmpty());
    }
    
    @Test
    void shouldLogoutAllSessionsForUser() {
        Optional<String> session1 = authService.login("testuser", "password123");
        Optional<String> session2 = authService.login("test@example.com", "password123");
        
        assertTrue(session1.isPresent());
        assertTrue(session2.isPresent());
        assertTrue(authService.isAuthenticated(session1.get()));
        assertTrue(authService.isAuthenticated(session2.get()));
        
        authService.logoutAllSessions(testUser.id());
        
        assertFalse(authService.isAuthenticated(session1.get()));
        assertFalse(authService.isAuthenticated(session2.get()));
    }
    
    @Test
    void shouldThrowExceptionWhenLogoutAllSessionsWithNullUserId() {
        assertThrows(NullPointerException.class, () -> authService.logoutAllSessions(null));
    }
    
    @Test
    void shouldGenerateUniqueSessionIds() {
        Optional<String> session1 = authService.login("testuser", "password123");
        authService.logout(session1.get());
        Optional<String> session2 = authService.login("testuser", "password123");
        
        assertTrue(session1.isPresent());
        assertTrue(session2.isPresent());
        assertNotEquals(session1.get(), session2.get());
    }
    
    @Test
    void shouldAllowMultipleSessionsForSameUser() {
        Optional<String> session1 = authService.login("testuser", "password123");
        Optional<String> session2 = authService.login("test@example.com", "password123");
        
        assertTrue(session1.isPresent());
        assertTrue(session2.isPresent());
        assertTrue(authService.isAuthenticated(session1.get()));
        assertTrue(authService.isAuthenticated(session2.get()));
        assertNotEquals(session1.get(), session2.get());
    }
}