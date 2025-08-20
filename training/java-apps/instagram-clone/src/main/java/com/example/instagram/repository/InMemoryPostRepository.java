package com.example.instagram.repository;

import com.example.instagram.model.Post;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public class InMemoryPostRepository implements PostRepository {
    private final Map<String, Post> posts = new ConcurrentHashMap<>();

    @Override
    public Post save(Post post) {
        Objects.requireNonNull(post, "Post cannot be null");
        posts.put(post.id(), post);
        return post;
    }

    @Override
    public Optional<Post> findById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        return Optional.ofNullable(posts.get(id));
    }

    @Override
    public List<Post> findByUserId(String userId) {
        Objects.requireNonNull(userId, "User ID cannot be null");
        return posts.values().stream()
                .filter(post -> post.userId().equals(userId))
                .toList();
    }

    @Override
    public List<Post> findAll() {
        return List.copyOf(posts.values());
    }

    @Override
    public void deleteById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        posts.remove(id);
    }

    @Override
    public boolean existsById(String id) {
        Objects.requireNonNull(id, "ID cannot be null");
        return posts.containsKey(id);
    }
}