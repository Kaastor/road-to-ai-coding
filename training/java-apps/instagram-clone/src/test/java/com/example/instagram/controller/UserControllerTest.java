package com.example.instagram.controller;

import com.example.instagram.model.User;
import com.example.instagram.service.AuthenticationService;
import com.example.instagram.service.UserService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @MockBean
    private AuthenticationService authenticationService;

    @Autowired
    private ObjectMapper objectMapper;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User("test-id", "testuser", "test@example.com", "password123");
    }

    @Test
    void shouldRegisterUserSuccessfully() throws Exception {
        when(userService.register(anyString(), anyString(), anyString())).thenReturn(testUser);

        Map<String, String> request = Map.of(
            "username", "testuser",
            "email", "test@example.com",
            "password", "password123"
        );

        mockMvc.perform(post("/api/users/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("testuser"))
                .andExpect(jsonPath("$.email").value("test@example.com"))
                .andExpect(jsonPath("$.message").value("User registered successfully"));
    }

    @Test
    void shouldLoginSuccessfully() throws Exception {
        when(authenticationService.login(anyString(), anyString())).thenReturn(Optional.of("session-123"));

        Map<String, String> request = Map.of(
            "usernameOrEmail", "testuser",
            "password", "password123"
        );

        mockMvc.perform(post("/api/users/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sessionId").value("session-123"))
                .andExpect(jsonPath("$.message").value("Login successful"));
    }

    @Test
    void shouldReturnCurrentUserInfo() throws Exception {
        when(authenticationService.getCurrentUser("session-123")).thenReturn(Optional.of(testUser));

        mockMvc.perform(get("/api/users/me")
                .header("Session-Id", "session-123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("testuser"))
                .andExpect(jsonPath("$.email").value("test@example.com"));
    }

    @Test
    void shouldReturnUnauthorizedForInvalidSession() throws Exception {
        when(authenticationService.getCurrentUser("invalid-session")).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/users/me")
                .header("Session-Id", "invalid-session"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.error").value("Not authenticated"));
    }
}