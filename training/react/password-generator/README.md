# Password Generator

Generate passwords based on certain characteristics selected by the user.

## Technical Stack

- Language: JavaScript (ES modules)
- Framework: React (functional components with hooks)
- Testing: Vitest, @testing-library/react, @testing-library/react-hooks
- Build Tool: Vite

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build production version
- `npm run test` - Run all tests
- `npm run preview` - Preview production build

## Project Structure

```
src/
├── components/     # React components
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
└── main.jsx       # Application entry point

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── setup.js       # Test setup configuration

public/
└── index.html     # HTML template
```

## Testing

Run single test file:
```bash
vitest run tests/unit/test-file.js
```

Run all tests:
```bash
npm run test
```