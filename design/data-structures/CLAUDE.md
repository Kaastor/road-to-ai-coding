# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
[Description]

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

[List of deps]

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

## Implementation Priority
0. High-level design sketch (e.g., architecture diagram or pseudocode) before coding.
1. Core functionality first (render, state)
2. User interactions
  - Implement only minimal working functionality
3. Minimal unit tests

### Iteration Target
- Around 5 min per cycle
- Keep tests simple, just core functionality checks
- Prioritize working code over perfection for POCs
