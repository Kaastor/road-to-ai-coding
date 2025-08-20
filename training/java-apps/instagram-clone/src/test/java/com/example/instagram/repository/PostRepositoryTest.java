package com.example.instagram.repository;

import com.example.instagram.model.Post;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class PostRepositoryTest {
    
    private PostRepository repository;
    private Post testPost;
    private Post testPost2;

    @BeforeEach
    void setUp() {
        repository = new InMemoryPostRepository();
        testPost = new Post("post1", "user1", "Hello World!", Instant.parse("2024-01-01T10:00:00Z"));
        testPost2 = new Post("post2", "user2", "Another post", Instant.parse("2024-01-01T11:00:00Z"));
    }

    @Test
    void shouldSaveAndFindPostById() {
        Post savedPost = repository.save(testPost);
        
        assertEquals(testPost, savedPost);
        
        Optional<Post> foundPost = repository.findById("post1");
        assertTrue(foundPost.isPresent());
        assertEquals(testPost, foundPost.get());
    }

    @Test
    void shouldReturnEmptyWhenPostNotFound() {
        Optional<Post> foundPost = repository.findById("nonexistent");
        assertFalse(foundPost.isPresent());
    }

    @Test
    void shouldFindPostsByUserId() {
        Post userPost1 = new Post("post1", "user1", "First post", Instant.now());
        Post userPost2 = new Post("post2", "user1", "Second post", Instant.now());
        Post otherUserPost = new Post("post3", "user2", "Other user post", Instant.now());
        
        repository.save(userPost1);
        repository.save(userPost2);
        repository.save(otherUserPost);
        
        List<Post> userPosts = repository.findByUserId("user1");
        assertEquals(2, userPosts.size());
        assertTrue(userPosts.contains(userPost1));
        assertTrue(userPosts.contains(userPost2));
        assertFalse(userPosts.contains(otherUserPost));
    }

    @Test
    void shouldReturnEmptyListWhenNoPostsForUser() {
        repository.save(testPost);
        
        List<Post> userPosts = repository.findByUserId("nonexistentuser");
        assertTrue(userPosts.isEmpty());
    }

    @Test
    void shouldReturnAllPosts() {
        repository.save(testPost);
        repository.save(testPost2);
        
        List<Post> allPosts = repository.findAll();
        assertEquals(2, allPosts.size());
        assertTrue(allPosts.contains(testPost));
        assertTrue(allPosts.contains(testPost2));
    }

    @Test
    void shouldDeletePostById() {
        repository.save(testPost);
        assertTrue(repository.existsById("post1"));
        
        repository.deleteById("post1");
        assertFalse(repository.existsById("post1"));
        assertFalse(repository.findById("post1").isPresent());
    }

    @Test
    void shouldCheckIfPostExistsById() {
        assertFalse(repository.existsById("post1"));
        
        repository.save(testPost);
        assertTrue(repository.existsById("post1"));
    }

    @Test
    void shouldThrowExceptionWhenSavingNullPost() {
        assertThrows(NullPointerException.class, () -> repository.save(null));
    }

    @Test
    void shouldThrowExceptionWhenFindingByNullId() {
        assertThrows(NullPointerException.class, () -> repository.findById(null));
    }

    @Test
    void shouldThrowExceptionWhenFindingByNullUserId() {
        assertThrows(NullPointerException.class, () -> repository.findByUserId(null));
    }

    @Test
    void shouldThrowExceptionWhenDeletingByNullId() {
        assertThrows(NullPointerException.class, () -> repository.deleteById(null));
    }

    @Test
    void shouldThrowExceptionWhenCheckingExistsByNullId() {
        assertThrows(NullPointerException.class, () -> repository.existsById(null));
    }
}