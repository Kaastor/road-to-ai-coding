package com.example.instagram.service;

import com.example.instagram.model.Post;
import com.example.instagram.model.User;
import com.example.instagram.repository.PostRepository;
import com.example.instagram.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.Instant;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class PostServiceTest {
    
    @Mock
    private PostRepository postRepository;
    
    @Mock
    private UserRepository userRepository;
    
    private PostService postService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        postService = new PostService(postRepository, userRepository);
    }

    @Test
    void constructor_withValidRepositories_shouldCreateService() {
        assertNotNull(new PostService(postRepository, userRepository));
    }

    @Test
    void constructor_withNullPostRepository_shouldThrowException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> new PostService(null, userRepository)
        );
        assertEquals("PostRepository cannot be null", exception.getMessage());
    }

    @Test
    void constructor_withNullUserRepository_shouldThrowException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> new PostService(postRepository, null)
        );
        assertEquals("UserRepository cannot be null", exception.getMessage());
    }

    @Test
    void createPost_withValidInput_shouldCreateAndSavePost() {
        String userId = "user123";
        String content = "Hello world!";
        Post expectedPost = new Post("post123", userId, content, Instant.now());
        
        when(userRepository.existsById(userId)).thenReturn(true);
        when(postRepository.save(any(Post.class))).thenReturn(expectedPost);

        Post result = postService.createPost(userId, content);

        assertNotNull(result);
        assertEquals(userId, result.userId());
        assertEquals(content, result.content());
        assertNotNull(result.id());
        assertNotNull(result.timestamp());
        
        verify(userRepository).existsById(userId);
        verify(postRepository).save(any(Post.class));
    }

    @Test
    void createPost_withNonExistentUser_shouldThrowException() {
        String userId = "nonexistent";
        String content = "Hello world!";
        
        when(userRepository.existsById(userId)).thenReturn(false);

        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.createPost(userId, content)
        );
        
        assertEquals("User with ID 'nonexistent' does not exist", exception.getMessage());
        verify(userRepository).existsById(userId);
        verify(postRepository, never()).save(any());
    }

    @Test
    void createPost_withNullUserId_shouldThrowException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> postService.createPost(null, "content")
        );
        assertEquals("User ID cannot be null", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).save(any());
    }

    @Test
    void createPost_withNullContent_shouldThrowException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> postService.createPost("user123", null)
        );
        assertEquals("Content cannot be null", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).save(any());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "   ", "\t", "\n"})
    void createPost_withBlankUserId_shouldThrowException(String blankUserId) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.createPost(blankUserId, "content")
        );
        assertEquals("User ID cannot be blank", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).save(any());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "   ", "\t", "\n"})
    void createPost_withBlankContent_shouldThrowException(String blankContent) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.createPost("user123", blankContent)
        );
        assertEquals("Content cannot be blank", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).save(any());
    }

    @Test
    void createPost_withContentTooLong_shouldThrowException() {
        String userId = "user123";
        String longContent = "a".repeat(2201);
        
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.createPost(userId, longContent)
        );
        
        assertEquals("Content cannot exceed 2200 characters", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).save(any());
    }

    @Test
    void createPost_withMaxValidContentLength_shouldSucceed() {
        String userId = "user123";
        String maxContent = "a".repeat(2200);
        Post expectedPost = new Post("post123", userId, maxContent, Instant.now());
        
        when(userRepository.existsById(userId)).thenReturn(true);
        when(postRepository.save(any(Post.class))).thenReturn(expectedPost);

        Post result = postService.createPost(userId, maxContent);

        assertNotNull(result);
        assertEquals(maxContent, result.content());
        verify(userRepository).existsById(userId);
        verify(postRepository).save(any(Post.class));
    }

    @Test
    void getUserPosts_withExistingUser_shouldReturnUserPosts() {
        String userId = "user123";
        List<Post> expectedPosts = List.of(
            new Post("post1", userId, "First post", Instant.now()),
            new Post("post2", userId, "Second post", Instant.now())
        );
        
        when(userRepository.existsById(userId)).thenReturn(true);
        when(postRepository.findByUserId(userId)).thenReturn(expectedPosts);

        List<Post> result = postService.getUserPosts(userId);

        assertEquals(expectedPosts, result);
        assertEquals(2, result.size());
        verify(userRepository).existsById(userId);
        verify(postRepository).findByUserId(userId);
    }

    @Test
    void getUserPosts_withNonExistentUser_shouldThrowException() {
        String userId = "nonexistent";
        
        when(userRepository.existsById(userId)).thenReturn(false);

        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.getUserPosts(userId)
        );
        
        assertEquals("User with ID 'nonexistent' does not exist", exception.getMessage());
        verify(userRepository).existsById(userId);
        verify(postRepository, never()).findByUserId(any());
    }

    @Test
    void getUserPosts_withNullUserId_shouldThrowException() {
        NullPointerException exception = assertThrows(
            NullPointerException.class,
            () -> postService.getUserPosts(null)
        );
        assertEquals("User ID cannot be null", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).findByUserId(any());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "   ", "\t", "\n"})
    void getUserPosts_withBlankUserId_shouldThrowException(String blankUserId) {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> postService.getUserPosts(blankUserId)
        );
        assertEquals("User ID cannot be blank", exception.getMessage());
        verify(userRepository, never()).existsById(any());
        verify(postRepository, never()).findByUserId(any());
    }

    @Test
    void getUserPosts_withExistingUserButNoPosts_shouldReturnEmptyList() {
        String userId = "user123";
        List<Post> emptyPosts = List.of();
        
        when(userRepository.existsById(userId)).thenReturn(true);
        when(postRepository.findByUserId(userId)).thenReturn(emptyPosts);

        List<Post> result = postService.getUserPosts(userId);

        assertTrue(result.isEmpty());
        verify(userRepository).existsById(userId);
        verify(postRepository).findByUserId(userId);
    }
}