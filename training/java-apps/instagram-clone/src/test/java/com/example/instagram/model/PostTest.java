package com.example.instagram.model;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import java.time.Instant;
import static org.junit.jupiter.api.Assertions.*;

class PostTest {

    private final Instant testTimestamp = Instant.now();

    @Test
    @DisplayName("Should create post with valid data")
    void createPostWithValidData() {
        Post post = new Post("post1", "user1", "Hello world!", testTimestamp);
        
        assertEquals("post1", post.id());
        assertEquals("user1", post.userId());
        assertEquals("Hello world!", post.content());
        assertEquals(testTimestamp, post.timestamp());
    }

    @Test
    @DisplayName("Should throw exception when id is null")
    void shouldThrowExceptionWhenIdIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new Post(null, "user1", "Hello world!", testTimestamp));
    }

    @Test
    @DisplayName("Should throw exception when userId is null")
    void shouldThrowExceptionWhenUserIdIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new Post("post1", null, "Hello world!", testTimestamp));
    }

    @Test
    @DisplayName("Should throw exception when content is null")
    void shouldThrowExceptionWhenContentIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new Post("post1", "user1", null, testTimestamp));
    }

    @Test
    @DisplayName("Should throw exception when timestamp is null")
    void shouldThrowExceptionWhenTimestampIsNull() {
        assertThrows(NullPointerException.class, () -> 
            new Post("post1", "user1", "Hello world!", null));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when id is blank")
    void shouldThrowExceptionWhenIdIsBlank(String blankId) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new Post(blankId, "user1", "Hello world!", testTimestamp));
        assertEquals("Post ID cannot be blank", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when userId is blank")
    void shouldThrowExceptionWhenUserIdIsBlank(String blankUserId) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new Post("post1", blankUserId, "Hello world!", testTimestamp));
        assertEquals("User ID cannot be blank", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", " ", "  "})
    @DisplayName("Should throw exception when content is blank")
    void shouldThrowExceptionWhenContentIsBlank(String blankContent) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new Post("post1", "user1", blankContent, testTimestamp));
        assertEquals("Content cannot be blank", exception.getMessage());
    }

    @Test
    @DisplayName("Should throw exception when content exceeds maximum length")
    void shouldThrowExceptionWhenContentExceedsMaxLength() {
        String longContent = "a".repeat(2201);
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> 
            new Post("post1", "user1", longContent, testTimestamp));
        assertEquals("Content cannot exceed 2200 characters", exception.getMessage());
    }

    @Test
    @DisplayName("Should accept content at maximum length")
    void shouldAcceptContentAtMaxLength() {
        String maxContent = "a".repeat(2200);
        assertDoesNotThrow(() -> 
            new Post("post1", "user1", maxContent, testTimestamp));
    }

    @Test
    @DisplayName("Should have proper equality behavior")
    void shouldHaveProperEqualityBehavior() {
        Post post1 = new Post("post1", "user1", "Hello world!", testTimestamp);
        Post post2 = new Post("post1", "user1", "Hello world!", testTimestamp);
        Post post3 = new Post("post2", "user1", "Hello world!", testTimestamp);

        assertEquals(post1, post2);
        assertNotEquals(post1, post3);
        assertEquals(post1.hashCode(), post2.hashCode());
    }

    @Test
    @DisplayName("Should have proper toString representation")
    void shouldHaveProperToStringRepresentation() {
        Post post = new Post("post1", "user1", "Hello world!", testTimestamp);
        String toString = post.toString();
        
        assertTrue(toString.contains("post1"));
        assertTrue(toString.contains("user1"));
        assertTrue(toString.contains("Hello world!"));
        assertTrue(toString.contains(testTimestamp.toString()));
    }

    @Test
    @DisplayName("Should handle different timestamp values")
    void shouldHandleDifferentTimestampValues() {
        Instant past = Instant.parse("2023-01-01T00:00:00Z");
        Instant future = Instant.parse("2025-01-01T00:00:00Z");
        
        Post pastPost = new Post("post1", "user1", "Past post", past);
        Post futurePost = new Post("post2", "user1", "Future post", future);
        
        assertEquals(past, pastPost.timestamp());
        assertEquals(future, futurePost.timestamp());
    }
}