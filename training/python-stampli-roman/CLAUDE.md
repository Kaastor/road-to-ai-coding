# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview
Roman Letters Calculator
Background
The Roman numeral system is a numerical notation that was used in ancient
Rome and is still occasionally used today for certain purposes. It uses
combinations of letters from the Latin alphabet to represent numbers.
Acceptance Criteria
Write a calculator that receives a String as input and if that input is in fact a valid
Roman numeral, return is Integer value as output.
If the input is not valid, handle as you please.
Basic symbols and values
- I (1)
- V (5)
- X (10)
- L (50)
- C (100)
- D (500)
- M (1000)
Combining Symbols
1. Symbols are combined to represent numbers. The value of the combined
symbols is determined by summing the values of the individual symbols
2. Symbols are read from left to right, and larger values come before smaller
values.
3. Repeating a numeral up to three times represents addition of the number. For
example, III represents 1 + 1 + 1 = 3.
4. Only I, X, C, and M can be repeated; V, L, and D cannot be, and there is no need to
do so.
Subtraction Rules
To write a number that otherwise would take repeating of a numeral four or more
times, there is a subtraction rule. Writing a smaller numeral to the left of a larger
numeral represents subtraction
For example, IV represents 5 - 1 = 4 and IX represents 10 - 1 = 9.
To avoid ambiguity,
the ONLY pairs of numerals that use this subtraction rule are:
- IV (4, 5 - 1)
- IX (9, 10 - 1)
- XL (40, 50 - 10)
- XC (90, 100 - 10)
- CD (400, 500 - 100)
- CM (900, 1000 - 100)
Note: Subtraction cannot repeat it self, for example, the String XCXC is invalid, the
correct presentation of the number 180 is CLXXX
Examples
Valid Examples
1. III = I(1) + I(1) + I(1) = 3
2. CV = C(100) + V(5) = 105
3. DCXLVIII = D(500) + C(100) + XL(40) + V(5) + I(1) + I(1) + I(1) = 648
4. MMDXLIX = M(1000) + M(1000) + D(500) + XL(40) + IX(9) = 2549
5. MCMXLIV = M(1000) + CM(900) + XL(40) + IV(4) = 1944
6. MCMXCIX = M(1000) + CM(900) + XC(90) + IV(4) = 1999
Invalid Examples
1. IIII: This violates the rule that you can't have more than three identical symbols
in a row. Instead, it should be written as IV (4).
2. VV: V cannot be repeated. The correct way to represent 10 is X.
3. IC: This is invalid because you can't subtract a symbol of smaller value before a
symbol of larger value. To represent 99, you should use XCIX.
4. CDCD: This violates the rule that you can't repeat a subtraction more than once.
The correct way to represent 400 is CD.
5. IL: This is invalid because subtractive notation can only be applied with powers
of ten (e.g., IV, IX, XL, XC, etc.). The correct way to represent 49 is XLIX.
GOOD LUCK!!

## Build & Test Commands

- Run app
`poetry run python -m app.app`

### Using poetry
- Install dependencies: `poetry install`

### Testing
# all tests
`poetry run python -m pytest`

# single test
`poetry run python -m pytest app/tests/test_app.py::test_hello_name -v`

# run Roman calculator tests
`poetry run python -m pytest app/tests/test_roman_calculator.py -v`


## Project Structure

```
.
├── app/
│   ├── app.py                          # Main Roman numeral calculator implementation
│   └── tests/
│       ├── test_app.py                 # Basic app tests
│       ├── test_inmem_cache.py         # In-memory cache tests (legacy)
│       └── test_roman_calculator.py    # Comprehensive Roman calculator tests
├── CLAUDE.md                           # Project documentation and guidelines
├── pyproject.toml                      # Poetry configuration and dependencies
├── poetry.lock                         # Locked dependency versions
└── pytest.ini                         # Pytest configuration
```

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for faster
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout

### Dependencies

**Production Dependencies:**
- fastapi ^0.104.0
- uvicorn ^0.24.0  
- python-dotenv ^1.0.0

**Development Dependencies:**
- pytest ^8.0.0

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

## Implementation Status

### ✅ Phase 1: Core Domain Logic - COMPLETED

Built Roman numeral conversion engine with clear separation of concerns:

1. ✅ **RomanNumeralValueMapping** - Symbol-to-value dictionaries for basic symbols and subtraction pairs
2. ✅ **SubtractionRuleValidator** - Validates IV, IX, XL, XC, CD, CM patterns and prevents invalid combinations
3. ✅ **RepetitionRuleValidator** - Enforces max 3 consecutive symbols and prevents V/L/D repetition
4. ✅ **ConversionAlgorithm** - Transforms valid Roman strings to integers
5. ✅ **InputValidation** - Orchestrates all validation rules with comprehensive character and rule checking
6. ✅ **RomanNumeralCalculator** - Main interface combining validation and conversion

### ✅ Phase 2: Testing Foundation - COMPLETED

Comprehensive test suite with 14 test cases covering:
- ✅ All valid examples: III=3, CV=105, DCXLVIII=648, MMDXLIX=2549, MCMXLIV=1944, MCMXCIX=1999
- ✅ All invalid examples: IIII, VV, IC, CDCD, IL
- ✅ Component-level unit tests for each class
- ✅ Integration tests for the main calculator
- ✅ Edge cases and boundary conditions

### 🔲 Phase 3: User Interface - PENDING

Simple CLI interface with user-friendly error handling:
- Command-line input/output
- Clear error messages for invalid inputs  
- Help text with usage examples

### 🔲 Phase 4: Integration & Validation - PENDING

Final testing and validation against all requirements
