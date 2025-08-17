package com.example.calc;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    @Test void adds() { assertEquals(5, Calculator.add(2, 3)); }
    @Test void subs() { assertEquals(-1, Calculator.sub(2, 3)); }
    @Test void muls() { assertEquals(6, Calculator.mul(2, 3)); }
    @Test void divs() { assertEquals(2, Calculator.div(7, 3)); } // integer division
    @Test void divByZero() { assertThrows(IllegalArgumentException.class, () -> Calculator.div(1, 0)); }
}