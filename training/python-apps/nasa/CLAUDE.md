# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Since 1992 over 4,000 exoplanets have been discovered outside our solar
system. The United States National Aeronautics and Space Administration (NASA)
maintains a publicly accessible archive of the data collected on these in
comma separated value (CSV) format.

The objective of the NASA Exoplanet Query app is to make this data available 
for simple queries by its users. 

### Requirements & Constraints

- The Developer should implement a means of efficiently loading the exoplanet
CSV data obtained from NASA to minimize any delays when the application starts.
- Similarly, the Developer should utilize a data structure and search mechanism
that minimizes the time required to query the exoplanet data and display the
results.
- The Developer will need to review the Exoplanet Archive documentation to
understand the format of the data fields.

### User Stories

- User can see an query input panel containing dropdowns allowing the
user to query on year of discovery, discovery method, host name, and discovery
facility.
- User can also see 'Clear' and 'Search' buttons in the query input panel.
- User can select a single value from any one or all of the query
dropdowns.
- User can click the 'Search' button to search for exoplanets matching
all of the selected query values.
- User can see an error message if the 'Search' button was clicked, but
no query values were selected.
- User can see the matching exoplanet data displayed in tabular format 
in an results panel below the query panel. Only the queriable fields should
be displayed.
- User can click the 'Clear' button to reset the query selections and
clear any data displayed in the results panel, if a search had been performed.

## Build & Test Commands

### Using uv (recommended)
- Install dependencies: `uv pip install --system -e .`
- Install dev dependencies: `uv pip install --system -e ".[dev]"`
- Update lock file: `uv pip compile --system pyproject.toml -o uv.lock`
- Install from lock file: `uv pip sync --system uv.lock`

### Testing
- Run tests: `pytest`
- Run single test: `pytest tests/path/to/test_file.py::test_function_name -v`

## Technical Stack

- **Python version**: Python 3.11
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `uv` for faster, more reliable dependency management with lock file
- **Dependencies**: Separate production and dev dependencies in `pyproject.toml`
- **Version management**: Use `setuptools_scm` for automatic versioning from Git tags
- **Linting**: `ruff` for style and error checking
- **Type checking**: Use VS Code with Pylance for static type checking
- **Project layout**: Organize code with `src/` layout

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
- **Dependency management**: Add libraries only when essential
  - When adding/updating dependencies, update `pyproject.toml` first
  - Regenerate the lock file with `uv pip compile --system pyproject.toml -o uv.lock`
  - Install the new dependencies with `uv pip sync --system uv.lock`

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
