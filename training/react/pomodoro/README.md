# Pomodoro Timer

A simple and effective Pomodoro Timer application built with React and Vite.

## About

The Pomodoro Technique is a time management method developed by Francesco Cirillo in the late 1980s. The technique uses a timer to break down work into intervals, traditionally 25 minutes in length, separated by short breaks (5 minutes).

## Features

- 25-minute work sessions
- 5-minute break sessions
- Start/pause functionality
- Reset timer
- Visual indication of work vs break time
- Clean, modern interface

## Project Structure

```
pomodoro/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── PomodoroTimer.jsx
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── setup.js           # Test configuration
├── package.json
├── vite.config.js
└── README.md
```

## Tech Stack

- **React** - UI library
- **Vite** - Build tool and development server
- **Vitest** - Testing framework
- **Testing Library** - Testing utilities
- **ESLint** - Code linting

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:5173`.

### Building

Build for production:
```bash
npm run build
```

### Testing

Run tests:
```bash
npm test
```

Run specific test file:
```bash
vitest run tests/unit/test-pomodoro-timer.js
```

Run tests with UI:
```bash
npm run test:ui
```

Run tests with coverage:
```bash
npm run test:coverage
```

### Linting

Run linter:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

## Usage

1. Click "Start" to begin a 25-minute work session
2. The timer will count down from 25:00 to 00:00
3. When the work session ends, it automatically switches to a 5-minute break
4. Use "Pause" to pause the timer at any time
5. Use "Reset" to return to the initial 25-minute work state

## Contributing

1. Follow the existing code style and structure
2. Write tests for new functionality
3. Run linter and tests before committing
4. Keep commits focused and descriptive

## License

MIT