You are an expert in Test-Driven Development (TDD) for JavaScript React applications. Your task is to generate a file named CLAUDE.md, which will serve as a reference guide for a "Claude Code agent" during the development of a proof-of-concept (POC) React app. The app is for quick feature testing only—no Git, deployment, or production concerns. Focus on aligning the process strictly with TDD principles to enable rapid iterations: write failing tests first, implement minimal code to pass them, refactor, and repeat.

Input: The project description is:
"""

"""


Structure CLAUDE.md as a Markdown file with the following sections, keeping content concise, actionable, and tailored to the project description:

1. **Project Overview**: Summarize the project description, key features, and goals. Emphasize it's a POC in React with no external dependencies beyond standard React ecosystem (e.g., React, React-DOM, testing-library/react for tests).

2. **TDD Workflow**: Outline the step-by-step TDD process:
   - Red: Write a failing test for a specific feature or component.
   - Green: Implement the minimal code to make the test pass.
   - Refactor: Clean up code while keeping tests green.
   - Iterate: Repeat for each feature, building incrementally.
   - Use Jest and @testing-library/react for testing. Assume a basic setup with create-react-app or equivalent.

3. **Component Breakdown**: List the main React components needed, based on the project description. For each:
   - Describe its purpose.
   - Suggest initial TDD steps (e.g., test for rendering, state changes, interactions).

4. **Feature Roadmap**: Break the project into small, testable features or user stories. Prioritize them for iterative development. For each feature:
   - Define acceptance criteria as test cases.
   - Suggest edge cases to test.

5. **Best Practices**: Include React-specific TDD tips, such as testing hooks with @testing-library/react-hooks, mocking APIs if needed (use MSW or jest.mock), and ensuring components are pure and testable. Remind to keep the app simple for quick POC validation.

6. **Iteration Guidelines**: Advise on quick cycles: Aim for 5-15 minute iterations per test-implement-refactor loop. If stuck, revisit tests or simplify features.

When creating a CLAUDE.md file use official Anthropic best practices and resources for Claude Code development.
Output only the contents of CLAUDE.md, starting with # CLAUDE.md as the title. Do not add any external commentary.

Improve over this template:

```
# Project: [Your App Name]
## Last Updated: [Today's Date]

## Overview
[Write a 2-3 sentence description of what your app will do]

## Technical Stack
- Language: [e.g., Python 3.11, Node.js 20]
- Framework: [e.g., FastAPI, Express, React]
- Testing: [e.g., pytest, Jest, React Testing Library]
- Database: [if applicable]

## Features (Prioritized)
### Must Have (MVP)
1. [ ] Feature 1
2. [ ] Feature 2
3. [ ] Feature 3

### Should Have
1. [ ] Feature 4
2. [ ] Feature 5

### Nice to Have
1. [ ] Feature 6

## Current Context
**Working on:** Initial project setup
**Next step:** Set up testing framework
**Blockers:** None

## Architecture Decisions
- [Record key decisions here]

## Code Patterns
- [Document patterns as you establish them]

## Test Strategy
- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user paths
```