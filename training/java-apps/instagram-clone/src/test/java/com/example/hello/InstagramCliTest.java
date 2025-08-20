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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class InstagramCliTest {
    private UserService userService;
    private AuthenticationService authService;
    private PostService postService;
    
    @BeforeEach
    void setUp() {
        UserRepository userRepository = new InMemoryUserRepository();
        PostRepository postRepository = new InMemoryPostRepository();
        userService = new UserService(userRepository);
        authService = new AuthenticationService(userRepository);
        postService = new PostService(postRepository, userRepository);
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
    
    @Test
    void userCanCreateAndViewPosts() {
        User user = userService.register("testuser", "test@example.com", "password123");
        
        Post post1 = postService.createPost(user.id(), "My first post");
        assertNotNull(post1);
        assertEquals(user.id(), post1.userId());
        assertEquals("My first post", post1.content());
        assertNotNull(post1.timestamp());
        
        Post post2 = postService.createPost(user.id(), "My second post");
        assertNotNull(post2);
        
        List<Post> userPosts = postService.getUserPosts(user.id());
        assertEquals(2, userPosts.size());
        
        boolean foundFirstPost = userPosts.stream()
            .anyMatch(p -> p.content().equals("My first post"));
        boolean foundSecondPost = userPosts.stream()
            .anyMatch(p -> p.content().equals("My second post"));
        
        assertTrue(foundFirstPost);
        assertTrue(foundSecondPost);
    }
    
    @Test
    void authenticatedUserCanCreatePosts() {
        User user = userService.register("testuser", "test@example.com", "password123");
        Optional<String> sessionId = authService.login("testuser", "password123");
        assertTrue(sessionId.isPresent());
        
        Optional<User> currentUser = authService.getCurrentUser(sessionId.get());
        assertTrue(currentUser.isPresent());
        
        Post post = postService.createPost(currentUser.get().id(), "Authenticated user post");
        assertNotNull(post);
        assertEquals(currentUser.get().id(), post.userId());
        assertEquals("Authenticated user post", post.content());
        
        List<Post> userPosts = postService.getUserPosts(currentUser.get().id());
        assertEquals(1, userPosts.size());
        assertEquals("Authenticated user post", userPosts.get(0).content());
    }
    
    @Test
    void emptyPostListForNewUser() {
        User user = userService.register("testuser", "test@example.com", "password123");
        
        List<Post> userPosts = postService.getUserPosts(user.id());
        assertTrue(userPosts.isEmpty());
    }
}