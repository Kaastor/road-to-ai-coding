# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Project description: https://raw.githubusercontent.com/florinpop17/app-ideas/refs/heads/master/Projects/3-Advanced/Elevator-App.md (do not use this, it's just doc for developer)

## Project Overview
# Codename Goose — Project Description

Codename **Goose** is a local-first Retrieval-Augmented Generation (RAG) service focused on answering questions from user-provided PDFs. You (the user) provide PDFs. **Goose** wires up a FastAPI application that:

* Ingests PDFs via a **PDF Reader MCP** (Model Context Protocol) server.
* Stores chunked text and vector embeddings in **PostgreSQL** (with `pgvector`) via a **PostgreSQL MCP** server.
* Runs a **local CPU-friendly embeddings model** (no external calls) and a simple hybrid retriever (vector + BM25).
* Exposes clean HTTP APIs for ingestion, search, and QA with source citations.
* Ships with a **Makefile** and **pytest**-based test suite, including **smoke tests** and **latency checks** that your app can run.

Goose’s job is to wire and scaffold; your app’s job is to serve, test itself, and stay fast and observable—entirely on your machine.

---

# Project Requirements

## Functional Requirements

1. **PDF Ingestion**

   * Accept one or many PDFs by file path or directory.
   * Use **PDF Reader MCP** to extract text + metadata (title, author if present, page numbers).
   * Chunk strategy: recursive, \~800–1,000 tokens per chunk with 10–15% overlap; store page and chunk indices.
   * Deduplicate by file hash; re-ingest updates on content hash change.

2. **Embeddings & Storage**

   * Generate local embeddings for each chunk.
   * Store in PostgreSQL with `pgvector` (schema includes: `documents`, `chunks`, `embeddings`, `ingestion_jobs`).
   * Index: `ivfflat` or `hnsw` (if available) on the vector column; additional trigram index for BM25/FULLTEXT.

3. **Retrieval & QA**

   * Endpoints:

     * `POST /ingest` — trigger ingestion from paths/URLs/configured MCP source(s).
     * `POST /query` — input natural language query, return ranked chunks with highlights and **source citations**.
     * `GET /healthz` — liveness & readiness checks (DB, embeddings model warm status).
     * `GET /metrics` — Prometheus-compatible metrics.
     * `GET /docs` — OpenAPI/Swagger UI.
   * Retrieval:

     * Top-k vector search + optional BM25 rerank; configurable `k` (default 8).
     * Optional filters: document id, filename, tag, time range.
     * Return fields: answer (if generator configured), or top contexts + scores + citations.

4. **Testing & Self-Checks**

   * **Smoke tests**: health, DB connectivity, basic ingest of a tiny PDF, and query returning ≥1 result.
   * **Relevance sanity test**: canned Q→A asserts that a top-3 chunk contains a known answer substring.

5. **Operations**

   * **Makefile** targets for: `setup`, `dev`, `run`, `ingest`, `test`, `smoke`, `latency`, `lint`, `typecheck`, `format`, `migrate`, `seed`, `clean`.
   * Config via env vars (12-factor): DB URL, embedding model name, chunk sizes, retriever `k`, log level.
   * Structured logging (JSON) + request IDs; Prometheus metrics; optional OpenTelemetry traces.

6. **Security & Privacy**

   * Entirely local by default (no outbound network for embeddings/RAG).
   * Role: “operator” can purge docs and reindex; soft delete with tombstones.


---

# Project Dev Dependencies (Python)

> These are **dev/test/tooling** dependencies (not runtime libs like FastAPI, pgvector, etc.).

* **Testing**

  * `pytest`
  * `pytest-asyncio`
  * `pytest-cov`
  * `hypothesis` (property-based tests for chunker & ranker)
  * `freezegun` (time control)
  * `faker` (synthetic text/doc metadata)
  * `respx` (mock HTTP if needed)
  * `httpx` (test client)

* **Quality & Types**

  * `ruff` (lint + import sort)
  * `black`
  * `mypy`
  * `types-requests` and `types-python-dateutil` (stub packages as needed)

* **Benchmarks & Profiling**

  * `pytest-benchmark`
  * `anyio` (timers for async latency harness)
  * `rich` (pretty CLI output for latency report)

* **Automation**

  * `pre-commit`
  * `tox` or `nox` (choose one for matrix testing)

> Optional dev helpers: `ipython`, `jupyter`, `line-profiler`, `memory-profiler`.

# Project Runtime Dependencies (Python)

## Web API
fastapi
uvicorn[standard]

## DB & migrations
sqlalchemy>=2
psycopg[binary]>=3
alembic
pgvector

## Retrieval / NLP (local-first)
sentence-transformers         # default local embedding model (e.g., all-MiniLM-L6-v2)
torch                         # CPU-only install is fine for local
rank-bm25                     # BM25 / hybrid retrieval
tokenizers                    # fast token counts for chunking
tiktoken                      # optional: OpenAI-like tokenizer for stable token-based chunk sizes

## MCP clients (to talk to PDF Reader MCP + PostgreSQL MCP)
## Use the official MCP Python client if you have it; otherwise fall back to JSON-RPC over stdio/websockets.
mcp                           # optional: official MCP Python SDK (if available in your env)
websockets                    # transport when MCP is exposed via ws
anyio                         # structured async for adapters


## Logging & config
structlog
python-json-logger
pydantic-settings
python-dotenv
orjson                       # fast JSON responses from FastAPI

## CLI / utilities
typer
tenacity                     # retries for MCP calls / DB reconnects

---

# User Stories

## Ingestion & Storage

1. **As an operator,** I can run `make ingest PATH=./docs` to import PDFs so that content is searchable.
   **Acceptance:** `documents` and `chunks` rows are created; `/query` returns contexts from those files.

2. **As an operator,** I can ingest the same PDF twice without duplicates.
   **Acceptance:** Second run updates `updated_at` only when content hash changes; chunk count stays unchanged otherwise.

3. **As an operator,** I can purge a document by id.
   **Acceptance:** Soft delete flags the doc and excludes its chunks from results; a re-ingest restores it.

4. **As an operator,** I can see ingestion progress.
   **Acceptance:** `/metrics` exposes `goose_ingest_duration_seconds` and `goose_chunks_total` counters.

## Retrieval & Query

5. **As a user,** I can `POST /query` with a natural language question and get relevant passages with citations.
   **Acceptance:** Response includes top-k contexts with filename, page range, and scores; JSON schema validated.

6. **As a user,** I can filter results to a specific document or tag.
   **Acceptance:** Passing `document_id` or `tag` restricts candidates before ranking.

7. **As a user,** I can adjust `k` and see different recall/latency tradeoffs.
   **Acceptance:** Latency and recall metrics reflect the new `k`.

8. **As a user,** I can request BM25 hybrid retrieval.
   **Acceptance:** A `retriever="hybrid"` flag changes the scorer; top-k now merges vector + BM25 with weights.


## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`

### Testing
```bash
# all tests
poetry run python -m pytest

# single test
poetry run python -m pytest app/tests/test_app.py::test_hello_name -v

# with coverage
poetry run python -m pytest --cov=app

# unit tests only
poetry run python -m pytest -m unit

# integration tests only
poetry run python -m pytest -m integration
```

### Code Quality
```bash
# format code
poetry run black .

# lint code
poetry run ruff check .

# fix linting issues
poetry run ruff check . --fix

# type checking
poetry run mypy app/
```


## Project Structure

```
training-app-mpc/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Main application module
│   ├── config/            # Configuration management
│   │   └── __init__.py
│   ├── core/              # Core business logic
│   │   └── __init__.py
│   ├── utils/             # Utility functions and helpers
│   │   └── __init__.py
│   └── tests/             # Test package
│       ├── __init__.py
│       ├── unit/          # Unit tests
│       │   └── __init__.py
│       ├── integration/   # Integration tests
│       │   └── __init__.py
│       └── test_app.py    # Main app tests
├── conftest.py            # Global pytest configuration
├── pytest.ini            # Pytest settings
├── pyproject.toml         # Project configuration and dependencies
├── poetry.lock            # Lock file for dependencies
├── CLAUDE.md              # Development guidelines
└── README.md              # Project documentation
```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout

### Dependencies

**Production:**
- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server for FastAPI
- `python-dotenv` - Environment variable management

**Development:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting for tests
- `pytest-mock` - Mocking support for pytest
- `black` - Code formatter
- `ruff` - Fast Python linter
- `mypy` - Static type checker

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
