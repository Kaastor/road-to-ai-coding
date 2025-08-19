# Elevator App

A Python-based elevator simulation with web interface that demonstrates event handling, state management, and real-time UI updates.

## Overview

This application simulates the operation of a 4-floor elevator system with:
- Call buttons on each floor (up/down)
- Elevator control panel with floor selection
- Real-time visual representation of elevator movement
- Event-driven request processing with proper queuing

## Features

- **Cross-section building view** with 4 floors and elevator shaft
- **Interactive call buttons** for summoning elevator from any floor
- **Control panel** for floor selection inside the elevator
- **Real-time status updates** showing current floor, direction, and queue
- **Automatic queuing** of requests processed in sequence
- **5-second passenger wait time** at each stop
- **Return to ground floor** when idle

## Technical Stack

- **Backend**: FastAPI with async/await for handling concurrent requests
- **Frontend**: Vanilla HTML/CSS/JavaScript with real-time polling
- **State Management**: Python dataclasses and enums
- **Testing**: pytest with async support
- **Server**: Uvicorn ASGI server

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry (recommended) or pip

### Installation

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the application:
   ```bash
   poetry run elevator
   ```

3. Open your browser to `http://127.0.0.1:8000/static/index.html`

### Testing

Run all tests:
```bash
poetry run python -m pytest
```

Run specific test:
```bash
poetry run python -m pytest elevator/tests/test_elevator.py::TestElevator::test_initialization -v
```

## Project Structure

```
elevator/
├── __init__.py
├── app.py              # Main entry point
├── api.py              # FastAPI endpoints
├── elevator.py         # Core elevator logic
├── models.py           # Data models and enums
├── static/             # Web interface files
│   ├── index.html      # Main UI
│   ├── style.css       # Styling and animations
│   └── script.js       # Client-side event handling
└── tests/              # Test suite
    ├── test_models.py  # Model tests
    ├── test_elevator.py # Core logic tests
    └── test_api.py     # API endpoint tests
```

## API Endpoints

- `GET /` - Application info
- `GET /status` - Current elevator status
- `POST /call` - Call elevator to floor with direction
- `POST /select` - Select destination floor from control panel

## Usage

1. **Call Elevator**: Click up/down buttons on any floor
2. **Select Floor**: Click floor buttons in the control panel
3. **Monitor Status**: Watch real-time updates in the status display
4. **View Movement**: Observe elevator car animation in the building diagram

## Development

The application follows clean architecture principles:
- **Models**: Define data structures and enums
- **Core Logic**: Handles elevator state and movement
- **API Layer**: Provides REST endpoints for client interaction
- **UI Layer**: Implements real-time visual interface

### Key Constraints Implemented

- Single event handler for all up/down floor buttons
- Single event handler for all control panel buttons
- Proper request queuing and sequential processing
- 5-second wait time at each stop
- Automatic return to ground floor when idle