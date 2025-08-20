package com.example.hello;

public class Hello {
    public static String greet(String name) {
        String who = (name == null || name.isBlank()) ? "World" : name;
        return "Hello, " + who + "!";
    }

    public static void main(String[] args) {
        String name = (args.length > 0) ? args[0] : null;
        System.out.println(greet(name));
    }
}
