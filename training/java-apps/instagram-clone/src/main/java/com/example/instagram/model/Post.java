package com.example.instagram.model;

import java.time.Instant;
import java.util.Objects;

public record Post(
    String id,
    String userId,
    String content,
    Instant timestamp
) {
    public Post {
        Objects.requireNonNull(id, "Post ID cannot be null");
        Objects.requireNonNull(userId, "User ID cannot be null");
        Objects.requireNonNull(content, "Content cannot be null");
        Objects.requireNonNull(timestamp, "Timestamp cannot be null");
        
        if (id.isBlank()) {
            throw new IllegalArgumentException("Post ID cannot be blank");
        }
        if (userId.isBlank()) {
            throw new IllegalArgumentException("User ID cannot be blank");
        }
        if (content.isBlank()) {
            throw new IllegalArgumentException("Content cannot be blank");
        }
        if (content.length() > 2200) {
            throw new IllegalArgumentException("Content cannot exceed 2200 characters");
        }
    }
}