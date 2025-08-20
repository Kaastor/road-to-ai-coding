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


# Implementation plan

Phase 1: Foundation (Week 1)

  1. Database Setup
    - PostgreSQL with pgvector
    - Basic schema: documents, chunks, embeddings tables
    - SQLAlchemy models and Alembic migrations
  2. Core FastAPI Structure
    - Basic app with health endpoint
    - Configuration management (pydantic-settings)
    - Structured logging setup

  Phase 2: PDF Processing (Week 2)

  3. PDF Ingestion Pipeline
    - File hash-based deduplication
    - Text extraction (without MCP first - use pypdf2/pymupdf)
    - Basic chunking strategy (recursive, ~800-1000 tokens)
  4. Storage Layer
    - Document and chunk persistence
    - Basic CRUD operations

  Phase 3: Embeddings & Search (Week 3)

  5. Embeddings Generation
    - Local sentence-transformers model
    - Batch processing for chunks
    - Vector storage in pgvector
  6. Basic Retrieval
    - Vector similarity search
    - Simple ranking and scoring

  Phase 4: API & Integration (Week 4)

  7. REST Endpoints
    - POST /ingest
    - POST /query
    - GET /healthz, /metrics, /docs
  8. BM25 Hybrid Search
    - Combine vector + BM25 scoring
    - Configurable retrieval parameters

  Phase 5: Operations & Testing (Week 5)

  9. Testing Suite
    - Unit tests for core functions
    - Integration tests for endpoints
    - Smoke tests for full pipeline
  10. Operations
    - Makefile targets
    - Prometheus metrics
    - Docker setup