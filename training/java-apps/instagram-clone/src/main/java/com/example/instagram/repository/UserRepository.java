package com.example.instagram.repository;

import com.example.instagram.model.User;
import java.util.List;
import java.util.Optional;

public interface UserRepository {
    User save(User user);
    Optional<User> findById(String id);
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    List<User> findAll();
    void deleteById(String id);
    boolean existsById(String id);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}