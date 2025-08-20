package com.example.instagram.model;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

class UserTest {

    @Test
    @DisplayName("Should create user with valid data")
    void createUserWithValidData() {
        User user = new User("1", "johndoe", "john@example.com", "password123");
        
        assertEquals("1", user.id());
        assertEquals("johndoe", user.username());
        assertEquals("john@example.com", user.email());
        assertEquals("password123", user.password());
    }

    @Test
    @DisplayName("Should throw exception when id is null")
    void shouldThrowExceptionWhenIdIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new User(null, "johndoe", "john@example.com", "password123"));
    }

    @Test
    @DisplayName("Should throw exception when username is null")
    void shouldThrowExceptionWhenUsernameIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new User("1", null, "john@example.com", "password123"));
    }

    @Test
    @DisplayName("Should throw exception when email is null")
    void shouldThrowExceptionWhenEmailIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new User("1", "johndoe", null, "password123"));
    }

    @Test
    @DisplayName("Should throw exception when password is null")
    void shouldThrowExceptionWhenPasswordIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new User("1", "johndoe", "john@example.com", null));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when id is blank")
    void shouldThrowExceptionWhenIdIsBlank(String blankId) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new User(blankId, "johndoe", "john@example.com", "password123"));
        assertEquals("User ID cannot be blank", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when username is blank")
    void shouldThrowExceptionWhenUsernameIsBlank(String blankUsername) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new User("1", blankUsername, "john@example.com", "password123"));
        assertEquals("Username cannot be blank", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when email is blank")
    void shouldThrowExceptionWhenEmailIsBlank(String blankEmail) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new User("1", "johndoe", blankEmail, "password123"));
        assertEquals("Email cannot be blank", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "1", "12", "123", "1234", "12345"})
    @DisplayName("Should throw exception when password is too short")
    void shouldThrowExceptionWhenPasswordIsTooShort(String shortPassword) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new User("1", "johndoe", "john@example.com", shortPassword));
        assertEquals("Password must be at least 6 characters long", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"invalid", "test@", "@example.com", "test@.com", "test.com", "test@com"})
    @DisplayName("Should throw exception when email format is invalid")
    void shouldThrowExceptionWhenEmailFormatIsInvalid(String invalidEmail) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new User("1", "johndoe", invalidEmail, "password123"));
        assertEquals("Email format is invalid", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"test@example.com", "user@domain.org", "name@test.co.uk", "a@b.c"})
    @DisplayName("Should accept valid email formats")
    void shouldAcceptValidEmailFormats(String validEmail) {
        assertDoesNotThrow(() -> 
            new User("1", "johndoe", validEmail, "password123"));
    }

    @Test
    @DisplayName("Should have proper equality behavior")
    void shouldHaveProperEqualityBehavior() {
        User user1 = new User("1", "johndoe", "john@example.com", "password123");
        User user2 = new User("1", "johndoe", "john@example.com", "password123");
        User user3 = new User("2", "johndoe", "john@example.com", "password123");

        assertEquals(user1, user2);
        assertNotEquals(user1, user3);
        assertEquals(user1.hashCode(), user2.hashCode());
    }

    @Test
    @DisplayName("Should have proper toString representation")
    void shouldHaveProperToStringRepresentation() {
        User user = new User("1", "johndoe", "john@example.com", "password123");
        String toString = user.toString();
        
        assertTrue(toString.contains("1"));
        assertTrue(toString.contains("johndoe"));
        assertTrue(toString.contains("john@example.com"));
        assertTrue(toString.contains("password123"));
    }

}