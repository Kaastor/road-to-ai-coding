package com.example.instagram;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureWebMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;

@SpringBootTest
@AutoConfigureWebMvc
class WebInterfaceIntegrationTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    private MockMvc getMockMvc() {
        return MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    void shouldRenderIndexPageWithNavigationAndContent() throws Exception {
        getMockMvc().perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/html;charset=UTF-8"))
                .andExpect(content().string(containsString("Instagram Clone")))
                .andExpect(content().string(containsString("Home")))
                .andExpect(content().string(containsString("Register")))
                .andExpect(content().string(containsString("Login")))
                .andExpect(content().string(containsString("Posts")))
                .andExpect(content().string(containsString("API Docs")));
    }

    @Test
    void shouldRenderRegisterPageWithForm() throws Exception {
        getMockMvc().perform(get("/register"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/html;charset=UTF-8"))
                .andExpect(content().string(containsString("Create Account")))
                .andExpect(content().string(containsString("Username")))
                .andExpect(content().string(containsString("Email")))
                .andExpect(content().string(containsString("Password")))
                .andExpect(content().string(containsString("registerForm")));
    }

    @Test
    void shouldRenderLoginPageWithForm() throws Exception {
        getMockMvc().perform(get("/login"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/html;charset=UTF-8"))
                .andExpect(content().string(containsString("Sign In")))
                .andExpect(content().string(containsString("Username or Email")))
                .andExpect(content().string(containsString("Password")))
                .andExpect(content().string(containsString("loginForm")));
    }

    @Test
    void shouldRenderPostsPageWithCreatePostSection() throws Exception {
        getMockMvc().perform(get("/posts"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/html;charset=UTF-8"))
                .andExpect(content().string(containsString("Posts")))
                .andExpect(content().string(containsString("Authentication Required")))
                .andExpect(content().string(containsString("Create New Post")))
                .andExpect(content().string(containsString("createPostForm")));
    }

    @Test
    void shouldRenderApiDocsPageWithEndpoints() throws Exception {
        getMockMvc().perform(get("/api-docs"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/html;charset=UTF-8"))
                .andExpect(content().string(containsString("API Documentation")))
                .andExpect(content().string(containsString("/api/users/register")))
                .andExpect(content().string(containsString("/api/users/login")))
                .andExpect(content().string(containsString("/api/posts")));
    }

    @Test
    void shouldServeCSSStyleSheet() throws Exception {
        getMockMvc().perform(get("/css/style.css"))
                .andExpect(status().isOk())
                .andExpect(content().contentType("text/css"))
                .andExpect(content().string(containsString("Instagram Clone - Shared Styles")))
                .andExpect(content().string(containsString(".nav")))
                .andExpect(content().string(containsString(".form-container")));
    }
}