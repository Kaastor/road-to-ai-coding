package com.example.instagram.model;

import java.util.Objects;

public record User(
    String id,
    String username,
    String email,
    String password
) {
    public User {
        Objects.requireNonNull(id, "User ID cannot be null");
        Objects.requireNonNull(username, "Username cannot be null");
        Objects.requireNonNull(email, "Email cannot be null");
        Objects.requireNonNull(password, "Password cannot be null");
        
        if (id.isBlank()) {
            throw new IllegalArgumentException("User ID cannot be blank");
        }
        if (username.isBlank()) {
            throw new IllegalArgumentException("Username cannot be blank");
        }
        if (email.isBlank()) {
            throw new IllegalArgumentException("Email cannot be blank");
        }
        if (password.length() < 6) {
            throw new IllegalArgumentException("Password must be at least 6 characters long");
        }
        if (!isValidEmail(email)) {
            throw new IllegalArgumentException("Email format is invalid");
        }
    }
    
    private static boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".") && 
               email.indexOf("@") > 0 && 
               email.lastIndexOf(".") > email.indexOf("@") + 1 &&
               email.lastIndexOf(".") < email.length() - 1;
    }
}