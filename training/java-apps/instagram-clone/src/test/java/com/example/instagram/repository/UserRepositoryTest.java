package com.example.instagram.repository;

import com.example.instagram.model.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class UserRepositoryTest {
    
    private UserRepository repository;
    private User testUser;

    @BeforeEach
    void setUp() {
        repository = new InMemoryUserRepository();
        testUser = new User("user1", "testuser", "test@example.com", "password123");
    }

    @Test
    void shouldSaveAndFindUserById() {
        User savedUser = repository.save(testUser);
        
        assertEquals(testUser, savedUser);
        
        Optional<User> foundUser = repository.findById("user1");
        assertTrue(foundUser.isPresent());
        assertEquals(testUser, foundUser.get());
    }

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        Optional<User> foundUser = repository.findById("nonexistent");
        assertFalse(foundUser.isPresent());
    }

    @Test
    void shouldFindUserByUsername() {
        repository.save(testUser);
        
        Optional<User> foundUser = repository.findByUsername("testuser");
        assertTrue(foundUser.isPresent());
        assertEquals(testUser, foundUser.get());
    }

    @Test
    void shouldFindUserByEmail() {
        repository.save(testUser);
        
        Optional<User> foundUser = repository.findByEmail("test@example.com");
        assertTrue(foundUser.isPresent());
        assertEquals(testUser, foundUser.get());
    }

    @Test
    void shouldReturnAllUsers() {
        User user2 = new User("user2", "testuser2", "test2@example.com", "password123");
        
        repository.save(testUser);
        repository.save(user2);
        
        List<User> allUsers = repository.findAll();
        assertEquals(2, allUsers.size());
        assertTrue(allUsers.contains(testUser));
        assertTrue(allUsers.contains(user2));
    }

    @Test
    void shouldDeleteUserById() {
        repository.save(testUser);
        assertTrue(repository.existsById("user1"));
        
        repository.deleteById("user1");
        assertFalse(repository.existsById("user1"));
        assertFalse(repository.findById("user1").isPresent());
    }

    @Test
    void shouldCheckIfUserExistsById() {
        assertFalse(repository.existsById("user1"));
        
        repository.save(testUser);
        assertTrue(repository.existsById("user1"));
    }

    @Test
    void shouldCheckIfUserExistsByUsername() {
        assertFalse(repository.existsByUsername("testuser"));
        
        repository.save(testUser);
        assertTrue(repository.existsByUsername("testuser"));
    }

    @Test
    void shouldCheckIfUserExistsByEmail() {
        assertFalse(repository.existsByEmail("test@example.com"));
        
        repository.save(testUser);
        assertTrue(repository.existsByEmail("test@example.com"));
    }

    @Test
    void shouldThrowExceptionWhenSavingNullUser() {
        assertThrows(NullPointerException.class, () -> repository.save(null));
    }

    @Test
    void shouldThrowExceptionWhenFindingByNullId() {
        assertThrows(NullPointerException.class, () -> repository.findById(null));
    }

    @Test
    void shouldThrowExceptionWhenFindingByNullUsername() {
        assertThrows(NullPointerException.class, () -> repository.findByUsername(null));
    }

    @Test
    void shouldThrowExceptionWhenFindingByNullEmail() {
        assertThrows(NullPointerException.class, () -> repository.findByEmail(null));
    }
}