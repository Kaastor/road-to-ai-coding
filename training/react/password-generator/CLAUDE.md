# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Generate passwords based on certain characteristics selected by the user.

## Technical Stack
- Language: JavaScript (ES modules)
- Framework: React (functional components with hooks)
- Build Tool: Vite
- Testing: Vitest, @testing-library/react

## Build and Test Commands

- `npm start` - Start development server (IMPORTANT: Never run this command directly; ask the user to start the server
  as needed)
- `npm run build` - Build production version
- `npm run test` - Run all tests
- `vitest run tests/unit/App.test.jsx` - Run a single test file

## Core Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance


## Implementation Priority
1. Core functionality first (render, state)
2. User interactions
  - Implement only minimal working functionality
3. Minimal unit tests

### Iteration Target
- Around 5 min per cycle
- Keep tests simple, just core functionality checks
- Prioritize working code over perfection for POCs

## Code Style Guidelines

- **Modules**: ES modules with import/export syntax (type: "module")
- **JavaScript Target**: ES2020 with strict null checks
- **Error Handling**: Use try/catch with explicit error messages that provide context about what failed
- **Naming**: camelCase for variables and functions, PascalCase for classes
- **Imports**: Group by source (internal/external) with proper separation
- **Documentation**: Use JSDoc for public APIs and complex functions, add comments for non-obvious code
- **Error Messages**: Use consistent, specific error messages (e.g., "Track buffer overflow" instead of "Overflow in disc building")


### Code Architecture

- **General Principles**:
  - Follow the existing code style and structure
  - Use `const` and `let` instead of `var`
  - Avoid global variables; use module scope
  - Use arrow functions for callbacks
  - Prefer template literals over string concatenation
  - Use destructuring for objects and arrays when appropriate
  - Use async/await for asynchronous code instead of callbacks or promises
  - Minimise special case handling - prefer explicit over implicit behaviour

## Project Structure

```
├── CLAUDE.md                 # Project guidance for Claude Code
├── README.md                 # Project documentation
├── package.json              # Dependencies and scripts
├── vite.config.js           # Vite configuration with Vitest setup
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── main.jsx             # Application entry point
│   ├── components/          # React components
│   │   └── App.jsx          # Main App component
│   ├── hooks/               # Custom React hooks
│   └── utils/               # Utility functions
└── tests/
    ├── setup.js             # Test setup configuration
    ├── unit/                # Unit tests
    │   └── App.test.jsx     # App component tests
    └── integration/         # Integration tests
```
