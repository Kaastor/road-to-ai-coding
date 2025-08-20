package com.example.instagram.service;

import com.example.instagram.model.Post;
import com.example.instagram.repository.PostRepository;
import com.example.instagram.repository.UserRepository;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

public class PostService {
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    public PostService(PostRepository postRepository, UserRepository userRepository) {
        this.postRepository = Objects.requireNonNull(postRepository, "PostRepository cannot be null");
        this.userRepository = Objects.requireNonNull(userRepository, "UserRepository cannot be null");
    }

    public Post createPost(String userId, String content) {
        Objects.requireNonNull(userId, "User ID cannot be null");
        Objects.requireNonNull(content, "Content cannot be null");

        if (userId.isBlank()) {
            throw new IllegalArgumentException("User ID cannot be blank");
        }
        if (content.isBlank()) {
            throw new IllegalArgumentException("Content cannot be blank");
        }
        if (content.length() > 2200) {
            throw new IllegalArgumentException("Content cannot exceed 2200 characters");
        }

        if (!userRepository.existsById(userId)) {
            throw new IllegalArgumentException("User with ID '" + userId + "' does not exist");
        }

        String postId = UUID.randomUUID().toString();
        Post post = new Post(postId, userId, content, Instant.now());
        
        return postRepository.save(post);
    }

    public List<Post> getUserPosts(String userId) {
        Objects.requireNonNull(userId, "User ID cannot be null");
        
        if (userId.isBlank()) {
            throw new IllegalArgumentException("User ID cannot be blank");
        }

        if (!userRepository.existsById(userId)) {
            throw new IllegalArgumentException("User with ID '" + userId + "' does not exist");
        }

        return postRepository.findByUserId(userId);
    }
}