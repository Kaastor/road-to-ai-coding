package com.example.hello;

import com.example.instagram.model.Post;
import com.example.instagram.model.User;
import com.example.instagram.repository.InMemoryPostRepository;
import com.example.instagram.repository.InMemoryUserRepository;
import com.example.instagram.repository.PostRepository;
import com.example.instagram.repository.UserRepository;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.PostService;
import com.example.instagram.service.UserService;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;
import java.util.Scanner;

public class InstagramCli {
    private final UserService userService;
    private final AuthenticationService authService;
    private final PostService postService;
    private final Scanner scanner;
    private String currentSessionId;
    
    public InstagramCli() {
        UserRepository userRepository = new InMemoryUserRepository();
        PostRepository postRepository = new InMemoryPostRepository();
        this.userService = new UserService(userRepository);
        this.authService = new AuthenticationService(userRepository);
        this.postService = new PostService(postRepository, userRepository);
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
        System.out.println("2. Create Post");
        System.out.println("3. View My Posts");
        System.out.println("4. Logout");
        System.out.print("Choose an option: ");
        
        String choice = scanner.nextLine().trim();
        
        switch (choice) {
            case "1" -> handleViewProfile();
            case "2" -> handleCreatePost();
            case "3" -> handleViewMyPosts();
            case "4" -> handleLogout();
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
    
    private void handleCreatePost() {
        Optional<User> currentUser = authService.getCurrentUser(currentSessionId);
        if (currentUser.isEmpty()) {
            System.out.println("Error: Could not retrieve user information.");
            handleLogout();
            return;
        }
        
        System.out.println("\n--- Create New Post ---");
        System.out.println("Enter your post content (max 2200 characters):");
        String content = scanner.nextLine().trim();
        
        if (content.isEmpty()) {
            System.out.println("Post content cannot be empty.");
            return;
        }
        
        try {
            Post post = postService.createPost(currentUser.get().id(), content);
            System.out.println("Post created successfully!");
            System.out.println("Post ID: " + post.id());
            System.out.println("Content: " + post.content());
        } catch (IllegalArgumentException e) {
            System.out.println("Failed to create post: " + e.getMessage());
        }
    }
    
    private void handleViewMyPosts() {
        Optional<User> currentUser = authService.getCurrentUser(currentSessionId);
        if (currentUser.isEmpty()) {
            System.out.println("Error: Could not retrieve user information.");
            handleLogout();
            return;
        }
        
        System.out.println("\n--- My Posts ---");
        try {
            List<Post> posts = postService.getUserPosts(currentUser.get().id());
            
            if (posts.isEmpty()) {
                System.out.println("You haven't created any posts yet.");
                return;
            }
            
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            System.out.println("Total posts: " + posts.size());
            System.out.println();
            
            for (int i = 0; i < posts.size(); i++) {
                Post post = posts.get(i);
                System.out.println("Post #" + (i + 1));
                System.out.println("Created: " + post.timestamp().atZone(java.time.ZoneId.systemDefault()).format(formatter));
                System.out.println("Content: " + post.content());
                System.out.println("Post ID: " + post.id());
                System.out.println("-".repeat(50));
            }
        } catch (IllegalArgumentException e) {
            System.out.println("Failed to retrieve posts: " + e.getMessage());
        }
    }
}
