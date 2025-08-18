# Binary Converter

A React application for converting numbers between different bases (binary, decimal, hexadecimal).

## Features

- Convert decimal numbers to binary
- Convert binary numbers to decimal
- Modern React with TypeScript
- Test-driven development with Vitest
- Fast development with Vite

## Getting Started

### Prerequisites

- Node.js (v20.19.0 or higher)
- npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server:
```bash
npm run dev
```

### Testing

Run tests:
```bash
npm test
```

Run tests with UI:
```bash
npm run test:ui
```

Run tests with coverage:
```bash
npm run test:coverage
```

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
├── test/          # Test setup and utilities
├── types/         # TypeScript type definitions
├── App.tsx        # Main application component
├── main.tsx       # Application entry point
└── index.css      # Global styles
```

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework
- **Testing Library** - Testing utilities
- **ESLint** - Code linting