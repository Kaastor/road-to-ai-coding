package com.example.instagram;

import com.example.instagram.model.User;

public class InstagramApp {
    public static void main(String[] args) {
        System.out.println("Instagram Clone Application");
        System.out.println("===========================");
        
        // Demo user creation
        try {
            User user = new User("1", "johndoe", "john@example.com", "password123");
            System.out.println("Successfully created user: " + user.username());
            System.out.println("User ID: " + user.id());
            System.out.println("Email: " + user.email());
        } catch (Exception e) {
            System.err.println("Error creating user: " + e.getMessage());
        }
    }
}