package com.example.instagram.repository;

import com.example.instagram.model.User;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public class InMemoryUserRepository implements UserRepository {
    private final Map<String, User> users = new ConcurrentHashMap<>();

    @Override
    public User save(User user) {
        Objects.requireNonNull(user, "User cannot be null");
        users.put(user.id(), user);
        return user;
    }

    @Override
    public Optional<User> findById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        return Optional.ofNullable(users.get(id));
    }

    @Override
    public Optional<User> findByUsername(String username) {
        Objects.requireNonNull(username, "Username cannot be null");
        return users.values().stream()
                .filter(user -> user.username().equals(username))
                .findFirst();
    }

    @Override
    public Optional<User> findByEmail(String email) {
        Objects.requireNonNull(email, "Email cannot be null");
        return users.values().stream()
                .filter(user -> user.email().equals(email))
                .findFirst();
    }

    @Override
    public List<User> findAll() {
        return List.copyOf(users.values());
    }

    @Override
    public void deleteById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        users.remove(id);
    }

    @Override
    public boolean existsById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        return users.containsKey(id);
    }

    @Override
    public boolean existsByUsername(String username) {
        Objects.requireNonNull(username, "Username cannot be null");
        return users.values().stream()
                .anyMatch(user -> user.username().equals(username));
    }

    @Override
    public boolean existsByEmail(String email) {
        Objects.requireNonNull(email, "Email cannot be null");
        return users.values().stream()
                .anyMatch(user -> user.email().equals(email));
    }
}