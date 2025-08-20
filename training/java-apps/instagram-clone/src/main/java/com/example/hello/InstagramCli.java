package com.example.hello;

import com.example.instagram.model.User;
import com.example.instagram.repository.InMemoryUserRepository;
import com.example.instagram.repository.UserRepository;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.UserService;

import java.util.Optional;
import java.util.Scanner;

public class InstagramCli {
    private final UserService userService;
    private final AuthenticationService authService;
    private final Scanner scanner;
    private String currentSessionId;
    
    public InstagramCli() {
        UserRepository userRepository = new InMemoryUserRepository();
        this.userService = new UserService(userRepository);
        this.authService = new AuthenticationService(userRepository);
        this.scanner = new Scanner(System.in);
        this.currentSessionId = null;
    }
    
    public static void main(String[] args) {
        InstagramCli cli = new InstagramCli();
        cli.run();
    }
    
    public void run() {
        System.out.println("Welcome to Instagram Clone!");
        System.out.println("===========================\n");
        
        while (true) {
            if (currentSessionId == null) {
                showLoginMenu();
            } else {
                showMainMenu();
            }
        }
    }
    
    private void showLoginMenu() {
        System.out.println("\n--- Login Menu ---");
        System.out.println("1. Register");
        System.out.println("2. Login");
        System.out.println("3. Exit");
        System.out.print("Choose an option: ");
        
        String choice = scanner.nextLine().trim();
        
        switch (choice) {
            case "1" -> handleRegister();
            case "2" -> handleLogin();
            case "3" -> {
                System.out.println("Goodbye!");
                System.exit(0);
            }
            default -> System.out.println("Invalid option. Please try again.");
        }
    }
    
    private void showMainMenu() {
        Optional<User> currentUser = authService.getCurrentUser(currentSessionId);
        if (currentUser.isPresent()) {
            System.out.println("\n--- Main Menu (Welcome, " + currentUser.get().username() + ") ---");
        }
        
        System.out.println("1. View Profile");
        System.out.println("2. Logout");
        System.out.print("Choose an option: ");
        
        String choice = scanner.nextLine().trim();
        
        switch (choice) {
            case "1" -> handleViewProfile();
            case "2" -> handleLogout();
            default -> System.out.println("Invalid option. Please try again.");
        }
    }
    
    private void handleRegister() {
        System.out.println("\n--- User Registration ---");
        System.out.print("Enter username: ");
        String username = scanner.nextLine().trim();
        
        System.out.print("Enter email: ");
        String email = scanner.nextLine().trim();
        
        System.out.print("Enter password: ");
        String password = scanner.nextLine().trim();
        
        try {
            User user = userService.register(username, email, password);
            System.out.println("Registration successful! Welcome, " + user.username() + "!");
        } catch (IllegalArgumentException e) {
            System.out.println("Registration failed: " + e.getMessage());
        }
    }
    
    private void handleLogin() {
        System.out.println("\n--- User Login ---");
        System.out.print("Enter username or email: ");
        String usernameOrEmail = scanner.nextLine().trim();
        
        System.out.print("Enter password: ");
        String password = scanner.nextLine().trim();
        
        Optional<String> sessionId = authService.login(usernameOrEmail, password);
        
        if (sessionId.isPresent()) {
            currentSessionId = sessionId.get();
            Optional<User> user = authService.getCurrentUser(currentSessionId);
            if (user.isPresent()) {
                System.out.println("Login successful! Welcome back, " + user.get().username() + "!");
            }
        } else {
            System.out.println("Login failed: Invalid credentials.");
        }
    }
    
    private void handleViewProfile() {
        Optional<User> currentUser = authService.getCurrentUser(currentSessionId);
        if (currentUser.isPresent()) {
            User user = currentUser.get();
            System.out.println("\n--- Your Profile ---");
            System.out.println("User ID: " + user.id());
            System.out.println("Username: " + user.username());
            System.out.println("Email: " + user.email());
        } else {
            System.out.println("Error: Could not retrieve user profile.");
            handleLogout();
        }
    }
    
    private void handleLogout() {
        if (currentSessionId != null) {
            authService.logout(currentSessionId);
            currentSessionId = null;
            System.out.println("Logged out successfully!");
        }
    }
}
