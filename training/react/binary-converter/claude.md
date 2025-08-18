# Claude.md

## Purpose

This claude.md file serves as the foundational guide for the Bin2Dec project development. It establishes project structure, development guidelines, and best practices for efficient development using Claude's AI capabilities. This document ensures consistent, high-quality code delivery while maximizing the benefits of AI-assisted development.

## Application Overview

**Project Name:** Bin2Dec - Binary to Decimal Converter

**Description:**
Binary is the number system all digital computers are based on. Therefore it's important for developers to understand binary, or base 2, mathematics. The purpose of Bin2Dec is to provide practice and understanding of how binary calculations work.

Bin2Dec allows the user to enter strings of up to 8 binary digits, 0's and 1's, in any sequence and then displays its decimal equivalent.

**Constraints:**
- Arrays may not be used to contain the binary digits entered by the user
- Determining the decimal equivalent of a particular binary digit in the sequence must be calculated using a single mathematical function, for example the natural logarithm. It's up to you to figure out which function to use.

**User Stories:**
- [ ] User can enter up to 8 binary digits in one input field
- [ ] User must be notified if anything other than a 0 or 1 was entered
- [ ] User views the results in a single output field containing the decimal (base 10) equivalent of the binary number that was entered

## Project Structure

```
bin2dec/
├── README.md
├── claude.md
├── src/
│   ├── index.html
│   ├── styles/
│   │   └── main.css
│   ├── scripts/
│   │   ├── main.js
│   │   ├── converter.js
│   │   └── validator.js
│   └── assets/
│       └── images/
├── tests/
│   ├── unit/
│   │   ├── converter.test.js
│   │   └── validator.test.js
│   └── integration/
│       └── app.test.js
├── docs/
│   ├── technical-specs.md
│   └── user-guide.md
├── .gitignore
├── package.json
└── LICENSE
```

## Development Guidelines

### Coding Standards and Best Practices

#### JavaScript Standards
- Use ES6+ modern JavaScript syntax
- Follow camelCase naming convention for variables and functions
- Use meaningful, descriptive variable and function names
- Implement proper error handling with try-catch blocks
- Add JSDoc comments for all functions
- Keep functions small and focused (single responsibility principle)
- Use const for immutable values, let for mutable variables

#### HTML/CSS Standards
- Use semantic HTML5 elements
- Follow BEM methodology for CSS class naming
- Ensure responsive design principles
- Maintain accessibility standards (ARIA labels, proper contrast)
- Use CSS custom properties for consistent theming

#### Code Example Template
```javascript
/**
 * Converts binary string to decimal using mathematical functions
 * @param {string} binaryString - Binary string input (0s and 1s only)
 * @returns {number} Decimal equivalent
 * @throws {Error} If input contains invalid characters
 */
function convertBinaryToDecimal(binaryString) {
    // Implementation following constraints
}
```

### Using Claude's AI Capabilities

#### Code Generation
- Provide Claude with specific requirements and constraints
- Request code reviews and optimization suggestions
- Ask for multiple implementation approaches
- Use Claude for debugging complex mathematical functions

#### Problem-Solving Approach
1. Break down complex problems into smaller components
2. Ask Claude to explain mathematical concepts (binary conversion algorithms)
3. Request validation of constraint compliance
4. Seek suggestions for edge case handling

#### Prompting Best Practices
- Be specific about constraints (no arrays, mathematical function requirement)
- Provide context about the educational nature of the project
- Request explanations along with code implementations
- Ask for test case suggestions

### Version Control Practices

#### Git Workflow
- Use feature branches for new functionality
- Commit messages should follow conventional commit format
- Create pull requests for code review
- Maintain clean commit history

#### Commit Message Format
```
type(scope): description

feat(converter): implement binary to decimal conversion using Math.pow
fix(validator): handle empty input edge case
docs(readme): add installation instructions
test(converter): add unit tests for edge cases
```

#### Branch Naming
- `feature/binary-converter`
- `fix/input-validation`
- `docs/user-guide`

## Testing and Quality Assurance

### Unit Testing Guidelines

#### Testing Framework
- Use Jest for JavaScript testing
- Maintain minimum 90% code coverage
- Test all public functions and edge cases

#### Test Categories
1. **Input Validation Tests**
   - Valid binary strings (0-8 digits)
   - Invalid characters detection
   - Empty input handling
   - Maximum length validation

2. **Conversion Logic Tests**
   - Single digit conversion (0, 1)
   - Multi-digit conversion
   - Maximum value (11111111 = 255)
   - Leading zeros handling

3. **UI Integration Tests**
   - Input field behavior
   - Output display formatting
   - Error message display
   - User interaction flow

#### Test Example Template
```javascript
describe('Binary to Decimal Converter', () => {
    test('should convert valid binary string to decimal', () => {
        expect(convertBinaryToDecimal('1010')).toBe(10);
    });

    test('should throw error for invalid input', () => {
        expect(() => convertBinaryToDecimal('102')).toThrow();
    });
});
```

### Quality Assurance Checklist
- [ ] All user stories implemented and tested
- [ ] Constraint compliance verified (no arrays, mathematical function used)
- [ ] Cross-browser compatibility tested
- [ ] Responsive design validated
- [ ] Accessibility standards met
- [ ] Performance optimized
- [ ] Error handling implemented
- [ ] Code documentation complete

## Resources and References

### Documentation Links
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [HTML5 Specification](https://html.spec.whatwg.org/)
- [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### API References
- [Math Object Methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math)
- [String Methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)
- [DOM Manipulation](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)

### Learning Materials
- [Binary Number System](https://www.khanacademy.org/math/algebra-home/alg-intro-to-algebra/algebra-alternate-number-bases/v/number-systems-introduction)
- [JavaScript Mathematical Functions](https://www.w3schools.com/js/js_math.asp)
- [Jest Testing Framework](https://jestjs.io/docs/getting-started)

### Mathematical References
- Binary to Decimal Conversion Algorithms
- Mathematical Functions for Base Conversion
- Logarithmic Calculations in JavaScript

## Project Milestones

1. **Phase 1:** Project Setup and Structure
2. **Phase 2:** Core Conversion Logic Implementation
3. **Phase 3:** User Interface Development
4. **Phase 4:** Input Validation and Error Handling
5. **Phase 5:** Testing and Quality Assurance
6. **Phase 6:** Documentation and Deployment