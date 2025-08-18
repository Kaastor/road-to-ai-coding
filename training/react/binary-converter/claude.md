# CLAUDE.md

## Last Updated: August 18, 2025

## Project Overview
Bin2Dec is a proof-of-concept React app for practicing binary-to-decimal conversion. Users enter up to 8 binary digits (0s and 1s) in a single input field, with validation for invalid inputs, and view the decimal equivalent in an output field. Key goals: Adhere to constraints (no arrays for digits, use a single math function like Math.pow for conversion), focus on TDD for rapid iterations, and keep it simple as a POC—no Git, deployment, or external deps beyond React, React DOM, Jest, and @testing-library/react.

## Technical Stack
- Language: JavaScript (ES modules)
- Framework: React (functional components with hooks)
- Testing: Jest, @testing-library/react, @testing-library/react-hooks

## TDD Workflow
Follow strict TDD for incremental development:
- **Red**: Write a failing test for a specific behavior (e.g., component renders without crashing).
- **Green**: Add minimal code to pass the test (e.g., basic component skeleton).
- **Refactor**: Clean up code (e.g., improve readability, extract logic) while ensuring tests remain green.
- **Iterate**: Repeat for next feature, committing changes mentally or via notes—aim for small steps.
Use Jest for test running and @testing-library/react for DOM assertions. Assume a basic setup like create-react-app. Start with `npm test` to watch tests.

## Component Breakdown
Break the app into testable React components. For each, begin TDD with rendering tests, then add interaction and state tests.

- **App**: Root component managing overall state and layout.
  - Purpose: Orchestrates input, validation, conversion, and output.
  - Initial TDD: Test it renders input and output; test state updates on input change.

- **BinaryInput**: Handles user input for binary string.
  - Purpose: Accepts input, validates (only 0/1, max 8 chars), notifies on errors.
  - Initial TDD: Test rendering with placeholder; test onChange updates value; test validation error display.

- **DecimalOutput**: Displays converted decimal value.
  - Purpose: Shows result or empty/default state.
  - Initial TDD: Test renders "0" initially; test updates on prop change.

- **ConverterLogic (hook or util)**: Performs binary-to-decimal conversion.
  - Purpose: Validates input and computes decimal using Math.pow (no arrays).
  - Initial TDD: Test conversion for valid binaries (e.g., "101" -> 5); test throws/returns error for invalid.

## Feature Roadmap
Prioritize features from user stories for iterative TDD. Each includes acceptance criteria as test cases and edge cases.

### Must Have (MVP)
1. [ ] User can enter up to 8 binary digits in one input field.
   - Acceptance: Test input accepts 8 chars; limits to 8; onChange updates state.
   - Edge cases: Empty input; exactly 8 chars; >8 chars (truncate or prevent).

2. [ ] User notified if anything other than 0 or 1 entered.
   - Acceptance: Test shows error message on invalid char (e.g., "2", "a"); clears on valid input.
   - Edge cases: Mixed valid/invalid; leading/trailing spaces; non-string inputs.

3. [ ] User views decimal equivalent in output field.
   - Acceptance: Test converts valid binary to decimal (e.g., "111" -> 7); updates on input change.
   - Edge cases: "0" -> 0; "1" -> 1; all 1s (255); invalid input shows 0 or error.

### Should Have
1. [ ] Real-time conversion on input change.
   - Acceptance: Test useEffect or onChange triggers conversion.
   - Edge cases: Rapid typing; invalid then valid transitions.

### Nice to Have
1. [ ] Accessibility features (e.g., ARIA labels).
   - Acceptance: Test component has proper labels.
   - Edge cases: Screen reader compatibility (manual verify if needed).

## Current Context
**Working on:**
User can enter up to 8 binary digits in one input field.
- Acceptance: Test input accepts 8 chars; limits to 8; onChange updates state.
- Edge cases: Empty input; exactly 8 chars; >8 chars (truncate or prevent).
**Next step:** Write failing test for input validation.

## Architecture Decisions
- Use functional components and hooks for state/logic separation.
- No arrays for binary digits; process as string with Math.pow(2, position).
- Keep pure functions for conversion to enable easy unit testing.

## Code Patterns
- Destructure props and imports.
- Use const for immutability.
- Export components/utils for testing.
- Follow TDD: Tests in `__tests__` folders, named `<Component>.test.js`.

## Test Strategy
- Unit tests: Pure functions (e.g., conversion logic) with Jest expect.
- Integration tests: Component interactions with @testing-library/react (e.g., fireEvent.change).
- Hooks tests: Use @testing-library/react-hooks for custom hooks.
- Mock if needed: Use jest.mock for any future deps (none planned).
- Coverage: Aim for 100% on logic; focus on behavior over snapshots.

## Best Practices
Align with Anthropic's Claude Code guidelines: Use this CLAUDE.md for project-specific instructions; iterate with /init for setup if needed; be specific in prompts (e.g., "Write TDD for BinaryInput validation").
React TDD tips: Test components as users interact (queryByRole, fireEvent); use act() for async; keep components pure (props in, JSX out); mock APIs with jest.mock if added later. Ensure quick POC: No styling beyond basics, focus on functionality.

## Iteration Guidelines
Aim for 5-15 minute red-green-refactor cycles. If stuck, simplify feature or revisit test specificity. Use checklists for complex flows (e.g., validation + conversion). Course-correct early by confirming plans before coding.