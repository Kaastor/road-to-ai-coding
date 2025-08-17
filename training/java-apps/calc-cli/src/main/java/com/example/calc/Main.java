package com.example.calc;

public class Main {
    private static void usage() {
        System.out.println("Usage: calc <add|sub|mul|div> <a> <b>");
        System.out.println("Examples:");
        System.out.println("  calc add 2 3   -> 5");
        System.out.println("  calc div 7 3   -> 2");
    }

    public static void main(String[] args) {
        if (args.length != 3) {
            usage();
            System.exit(1);
        }

        String op = args[0];
        int a, b;
        try {
            a = Integer.parseInt(args[1]);
            b = Integer.parseInt(args[2]);
        } catch (NumberFormatException e) {
            System.err.println("Both <a> and <b> must be integers.");
            usage();
            System.exit(2);
            return;
        }

        try {
            int result = switch (op) {
                case "add" -> Calculator.add(a, b);
                case "sub" -> Calculator.sub(a, b);
                case "mul" -> Calculator.mul(a, b);
                case "div" -> Calculator.div(a, b);
                default -> { usage(); System.exit(3); yield 0; }
            };
            System.out.println(result);
        } catch (IllegalArgumentException ex) {
            System.err.println("Error: " + ex.getMessage());
            System.exit(4);
        }
    }
}