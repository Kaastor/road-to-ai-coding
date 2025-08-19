# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Project description: https://raw.githubusercontent.com/florinpop17/app-ideas/refs/heads/master/Projects/3-Advanced/Elevator-App.md (do not use this, it's just doc for developer)

## Project Overview
It's tough to think of a world without elevators. Especially if you have to
walk up and down 20 flights of stairs each day. But, if you think about it 
elevators were one of the original implementations of events and event handlers
long before web applications came on the scene.

The objective of the Elevator app is to simulate the operation of an elevator
and more importantly, how to handle the events generated when the buildings
occupants use it. This app simulates occupants calling for an elevator from
any floor and pressing the buttons inside the elevator to indicate the floor
they wish to go to. 

### Constraints

- You must implement a single event handler for the up and down buttons on
each floor. For example, if there are 4 floors a single event handler should
be implemented rather than 8 (two buttons per floor).
- Similarly, a single event handler should be implemented for all buttons on
the control panel in the elevator rather than a unique event handler for each
button.

## User Stories

-   [ ] User can see a cross section diagram of a building with four floors,
an elevator shaft, the elevator, and an up button on the first floor, up and 
down buttons on the second and third floors, and a down button on the fourth
floor.
-   [ ] User can see the elevator control panel with a button for each of the
floors to the side of the diagram.
-   [ ] User can click the up and down button on any floor to call the 
elevator.
-   [ ] User can expect that clicking the up and down buttons on any floor
to request the elevator will be queued and serviced in the sequence they were
clicked.
-   [ ] User can see the elevator move up and down the shaft to the floor it
was called to.
-   [ ] User can click the elevator control panel to select the floor it
should travel to.
-   [ ] User can expect the elevator to pause for 5 seconds waiting for a
floor button on the control panel to be clicked. If a floor button isn't
clicked within that time the elevator will process the next call request.
-   [ ] User can expect the elevator to return to the first floor when there
are no requests to process.

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`

### Testing
# all tests
pytest -c ../pyproject.toml --rootdir ..

# single test
pytest -c ../pyproject.toml --rootdir .. ../tests/path/to/test_file.py::test_function_name -v


## Project Structure

```
/
├── elevator/                    # Main application package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # CLI entry point
│   ├── app.py                  # Core elevator application logic
│   ├── CLAUDE.md               # This guidance file
│   └── tests/                  # Test suite
│       └── test_app.py         # Application tests
├── pyproject.toml              # Project configuration and dependencies
├── poetry.lock                 # Locked dependency versions
└── pytest.ini                 # pytest configuration

```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout

### Dev dependencies

- FastAPI: Web framework for building the API backend, handling routes, WebSockets for real-time updates, and serving static files (e.g., HTML/JS/CSS for the UI).
- Uvicorn: ASGI server to run the FastAPI application.
- asyncio: Standard library for handling asynchronous event queues, timers (e.g., 5-second pause), and simulation logic without external dependencies.
- Pydantic: Included with FastAPI; used for data validation and modeling elevator state/requests.
- HTML/CSS/JavaScript: Vanilla frontend (no frameworks like React) for the UI diagram, buttons, and event handling; use CSS for positioning/animation of the elevator, JS for button clicks sending API requests or WebSocket messages.
- WebSockets (via FastAPI): For real-time state updates to the client (e.g., elevator position changes) to avoid polling.

## Code Style Guidelines

- **Type hints**: Use native Python type hints (e.g., `list[str]` not `List[str]`)
- **Documentation**: Google-style docstrings for all modules, classes, functions
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Function length**: Keep functions short (< 30 lines) and single-purpose
- **PEP 8**: Follow PEP 8 style guide

## Python Best Practices

- **File handling**: Prefer `pathlib.Path` over `os.path`
- **Debugging**: Use `logging` module instead of `print`
- **Error handling**: Use specific exceptions with context messages and proper logging
- **Data structures**: Use list/dict comprehensions for concise, readable code
- **Function arguments**: Avoid mutable default arguments
- **Data containers**: Leverage `dataclasses` to reduce boilerplate
- **Configuration**: Use environment variables (via `python-dotenv`) for configuration

## Development Patterns & Best Practices

- **Favor simplicity**: Choose the simplest solution that meets requirements
- **DRY principle**: Avoid code duplication; reuse existing functionality
- **Configuration management**: Use environment variables for different environments
- **Focused changes**: Only implement explicitly requested or fully understood changes
- **Preserve patterns**: Follow existing code patterns when fixing bugs
- **File size**: Keep files under 300 lines; refactor when exceeding this limit
- **Test coverage**: Write comprehensive unit and integration tests with `pytest`; include fixtures
- **Test structure**: Use table-driven tests with parameterization for similar test cases
- **Mocking**: Use unittest.mock for external dependencies; don't test implementation details
- **Modular design**: Create reusable, modular components
- **Logging**: Implement appropriate logging levels (debug, info, error)
- **Error handling**: Implement robust error handling for production reliability
- **Security best practices**: Follow input validation and data protection practices
- **Performance**: Optimize critical code sections when necessary


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
