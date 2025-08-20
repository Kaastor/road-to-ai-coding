package com.example.instagram;

import com.example.instagram.repository.InMemoryPostRepository;
import com.example.instagram.repository.InMemoryUserRepository;
import com.example.instagram.repository.PostRepository;
import com.example.instagram.repository.UserRepository;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.PostService;
import com.example.instagram.service.UserService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class InstagramWebApp {

    public static void main(String[] args) {
        SpringApplication.run(InstagramWebApp.class, args);
    }

    @Bean
    public UserRepository userRepository() {
        return new InMemoryUserRepository();
    }

    @Bean
    public PostRepository postRepository() {
        return new InMemoryPostRepository();
    }

    @Bean
    public UserService userService(UserRepository userRepository) {
        return new UserService(userRepository);
    }

    @Bean
    public AuthenticationService authenticationService(UserRepository userRepository) {
        return new AuthenticationService(userRepository);
    }

    @Bean
    public PostService postService(PostRepository postRepository, UserRepository userRepository) {
        return new PostService(postRepository, userRepository);
    }
}