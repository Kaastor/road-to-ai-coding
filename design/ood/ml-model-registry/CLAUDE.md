# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
A lightweight ML Model Registry Proof of Concept for managing machine learning models, their metadata, versions, and lifecycle. This REST API service allows data scientists to register, discover, and manage ML models with proper versioning and metadata tracking.

### Core Features:
- Model registration and versioning
- Metadata management and search
- Model artifact storage (local filesystem) with multi-format support
- Model lifecycle management (draft/staging/production/archived)
- Model promotion workflow with validation
- Performance metrics tracking
- REST API with OpenAPI documentation
- Advanced search capabilities (by name, description, and tags)
- Metadata update operations for models and versions
- File upload/download operations for model artifacts
- Audit logging for all model operations
- Comprehensive input validation and error handling
- Clean Architecture implementation with proper separation of concerns

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`

### Testing
# all tests
`poetry run python -m pytest`

# single test
`poetry run python -m pytest app/tests/test_domain_models.py::TestModel::test_create_model -v`

# run file storage tests
`poetry run python -m pytest app/tests/test_file_storage.py -v`

# run model lifecycle tests
`poetry run python -m pytest app/tests/test_model_lifecycle.py -v`

# run artifact operations tests
`poetry run python -m pytest app/tests/test_artifact_operations.py -v`

### Running the Application
# start the development server
`poetry run python -m app.main`

# or using the script entry point
`poetry run ml-registry`

### Type Checking
# run type checker
`poetry run mypy app --ignore-missing-imports`

## Project Structure

```
ml-model-registry/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Configuration management with Pydantic settings
│   ├── app.py                      # Legacy application file
│   ├── api/                        # REST API layer
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── models.py           # Model and version API endpoints with full CRUD operations
│   ├── domain/                     # Domain layer (business logic)
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── model.py            # Core domain models (Model, ModelVersion, ModelMetadata)
│   │   │   ├── schemas.py          # Pydantic schemas for validation/serialization
│   │   │   ├── mappers.py          # Domain to schema mapping functions
│   │   │   └── audit.py            # Audit logging models and functionality
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       └── exceptions.py       # Custom domain exceptions
│   ├── infrastructure/             # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Abstract repository interfaces
│   │   │   └── sqlalchemy_repositories.py  # SQLAlchemy repository implementations
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── database.py         # Database configuration and session management
│   │       ├── models.py           # SQLAlchemy ORM models
│   │       ├── file_storage.py     # File storage abstraction and implementations
│   │       └── storage_factory.py  # Factory for creating storage instances
│   ├── services/                   # Application services layer
│   │   ├── __init__.py
│   │   └── model_service.py        # Model management business logic with search, update, file operations
│   └── tests/                      # Test suite
│       ├── __init__.py
│       ├── test_domain_models.py   # Domain model unit tests
│       ├── test_api.py             # Comprehensive API integration tests
│       ├── test_file_storage.py    # File storage functionality tests
│       ├── test_model_lifecycle.py # Model promotion and lifecycle tests
│       ├── test_artifact_operations.py # Artifact upload/download/delete tests
│       └── test_app.py             # Legacy test file
├── .env.example                    # Environment variables example
├── CLAUDE.md                       # This file - Project documentation and guidelines
├── PLAN.md                         # Project development plan
├── pyproject.toml                  # Poetry project configuration
├── pytest.ini                     # Pytest configuration
└── poetry.lock                     # Locked dependencies
```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout

### Dependencies

#### Core Dependencies
- **fastapi**: Modern, fast web framework for building APIs
- **pydantic**: Data validation and settings management using Python type annotations
- **pydantic-settings**: Settings management for Pydantic v2
- **sqlalchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **python-multipart**: Support for form data and file uploads
- **python-dotenv**: Environment variable management from .env files
- **uvicorn**: ASGI web server implementation for Python

#### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Pytest plugin for testing asyncio code
- **httpx**: HTTP client library for testing API endpoints
- **black**: Code formatter
- **mypy**: Static type checker
- **faker**: Library for generating fake data for testing
- **pytest-mock**: Enhanced mocking capabilities for tests

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

## Object-Oriented Design Guidelines (Python-Focused)

- **SOLID Principles**: Adhere to SOLID for robust, maintainable classes:
  - **Single Responsibility Principle (SRP)**: Each class should have one reason to change; avoid god classes by splitting concerns (e.g., separate data models from business logic).
  - **Open-Closed Principle (OCP)**: Classes should be open for extension but closed for modification; use abstract base classes (ABCs from `abc` module) and inheritance/composition for extensibility.
  - **Liskov Substitution Principle (LSP)**: Subclasses must be substitutable for base classes without altering program correctness; ensure method signatures and behaviors are compatible.
  - **Interface Segregation Principle (ISP)**: Prefer many small, client-specific interfaces over large ones; use Python's `Protocol` from `typing` for structural subtyping (duck typing with type hints).
  - **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions; implement dependency injection via constructors or factories to decouple modules.
- **Inheritance vs. Composition**: Favor composition over inheritance to avoid tight coupling; use mixins for shared behavior only when necessary.
- **Encapsulation and Properties**: Use private attributes (prefixed with `_` or `__`) and `@property` decorators for controlled access, promoting data hiding.
- **Abstract Classes and Interfaces**: Leverage `abc.ABC` and `@abstractmethod` for defining interfaces; combine with type hints for better IDE support and runtime checks.
- **Polymorphism**: Exploit Python's duck typing for flexible designs, but add `Protocol` types for static checking.
- **Class Design Best Practices**:
  - Keep classes small (< 200 lines) and focused; refactor early if a class handles multiple responsibilities.
  - Use `dataclasses` for simple data-holding classes to reduce boilerplate.
  - Avoid over-engineering: Start with functions, promote to classes only when state or polymorphism is needed.
- **Integration with Patterns**: Apply OOD in architectural patterns, e.g., use factories for object creation in MVC, or observers for event handling in ML pipelines.
- **Testing OOD**: Mock dependencies with `unittest.mock` to test classes in isolation; focus tests on public interfaces, not internal state.

### Microservices Design Guidelines (Python-Focused)
- **Service Boundaries**: Define clear boundaries based on domain-driven design; each microservice should own its data and logic (e.g., separate user service from payment service).
- **Communication**: Use synchronous HTTP/REST for simple interactions (via requests or httpx libraries) and asynchronous messaging (e.g., RabbitMQ with pika or Celery) for decoupled events.
- **Resilience Patterns**: Implement circuit breakers (e.g., with pybreaker), retries (e.g., with tenacity), and timeouts to handle failures gracefully.
- **Service Discovery & Configuration**: Use environment variables for config; for discovery in containerized setups, integrate with Consul or etcd via Python clients.
- **Containerization**: Package services with Docker; use multi-stage builds for efficiency and include health checks (e.g., via FastAPI's `/health` endpoint).
- **Orchestration**: Design for Kubernetes deployment; use Python tools like kubernetes client for dynamic scaling if needed.
- **Testing in Microservices**: Write contract tests for APIs (e.g., with pact-python); use integration tests with testcontainers-python for spinning up dependent services like databases.

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
- **Separation of Concerns**: Ensure each module/class has a single responsibility; refactor early to avoid god classes.
- **Scalability Planning**: Evaluate designs for growth—e.g., database sharding, microservices decomposition.
- **Prototyping**: For complex designs, create quick prototypes or UML diagrams before full implementation.

## Architectural Patterns

- **Modular Architecture**: Design applications as loosely coupled modules (e.g., separate concerns like data access, business logic, and UI/API layers). Use dependency injection to promote testability and flexibility.
- **Design Patterns**: Apply common patterns where appropriate:
  - **MVC (Model-View-Controller)**: For web or API-driven apps to separate data, presentation, and logic.
  - **Singleton/Factory**: For managing shared resources like database connections or ML model instances.
  - **Observer/Command**: For event-driven systems, such as real-time ML inference updates.
- **Layered Design**: Structure code in layers (e.g., presentation, application, domain, infrastructure) to enable easy scaling and maintenance.
- **API-First Design**: For services, design APIs before implementation; use tools like OpenAPI/Swagger for documentation.

## Scalability and Performance Guidelines

- **Horizontal Scaling**: Design for stateless components where possible; use load balancers and containerization (e.g., Docker) for deployment.
- **Caching Strategies**: Implement caching (e.g., with Redis) for frequent reads in performance-critical paths, like ML model predictions.
- **Asynchronous Processing**: Use async/await or queues (e.g., Celery with RabbitMQ) for I/O-bound tasks to handle high throughput.
- **Monitoring and Observability**: Integrate tools like Prometheus/Grafana for metrics, and structured logging for tracing.
- **ML-Specific Scalability**: For ML apps, design pipelines with MLOps in mind—use tools like MLflow for model registry, Kubeflow for orchestration, and ensure data pipelines handle large volumes with tools like Dask or Spark.

## ML-Specific Design Guidelines (Optional, if repo involves AI/ML)

- **Pipeline Design**: Build end-to-end ML workflows (data ingestion → preprocessing → training → deployment) using libraries like scikit-learn, PyTorch, or Hugging Face.
- **Model Management**: Version models and data; implement drift detection and automated retraining triggers.
- **Ethical Considerations**: Include bias checks, explainability (e.g., SHAP), and privacy (e.g., federated learning) in designs.
- **Integration Patterns**: Use RAG (Retrieval-Augmented Generation) for LLM apps; design for low-latency inference with tools like FastAPI or gRPC.

## Core Workflow
- Be sure to typecheck when you're done making a series of code changes: `poetry run mypy app --ignore-missing-imports`
- Prefer running single tests, and not the whole test suite, for performance
- Review designs against scalability and modularity guidelines before committing.

## API Documentation

The application provides a RESTful API for model registry operations:

### Health Check
- `GET /health` - Check service health

### Models
- `POST /api/v1/models/` - Create a new model
- `GET /api/v1/models/` - List all models (with pagination, search, and tag filtering)
- `GET /api/v1/models/{model_id}` - Get a specific model
- `PATCH /api/v1/models/{model_id}` - Update model basic information (name, description)
- `DELETE /api/v1/models/{model_id}` - Delete a model

### Model Versions
- `POST /api/v1/models/{model_id}/versions` - Create a new version for a model
- `GET /api/v1/models/{model_id}/versions` - List all versions for a model
- `GET /api/v1/models/{model_id}/versions/{version}` - Get a specific version
- `PATCH /api/v1/models/{model_id}/versions/{version}/status` - Update version status
- `PATCH /api/v1/models/{model_id}/versions/{version}/metadata` - Update version metadata
- `GET /api/v1/models/{model_id}/versions/latest` - Get the latest version

### Model Artifacts
- `POST /api/v1/models/{model_id}/versions/{version}/artifact` - Upload artifact file for a model version
- `GET /api/v1/models/{model_id}/versions/{version}/artifact` - Download artifact file for a model version
- `DELETE /api/v1/models/{model_id}/versions/{version}/artifact` - Delete artifact file for a model version

### Model Lifecycle
- `POST /api/v1/models/{model_id}/versions/{version}/promote` - Promote model version to higher status

### Search and Filtering
The models listing endpoint (`GET /api/v1/models/`) supports the following query parameters:
- `skip` - Number of records to skip for pagination (default: 0)
- `limit` - Maximum number of records to return (default: 100, max: 1000)
- `search` - Search models by name or description
- `tags` - Comma-separated list of tags to filter models by

### Model Status Lifecycle
- **draft** - Initial development status
- **staging** - Version ready for testing
- **production** - Version deployed to production
- **archived** - Deprecated version

### Supported Model Formats
- **pickle** - Python pickle format
- **joblib** - Joblib serialization format
- **onnx** - ONNX (Open Neural Network Exchange) format
- **h5** - HDF5 format (commonly used with Keras/TensorFlow)
- **pt** - PyTorch model format
- **pb** - TensorFlow protobuf format

### Model Promotion Rules
- **draft → staging**: Standard promotion path for models ready for testing
- **staging → production**: Models that have passed testing and validation
- **production → archived**: Retire models from active production use
- Only one version per model can be in **production** status at a time

## Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_URL` - SQLite database path (default: `sqlite:///./models.db`)
- `API_HOST` - Server host (default: `127.0.0.1`)
- `API_PORT` - Server port (default: `8000`)
- `DEBUG` - Enable debug mode (default: `false`)
- `ARTIFACT_STORAGE_PATH` - Directory for storing model artifacts (default: `./artifacts`)
- `MAX_ARTIFACT_SIZE_MB` - Maximum artifact file size in MB (default: `100`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

## Architecture Notes

The application follows **Clean Architecture** principles with clear separation of concerns:

1. **Domain Layer**: Contains business logic and domain models
2. **Application Layer**: Contains services that orchestrate domain operations
3. **Infrastructure Layer**: Contains database and external service integrations
4. **API Layer**: Contains REST API endpoints and request/response handling

Key patterns implemented:
- **Repository Pattern**: Abstract data access behind interfaces
- **Dependency Injection**: Services depend on abstractions, not concrete implementations
- **Domain-Driven Design**: Rich domain models with business logic encapsulation
- **Factory Pattern**: Storage factory for creating file storage instances
- **Strategy Pattern**: File storage abstraction allows different storage implementations
- **Audit Logging Pattern**: Comprehensive logging of all domain operations
- **State Machine Pattern**: Model lifecycle with controlled status transitions
