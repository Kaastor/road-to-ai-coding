package com.example.instagram.service;

import com.example.instagram.model.User;
import com.example.instagram.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        userService = new UserService(userRepository);
    }
    
    @Test
    void register_ValidInput_ReturnsUser() {
        when(userRepository.existsByUsername("testuser")).thenReturn(false);
        when(userRepository.existsByEmail("test@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> invocation.getArgument(0));
        
        User result = userService.register("testuser", "test@example.com", "password123");
        
        assertNotNull(result);
        assertEquals("testuser", result.username());
        assertEquals("test@example.com", result.email());
        assertEquals("password123", result.password());
        assertNotNull(result.id());
        
        verify(userRepository).existsByUsername("testuser");
        verify(userRepository).existsByEmail("test@example.com");
        verify(userRepository).save(any(User.class));
    }
    
    @Test
    void register_DuplicateUsername_ThrowsException() {
        when(userRepository.existsByUsername("existinguser")).thenReturn(true);
        
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register("existinguser", "test@example.com", "password123")
        );
        
        assertEquals("Username 'existinguser' is already taken", exception.getMessage());
        verify(userRepository).existsByUsername("existinguser");
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_DuplicateEmail_ThrowsException() {
        when(userRepository.existsByUsername("testuser")).thenReturn(false);
        when(userRepository.existsByEmail("existing@example.com")).thenReturn(true);
        
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register("testuser", "existing@example.com", "password123")
        );
        
        assertEquals("Email 'existing@example.com' is already registered", exception.getMessage());
        verify(userRepository).existsByUsername("testuser");
        verify(userRepository).existsByEmail("existing@example.com");
        verify(userRepository, never()).save(any(User.class));
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", "  ", "ab", "thisusernameiswaytoolongtobevalid"})
    void register_InvalidUsername_ThrowsException(String invalidUsername) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register(invalidUsername, "test@example.com", "password123")
        );
        
        assertTrue(exception.getMessage().contains("Username"));
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_UsernameWithInvalidCharacters_ThrowsException() {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register("user@name", "test@example.com", "password123")
        );
        
        assertEquals("Username can only contain letters, numbers, and underscores", exception.getMessage());
        verify(userRepository, never()).save(any(User.class));
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", "12345"})
    void register_InvalidPassword_ThrowsException(String invalidPassword) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register("testuser", "test@example.com", invalidPassword)
        );
        
        assertTrue(exception.getMessage().contains("Password"));
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_TooLongPassword_ThrowsException() {
        String longPassword = "a".repeat(101);
        
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> userService.register("testuser", "test@example.com", longPassword)
        );
        
        assertEquals("Password cannot exceed 100 characters", exception.getMessage());
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_NullUsername_ThrowsException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> userService.register(null, "test@example.com", "password123")
        );
        
        assertEquals("Username cannot be null", exception.getMessage());
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_NullEmail_ThrowsException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> userService.register("testuser", null, "password123")
        );
        
        assertEquals("Email cannot be null", exception.getMessage());
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void register_NullPassword_ThrowsException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> userService.register("testuser", "test@example.com", null)
        );
        
        assertEquals("Password cannot be null", exception.getMessage());
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    void constructor_NullRepository_ThrowsException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> new UserService(null)
        );
        
        assertEquals("UserRepository cannot be null", exception.getMessage());
    }
}