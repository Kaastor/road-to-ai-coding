package com.example.instagram.controller;

import com.example.instagram.model.Post;
import com.example.instagram.model.User;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.PostService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/posts")
public class PostController {
    private final PostService postService;
    private final AuthenticationService authenticationService;

    public PostController(PostService postService, AuthenticationService authenticationService) {
        this.postService = postService;
        this.authenticationService = authenticationService;
    }

    @PostMapping
    public ResponseEntity<?> createPost(@RequestHeader(value = "Session-Id", required = false) String sessionId,
                                       @RequestBody Map<String, String> request) {
        try {
            Optional<User> currentUser = authenticationService.getCurrentUser(sessionId);
            if (currentUser.isEmpty()) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Authentication required"));
            }

            String content = request.get("content");
            Post post = postService.createPost(currentUser.get().id(), content);
            
            return ResponseEntity.ok(Map.of(
                "id", post.id(),
                "userId", post.userId(),
                "content", post.content(),
                "createdAt", post.timestamp().toString(),
                "message", "Post created successfully"
            ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Failed to create post"));
        }
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<?> getUserPosts(@PathVariable String userId) {
        try {
            List<Post> posts = postService.getUserPosts(userId);
            
            List<Map<String, String>> postData = posts.stream()
                .map(post -> Map.of(
                    "id", post.id(),
                    "userId", post.userId(),
                    "content", post.content(),
                    "createdAt", post.timestamp().toString()
                ))
                .toList();
                
            return ResponseEntity.ok(Map.of(
                "posts", postData,
                "count", posts.size()
            ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Failed to get user posts"));
        }
    }

    @GetMapping("/my")
    public ResponseEntity<?> getMyPosts(@RequestHeader(value = "Session-Id", required = false) String sessionId) {
        try {
            Optional<User> currentUser = authenticationService.getCurrentUser(sessionId);
            if (currentUser.isEmpty()) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Authentication required"));
            }

            List<Post> posts = postService.getUserPosts(currentUser.get().id());
            
            List<Map<String, String>> postData = posts.stream()
                .map(post -> Map.of(
                    "id", post.id(),
                    "userId", post.userId(),
                    "content", post.content(),
                    "createdAt", post.timestamp().toString()
                ))
                .toList();
                
            return ResponseEntity.ok(Map.of(
                "posts", postData,
                "count", posts.size()
            ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Failed to get posts"));
        }
    }
}