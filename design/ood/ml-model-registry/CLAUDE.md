# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
A lightweight ML Model Registry Proof of Concept for managing machine learning models, their metadata, versions, and lifecycle. This REST API service allows data scientists to register, discover, and manage ML models with proper versioning and metadata tracking.

### Core Features:
- Model registration and versioning
- Metadata management and search
- Model artifact storage (local filesystem)
- Model lifecycle management (draft/staging/production)
- Performance metrics tracking
- REST API with OpenAPI documentation

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
- **sqlalchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **python-multipart**: Support for form data and file uploads
- **python-dotenv**: Environment variable management from .env files
- **uvicorn**: ASGI web server implementation for Python

#### ML & Data Dependencies
- **scikit-learn**: Machine learning library for sample models and metrics
- **joblib**: Efficient serialization of Python objects (for model persistence)
- **pandas**: Data manipulation and analysis library
- **numpy**: Numerical computing library

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
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- Review designs against scalability and modularity guidelines before committing.
