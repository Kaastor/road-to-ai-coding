# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quantum Neural Networks Spectral Invariance Research Implementation**

This project implements the theoretical findings from the research paper "Spectral invariance and maximality properties of the frequency spectrum of quantum neural networks". It provides a complete proof-of-concept implementation demonstrating:

- Spectral invariance under area-preserving transformations (Theorem 9)
- Maximality conditions for QNN frequency spectra (Theorems 12-13)  
- 2D sub-generator analysis using Pauli matrices
- Arbitrary dimensional generators with Golomb ruler optimization
- Comprehensive visualization and validation suite

**Status: Complete and validated against research paper (39/39 tests passing)**

## Build & Test Commands

### Using poetry
- Install dependencies: `poetry install`
- Update dependencies: `poetry lock --no-update && poetry install`

### Testing
```bash
# Run all tests (all 39 tests now working!)
poetry run python -m pytest tests/ -v

# Run paper compliance validation
poetry run python -m pytest tests/test_paper_compliance.py -v

# Run specific test modules
poetry run python -m pytest tests/test_frequency_analyzer.py -v
poetry run python -m pytest tests/test_maximality.py -v
poetry run python -m pytest tests/test_golomb_generators.py -v
```

### Demo Scripts
```bash
# Run maximality analysis demo
poetry run python demo_maximality.py

# Run Golomb generators demo  
poetry run python demo_golomb.py

# Run comprehensive validation with visualizations
poetry run python demo_validation.py

# Run paper compliance validation
poetry run python validation_against_paper.py
```

## Project Structure

```
spectral_qnn/                    # Main package
├── core/                        # Core mathematical framework
│   ├── frequency_analyzer.py    # Frequency spectrum analysis & Minkowski sums
│   ├── generators.py           # Hamiltonian generators & encoding strategies
│   ├── simple_qnn.py          # Simplified QNN implementation
│   └── qnn_pennylane.py       # Full PennyLane QNN implementation (working!)
├── maximality/                 # Maximality analysis modules
│   ├── two_dim_analysis.py     # 2D sub-generator maximality (Theorems 12-13)
│   └── golomb_generators.py    # Arbitrary dimensional generators with Golomb rulers
└── validation/                 # Validation and visualization
    └── visualization.py        # Comprehensive validation suite with plots

tests/                          # Test suite (39 tests, 100% passing)
├── test_frequency_analyzer.py  # Core frequency analysis tests
├── test_generators.py         # Hamiltonian generator tests  
├── test_simple_qnn.py         # QNN implementation tests
├── test_maximality.py         # Maximality analysis tests
├── test_golomb_generators.py  # Golomb generator tests
├── test_visualization.py      # Validation suite tests
└── test_paper_compliance.py   # Paper specification compliance tests

papers/                         # Research paper
└── Spectral invariance and maximality properties...pdf

demo_*.py                      # Demonstration scripts
validation_against_paper.py   # Comprehensive paper validation
```

## Technical Stack

- **Python version**: Python 3.11+
- **Project config**: `pyproject.toml` for configuration and dependency management
- **Environment**: Use virtual environment in `.venv` for dependency isolation
- **Package management**: Use `poetry install` for dependency management
- **Dependencies**: Production and dev dependencies in `pyproject.toml`
- **Project layout**: Standard Python package layout

### Dependencies

**Core Dependencies:**
- `pennylane ^0.35.0` - Quantum computing framework
- `numpy ^2.0.0` - Numerical computations
- `scipy ^1.13.0` - Scientific computing (eigenvalue calculations)
- `matplotlib ^3.7.0` - Visualization and plotting

**Development Dependencies:**
- `pytest ^8.0.0` - Testing framework
- `jupyter ^1.0.0` - Notebook support
- `black ^23.0.0` - Code formatting

## Implementation Details

### Core Features Implemented:

1. **Frequency Spectrum Analysis** (`spectral_qnn/core/frequency_analyzer.py`)
   - Eigenvalue difference computation (Definition 3)
   - Minkowski sum operations for spectrum calculation
   - Area-preserving transformation validation
   - Maximality analysis utilities

2. **Hamiltonian Generators** (`spectral_qnn/core/generators.py`)
   - Pauli matrices (2D sub-generators)  
   - Multiple encoding strategies:
     - Hamming encoding (identical generators)
     - Sequential exponential encoding
     - Ternary encoding  
     - Equal layers maximal encoding
   - Generator spectrum analysis

3. **QNN Implementation** (`spectral_qnn/core/simple_qnn.py`)
   - Simplified QNN focusing on frequency spectrum properties
   - Area-preserving transformation validation
   - Spectral invariance demonstration

4. **Maximality Analysis** (`spectral_qnn/maximality/`)
   - 2D sub-generator maximality conditions (Theorems 12-13)
   - Equal data encoding layers analysis
   - Arbitrary encoding optimization
   - Comprehensive configuration testing

5. **Golomb Generators** (`spectral_qnn/maximality/golomb_generators.py`)
   - Golomb ruler construction for optimal frequency separation
   - Arbitrary dimensional Hermitian generators
   - Performance comparison with standard approaches
   - Optimal configuration search

6. **Validation Suite** (`spectral_qnn/validation/visualization.py`)
   - Comprehensive validation against research paper
   - Visualization plots for all major results
   - Area invariance demonstration
   - Maximality analysis visualization
   - Performance comparison charts

### Key Mathematical Results Implemented:

- **Theorem 9**: Area-preserving spectral invariance (A = R × L)
- **Theorem 12**: Equal layers maximality |Ω| = (2L + 1)^R - 1
- **Theorem 13**: Arbitrary encoding optimization
- **Definition 3**: Frequency spectrum Ω = ⊕_{r,l} Ω_{r,l}
- **Equation 4**: Minkowski sum operations

### Validation Status:

✅ **Paper Compliance**: 6/6 core requirements validated
✅ **Test Coverage**: 39/39 tests passing (100% success rate)
✅ **Mathematical Accuracy**: All formulas match paper specifications
✅ **Area Invariance**: 100% success rate on validation tests
✅ **Maximality Conditions**: Theoretical formulas correctly implemented

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

- Use poetry for testing and installing dependencies