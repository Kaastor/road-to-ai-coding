# Training App MPC

A Python training application built with Poetry and pytest for learning and experimentation.

## Project Structure

```
training-app-mpc/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── app.py             # Main application module
│   ├── config/            # Configuration management
│   ├── core/              # Core business logic
│   ├── utils/             # Utility functions and helpers
│   └── tests/             # Test package
│       ├── unit/          # Unit tests
│       ├── integration/   # Integration tests
│       └── test_app.py    # Main app tests
├── conftest.py            # Global pytest configuration
├── pytest.ini            # Pytest settings
├── pyproject.toml         # Project configuration and dependencies
├── poetry.lock            # Lock file for dependencies
├── CLAUDE.md              # Development guidelines
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.11+
- Poetry

### Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Usage

```bash
# Run the application
poetry run elevator

# Or directly
poetry run python -m app.app
```

## Development

### Testing
```bash
# Run all tests
poetry run python -m pytest

# Run specific test
poetry run python -m pytest app/tests/test_app.py::test_hello_name -v

# Run with coverage
poetry run python -m pytest --cov=app

# Run only unit tests
poetry run python -m pytest -m unit

# Run only integration tests  
poetry run python -m pytest -m integration
```

### Code Quality
```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy app/
```

## Technical Stack

- **Python**: 3.11+
- **Package Management**: Poetry
- **Testing**: pytest with coverage and mocking
- **Code Formatting**: Black
- **Linting**: Ruff
- **Type Checking**: mypy
- **Web Framework**: FastAPI (if needed)
- **Configuration**: python-dotenv for environment variables