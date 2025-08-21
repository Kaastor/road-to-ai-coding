# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
This project develops an API-based application for creating, training, and testing reinforcement learning (RL) agents focused on detecting radio frequency (RF) jamming using the RFRL Gym environment (from https://github.com/vtnsi/rfrl-gym). The application will wrap RFRL Gym's scenarios to simulate RF jamming detection tasks, allowing users to define custom detection environments, train agents (e.g., using Stable Baselines3), evaluate performance, and interact via a RESTful API. Key features include endpoints for training initiation, model saving/loading, real-time testing in simulated scenarios, and metrics reporting (e.g., detection accuracy, reward curves). It supports both single-agent and multi-agent setups for jamming detection, building on RFRL Gym's gamified RF spectrum simulations. The goal is to provide a scalable tool for RF research, enabling incremental development from basic detection to advanced multi-agent strategies.

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`

### Testing
# all tests
`poetry run python -m pytest`

# single test
`poetry run python -m pytest app/tests/test_app.py::test_hello_name -v`


## Project Structure

```
app/                          # Main application package
├── __init__.py              # Package initialization with version info
├── api/                     # FastAPI endpoints and routing
│   └── __init__.py
├── core/                    # Core functionality and business logic
│   └── __init__.py
├── models/                  # Data models and Pydantic schemas
│   └── __init__.py
├── scenarios/               # Custom RFRL Gym scenarios for jamming detection
│   └── __init__.py
├── training/                # RL training scripts and utilities
│   └── __init__.py
├── utils/                   # Utility functions and helpers
│   └── __init__.py
├── tests/                   # Unit and integration tests
│   └── test_app.py
└── app.py                   # Legacy app file (can be refactored)

rfrl-gym/                    # RFRL Gym repository (cloned dependency)
├── rfrl_gym/               # Core RFRL Gym package
├── scripts/                # Example and testing scripts
└── scenarios/              # Default scenario configurations

pyproject.toml              # Poetry configuration with dependencies
poetry.lock                 # Locked dependency versions
pytest.ini                  # Pytest configuration
test_setup.py              # Project setup verification script
CLAUDE.md                  # This file - project documentation
```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout


## Modular Implementation Plan

This plan is divided into incremental steps, each building on the previous. Complete one module before proceeding, testing at each stage. Use Git for version control, committing after each step.

### Step 1: Set Up Environment and Clone RFRL Gym
- Clone the RFRL Gym repository: `git clone https://github.com/vtnsi/rfrl-gym.git`.
- Create and activate a Python virtual environment: `python3 -m venv rfrl-app-venv` and `source rfrl-app-venv/bin/activate`.
- Install RFRL Gym editable: `pip install --editable .` (from inside the cloned repo).
- Test installation: Run `python scripts/preview_scenario.py -m abstract` to verify basic scenario rendering.
- Outcome: Functional RFRL Gym setup for local testing.

### Step 2: Define Custom Jamming Detection Scenarios
- Extend RFRL Gym's scenario generation to create jamming detection environments (e.g., modify existing scripts to include jamming signals as observations).
- Implement a simple single-agent environment where the agent observes RF spectrum data (abstract or IQ mode) and actions detect/predict jamming presence.
- Add support for multi-agent scenarios using the `marl-dev` branch: `git checkout marl-dev` and reinstall editable.
- Test: Run modified preview scripts to visualize detection scenarios.
- Outcome: Custom Gym environments ready for RL training.

### Step 3: Integrate RL Training Framework
- Install and integrate Stable Baselines3: `pip install -e ".[rl_packages]"`.
- Create training scripts: Wrap RFRL Gym environments in training loops (e.g., using PPO or DQN algorithms from Stable Baselines3).
- Add model saving/loading functionality (e.g., via `model.save()` and `model.load()`).
- Test: Train a basic agent on a detection scenario and evaluate with `python scripts/sb3_example.py -m abstract` (adapted for detection).
- Outcome: Trainable agents with saved models for jamming detection.

### Step 4: Develop API Backend
- Use Flask or FastAPI to create a RESTful API.
- Define endpoints:
  - `/train`: POST request with parameters (e.g., scenario type, episodes); initiates training and returns job ID.
  - `/test`: POST with model path and scenario; runs evaluation and returns metrics (e.g., accuracy, rewards).
  - `/status`: GET with job ID; checks training progress.
  - `/models`: GET/POST for listing/uploading models.
- Handle asynchronous training (e.g., using Celery or threading).
- Test: Run the API locally and send curl requests to train/test a sample agent.
- Outcome: API server operational for agent management.

### Step 5: Add Evaluation and Visualization Tools
- Implement metrics collection (e.g., detection rate, false positives) during testing.
- Add visualization endpoints (e.g., return plots of reward curves via Matplotlib, served as images).
- Support for comparing agents (e.g., before/after training, as in RFRL Gym examples).
- Test: Evaluate a trained model via API and verify metrics output.
- Outcome: Comprehensive testing capabilities with visual feedback.

### Step 6: Containerize and Deploy
- Create a Dockerfile for the application, including RFRL Gym and dependencies.
- Use Docker Compose for API server setup.
- Deploy to a cloud platform (e.g., Heroku or AWS) for public API access, or keep local.
- Add authentication (e.g., API keys) for secure usage.
- Test: Build and run the container, accessing API endpoints remotely.
- Outcome: Deployed, accessible application.

### Step 7: Documentation and Extensions
- Write API docs (e.g., using Swagger for FastAPI).
- Add examples: Scripts for users to interact with the API (train/test via Python requests).
- Extend for advanced features (e.g., hyperparameter tuning, integration with other RL libs like Ray).
- Test: Validate full workflow from training to testing via API.
- Outcome: Complete, user-friendly project.

### Needed Dependencies

- **Core Python and Setup**: Python 3.12+, pip, venv, wheel, setuptools.
- **RFRL Gym Specific**: From repo installation (includes numpy, gym; optional stable_baselines3 for RL).
- **RL Libraries**: stable-baselines3 (for training agents), torch (if using PyTorch-based models).
- **API Framework**: fastapi (or flask), uvicorn (for serving).
- **Async/Queueing**: celery (optional, for background training).
- **Visualization**: matplotlib (for plots).
- **Containerization**: docker.
- **Others**: git (for cloning), requests (for API testing).

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
