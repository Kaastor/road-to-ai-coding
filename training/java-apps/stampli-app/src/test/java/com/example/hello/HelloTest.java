package com.example.hello;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class HelloTest {
    @Test
    void defaultGreeting() {
        assertEquals("Hello, World!", Hello.greet(null));
        assertEquals("Hello, World!", Hello.greet(""));
    }

    @Test
    void namedGreeting() {
        assertEquals("Hello, Alice!", Hello.greet("Alice"));
    }
}