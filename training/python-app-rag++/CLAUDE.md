# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
“RAG++” with Feedback & Live Re-Rank

“Build a retrieval-augmented generation service over 20–50 short docs; capture user feedback and improve ranking online.” (Hits LLMs + microservice + eval/monitoring.)

* Index: chunk 20–50 markdown files → TF-IDF+SVD embeddings → FAISS.
* Query pipeline: hybrid recall (BM25 + vectors) → cross-encoder/LLM re-rank → answer with cited spans.
* Feedback: `POST /feedback` stores 👍/👎 per (query, doc, rank) for online re-weighting.
  **Endpoints**
* `POST /ask {q}` → `{answer, sources[], lat_ms, token_usage}`
* `POST /feedback {q, doc_id, label}` → `{ok:true}`
* `GET /metrics` → `{p50,p95,hit_rate@3,avg_rerank_ms}`
  **Success**
* Cited answers; measurable **hit\_rate\@k**; latency + token counters surfaced. (End-to-end + ops.)
  **Stretch**
* Simple “learning to re-rank” weight tweak from feedback (e.g., doc prior boosts).

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`
- Run development server: `poetry run uvicorn app.app:app --reload`

### Testing
# all tests
`poetry run python -m pytest`

# single test
`poetry run python -m pytest app/tests/test_app.py::test_hello_name -v`

# test embedding pipeline
`poetry run python -m pytest app/tests/test_services/test_tfidf_embedding_service.py -v`

# test document indexing
`poetry run python -m pytest app/tests/test_services/test_document_indexer_lightweight.py -v`

# test vector storage
`poetry run python -m pytest app/tests/test_services/test_vector_storage.py -v`

# test BM25 search
`poetry run python -m pytest app/tests/test_services/test_bm25_search.py -v`

# test hybrid search
`poetry run python -m pytest app/tests/test_services/test_hybrid_search.py -v`

# test hybrid search integration
`poetry run python -m pytest app/tests/test_services/test_document_indexer_hybrid.py -v`

# integration tests
`poetry run python -m pytest app/tests/test_integration.py -v`


## Project Structure

```
training-python-app-rag++/
├── app/
│   ├── __init__.py
│   ├── app.py                      # FastAPI application entry point
│   ├── models/                     # Data models and schemas
│   │   └── __init__.py
│   ├── services/                   # Business logic (embeddings, search, LLM)
│   │   ├── __init__.py
│   │   ├── document_loader.py      # Markdown document loading
│   │   ├── text_chunker.py         # Text chunking with overlap
│   │   ├── tfidf_embedding_service.py    # TF-IDF + SVD embeddings
│   │   ├── mock_embedding_service.py     # Mock embeddings for testing
│   │   ├── adaptive_embedding_service.py # Auto-selecting embedding service
│   │   ├── vector_storage.py       # FAISS vector similarity search
│   │   ├── bm25_search.py          # BM25 keyword search service
│   │   ├── hybrid_search.py        # Hybrid BM25 + vector search with score fusion
│   │   └── document_indexer.py     # Complete indexing pipeline with hybrid search
│   └── tests/
│       ├── test_app.py                        # API endpoint tests
│       ├── test_integration.py                # End-to-end pipeline tests
│       └── test_services/                     # Service layer tests
│           ├── __init__.py
│           ├── test_adaptive_embedding_service.py
│           ├── test_bm25_search.py         # BM25 search functionality tests
│           ├── test_document_indexer_hybrid.py # Hybrid search integration tests
│           ├── test_document_indexer_lightweight.py
│           ├── test_document_loader.py
│           ├── test_hybrid_search.py       # Hybrid search service tests
│           ├── test_mock_embedding_service.py
│           ├── test_text_chunker.py
│           ├── test_tfidf_embedding_service.py
│           └── test_vector_storage.py
├── docs/                           # Sample markdown documents (20-50 files)
│   ├── api_design.md
│   ├── bm25_search.md
│   ├── feedback_systems.md
│   ├── introduction.md
│   └── vector_embeddings.md
├── data/                           # Generated embeddings and indices (gitignored)
│   ├── *.faiss                     # FAISS vector index files
│   └── *.json                      # Index metadata and document storage
├── poetry.lock                     # Poetry lock file
├── pyproject.toml                  # Poetry configuration and dependencies
├── pytest.ini                     # Pytest configuration
└── CLAUDE.md                      # This file
```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster dependency management
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout with FastAPI structure

### Dependencies

#### Production Dependencies
- `fastapi` ^0.104.0 - Web framework for building APIs
- `uvicorn` ^0.24.0 - ASGI server for FastAPI
- `scikit-learn` ^1.3.0 - TF-IDF embeddings and machine learning utilities
- `numpy` ^1.24.0 - Numerical operations for vectors
- `faiss-cpu` ^1.7.4 - Efficient vector similarity search and clustering
- `rank-bm25` ^0.2.2 - BM25 keyword search implementation
- `anthropic` ^0.7.0 - Claude API client for LLM integration
- `python-dotenv` ^1.0.0 - Environment variable management

#### Development Dependencies
- `pytest` ^8.0.0 - Testing framework
- `httpx` - HTTP client for testing FastAPI endpoints

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

## Hybrid Search System

The application now includes a comprehensive hybrid search system that combines keyword-based BM25 search with semantic vector search:

### Search Methods Available
1. **Vector Search** (`search_documents()`): Semantic similarity search using TF-IDF+SVD embeddings
2. **BM25 Search** (`bm25_search_documents()`): Keyword-based search using BM25 relevance scoring
3. **Hybrid Search** (`hybrid_search_documents()`): Combines BM25 and vector search with configurable score fusion

### Hybrid Search Features
- **Score Fusion**: Normalizes BM25 and vector scores to [0,1] range before combining
- **Configurable Weights**: Default 30% BM25, 70% vector search (configurable via `bm25_weight` and `vector_weight`)
- **Document Deduplication**: Handles cases where same document appears in both search results
- **Ranked Results**: Returns documents ranked by combined hybrid relevance scores

### Usage Example
```python
from app.services.document_indexer import DocumentIndexer

indexer = DocumentIndexer()
indexer.index_documents(Path("docs/"))

# Different search methods
vector_results = indexer.search_documents("machine learning", k=5)
bm25_results = indexer.bm25_search_documents("machine learning", k=5)  
hybrid_results = indexer.hybrid_search_documents("machine learning", k=5)
```

## Core Workflow
- Be sure to typecheck when you're done making a series of code changes
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

# Implementation plan

✅ Phase 1: Add minimal dependencies (FastAPI, uvicorn, pytest, scikit-learn)
✅ Phase 2: Document Management - Create sample markdown docs and document loader
✅ Phase 2: Text chunking functionality with overlap
✅ Phase 3: Embedding Pipeline - TF-IDF+SVD embeddings with FAISS vector storage
✅ Phase 3: Document indexing and basic vector similarity search
✅ Phase 4: Hybrid Search - Add BM25 keyword search capability
✅ Phase 4: Combine BM25 + vector search with simple score fusion
☐ Phase 5: Core API - Implement POST /ask endpoint with basic retrieval
☐ Phase 5: Add LLM answer generation with cited spans (Claude API)
☐ Phase 6: Feedback System - Implement POST /feedback endpoint with in-memory storage
☐ Phase 6: Simple feedback-based document score adjustment
☐ Phase 7: Monitoring - Add latency tracking and basic metrics collection
☐ Phase 7: Implement GET /metrics endpoint with p50, p95, hit_rate@3
☐ Phase 8: Testing - Add unit tests for core components
☐ Phase 8: Add integration tests for API endpoints
