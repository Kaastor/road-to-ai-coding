package com.example.instagram.repository;

import com.example.instagram.model.Post;
import java.util.List;
import java.util.Optional;

public interface PostRepository {
    Post save(Post post);
    Optional<Post> findById(String id);
    List<Post> findByUserId(String userId);
    List<Post> findAll();
    void deleteById(String id);
    boolean existsById(String id);
}