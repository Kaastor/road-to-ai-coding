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

## Quick Start Tutorial

### 1. Setup & First Run

**Step 1: Install dependencies**
```bash
poetry install
```

**Step 2: Configure API key**
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key:
ANTHROPIC_API_KEY=your_actual_claude_api_key_here
```

**Step 3: Start the server**
```bash
poetry run uvicorn app.app:app --reload
```

The server will automatically:
- Load 5 sample documents from `docs/` folder
- Create text chunks and build search indices
- Initialize hybrid BM25+vector search
- Start at `http://localhost:8000`

### 2. Try the API

**Ask a question:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is BM25?", "max_sources": 3}'
```

**Submit feedback to improve results:**
```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is BM25?", "doc_id": "docs/bm25_search.md", "label": "positive"}'
```

**Check performance metrics:**
```bash
curl http://localhost:8000/metrics
```

### 3. Web Interface

Visit `http://localhost:8000/docs` for interactive Swagger UI to test all endpoints.

### 4. See Learning in Action

1. Ask: "How does search work?"
2. Submit positive feedback on relevant results
3. Submit negative feedback on irrelevant results  
4. Ask similar questions and see improved rankings
5. Check `/feedback/stats` to monitor learning progress

The system learns from your feedback and immediately improves future search results!

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`
- Run development server: `poetry run uvicorn app.app:app --reload`

### Testing
# all tests
`poetry run python -m pytest`

# all service layer tests (120 tests - recommended)
`poetry run python -m pytest app/tests/test_services/ -v`

# test LLM service (new)
`poetry run python -m pytest app/tests/test_services/test_llm_service.py -v`

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

# test feedback scoring (new)
`poetry run python -m pytest app/tests/test_services/test_feedback_scorer.py -v`

# integration tests
`poetry run python -m pytest app/tests/test_integration.py -v`

### API Testing
# Note: FastAPI endpoint tests have compatibility issues with current httpx version
# Use manual testing with:
# 1. Start server: `poetry run uvicorn app.app:app --reload`
# 2. Test with curl, Postman, or browser at http://localhost:8000/docs


## Project Structure

```
training-python-app-rag++/
├── app/
│   ├── __init__.py
│   ├── app.py                      # FastAPI application entry point with API endpoints
│   ├── models/                     # Data models and schemas
│   │   ├── __init__.py
│   │   └── api.py                  # Pydantic models for API requests/responses
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
│   │   ├── document_indexer.py     # Complete indexing pipeline with hybrid search
│   │   ├── llm_service.py          # Claude API integration for answer generation
│   │   └── feedback_scorer.py      # Feedback-based document scoring and live re-ranking
│   └── tests/
│       ├── test_app.py                        # API endpoint tests (compatibility issues)
│       ├── test_integration.py                # End-to-end pipeline tests
│       └── test_services/                     # Service layer tests (120 tests)
│           ├── __init__.py
│           ├── test_adaptive_embedding_service.py
│           ├── test_bm25_search.py         # BM25 search functionality tests
│           ├── test_document_indexer_hybrid.py # Hybrid search integration tests
│           ├── test_document_indexer_lightweight.py
│           ├── test_document_loader.py
│           ├── test_hybrid_search.py       # Hybrid search service tests
│           ├── test_llm_service.py         # LLM service tests (new)
│           ├── test_feedback_scorer.py     # Feedback scoring tests (new)
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
├── .env.example                    # Environment variables template
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
- `pydantic` ^2.0.0 - Data validation and serialization

#### Development Dependencies
- `pytest` ^8.0.0 - Testing framework
- `httpx` ^0.25.0 - HTTP client for testing FastAPI endpoints (version compatibility issues noted)

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

## Feedback-Based Live Re-Ranking

The application now includes a sophisticated feedback learning system that improves search relevance over time:

### Feedback Scoring Features
- **Real-time Learning**: Document scores are adjusted immediately when feedback is submitted
- **Global Document Scoring**: Documents accumulate reputation across all queries
- **Query-Specific Learning**: Documents can have different scores for different query types
- **Configurable Parameters**: Positive boost (default 20%) and negative penalty (default 10%) are tunable
- **Score Bounds**: Feedback adjustments are bounded to prevent extreme score distortions (0.1x to 2.0x)

### How It Works
1. **Initial Search**: Hybrid search retrieves 2x the requested documents for better re-ranking pool
2. **Feedback Application**: FeedbackScorer calculates boost/penalty multipliers for each document
3. **Score Adjustment**: Original search scores are multiplied by feedback-based multipliers
4. **Re-ranking**: Results are re-sorted by adjusted scores before returning top-k to user
5. **Continuous Learning**: Each feedback submission immediately updates future rankings

### Usage Example
```python
from app.services.feedback_scorer import FeedbackScorer

# Initialize scorer
scorer = FeedbackScorer(positive_boost=0.2, negative_penalty=0.1)

# Record feedback
scorer.add_feedback("machine learning", "docs/intro.md:0", "positive")
scorer.add_feedback("machine learning", "docs/complex.md:1", "negative")

# Apply to search results
adjusted_results = scorer.adjust_search_results(
    results=search_results,
    query="machine learning",
    score_key="hybrid_score"
)
```

## RAG++ API Endpoints

The FastAPI application provides a complete RAG service with the following endpoints:

### Core API Endpoints

#### POST /ask
Answers questions using hybrid search and LLM generation.

**Request:**
```json
{
  "q": "What is machine learning?",
  "max_sources": 5
}
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of AI [SOURCE_1]...",
  "sources": [
    {
      "source_file": "docs/introduction.md",
      "title": "Introduction to AI",
      "chunk_text": "Machine learning is...",
      "chunk_index": 0,
      "relevance_score": 0.85,
      "cited_spans": ["subset of AI", "algorithms"]
    }
  ],
  "lat_ms": 1250,
  "token_usage": {
    "input_tokens": 150,
    "output_tokens": 75,
    "total_tokens": 225
  },
  "query": "What is machine learning?"
}
```

#### POST /feedback
Submits user feedback for query-document pairs.

**Request:**
```json
{
  "q": "What is machine learning?",
  "doc_id": "docs/introduction.md",
  "label": "positive"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Feedback 'positive' recorded successfully"
}
```

#### GET /metrics
Returns service performance metrics.

**Response:**
```json
{
  "p50": 1200.0,
  "p95": 2500.0,
  "hit_rate_at_3": 0.85,
  "avg_rerank_ms": 120.0,
  "total_queries": 42,
  "total_feedback": 15
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "indexer": true,
    "llm": true,
    "feedback_scorer": true
  }
}
```

#### GET /feedback/stats
Returns detailed feedback statistics for monitoring learning progress.

**Response:**
```json
{
  "total_feedback_entries": 25,
  "total_positive": 18,
  "total_negative": 7,
  "unique_documents_with_feedback": 8,
  "unique_query_document_pairs": 15,
  "top_documents": [["docs/introduction.md:0", 0.75, 4]],
  "bottom_documents": [["docs/complex.md:2", -0.33, 3]],
  "positive_boost_factor": 0.2,
  "negative_penalty_factor": 0.1
}
```

### Environment Configuration

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Your Claude API key from Anthropic
- `CLAUDE_MODEL` - Optional, defaults to "claude-3-haiku-20240307"
- `LOG_LEVEL` - Optional, defaults to "INFO"

### Usage Example
```bash
# Start the server
poetry run uvicorn app.app:app --reload

# Test with curl
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is machine learning?", "max_sources": 3}'

# Submit feedback
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is machine learning?", "doc_id": "docs/introduction.md", "label": "positive"}'

# Check metrics
curl http://localhost:8000/metrics

# Check feedback statistics
curl http://localhost:8000/feedback/stats
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
✅ Phase 5: Core API - Implement POST /ask endpoint with hybrid retrieval integration
✅ Phase 5: Add LLM answer generation with cited spans using Claude API
✅ Phase 5: Implement POST /feedback endpoint with in-memory storage
✅ Phase 5: Add latency tracking and basic metrics collection
✅ Phase 5: Implement GET /metrics endpoint with p50, p95, hit_rate@3, and GET /health
✅ Phase 5: Add comprehensive unit tests for LLM service (11 tests)
✅ Phase 5: Environment configuration with .env.example for Claude API
✅ Phase 6: Simple feedback-based document score adjustment and live re-ranking
☐ Phase 7: Advanced monitoring with structured logging and observability
☐ Phase 8: Production deployment configuration and Docker support
☐ Phase 8: Fix FastAPI endpoint testing compatibility issues

## Current Status

**✅ PHASE 6 COMPLETE** - The RAG++ service now includes live learning capabilities with:
- Complete POST /ask pipeline with hybrid search → feedback-based re-ranking → LLM answer generation → cited responses
- Advanced feedback collection system via POST /feedback with live score adjustment
- Performance monitoring via GET /metrics
- Detailed feedback analytics via GET /feedback/stats
- Health checks via GET /health with feedback scorer status
- Token usage tracking and latency measurement
- 120 passing service layer tests (103 original + 17 feedback scorer tests)
- Environment-based configuration for Claude API
- **Live re-ranking based on user feedback** - documents are dynamically boosted/penalized based on positive/negative feedback

**Next: Phase 7** - Advanced monitoring with structured logging and observability.
