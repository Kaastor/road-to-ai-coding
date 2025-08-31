# ML Model Registry Demo Scripts

This directory contains comprehensive demo scripts that showcase all the features of the ML Model Registry application. These scripts are designed to test main use cases and provide clear verification steps for functionality.

## Overview

The demo scripts simulate real-world MLOps scenarios and demonstrate the complete lifecycle of machine learning model management, from experimentation to production deployment.

## Available Demos

### 1. Basic Model Registration (`01_basic_model_registration.py`)
**Use Case**: Data scientists need to register their trained models in the registry with proper metadata and versioning.

**What it demonstrates**:
- Creating models with name and description
- Creating multiple versions with different metadata
- Listing models and versions
- Search functionality by name/description

**Verification steps**:
- Models are created with unique IDs
- Model metadata is stored correctly
- Version information is accurate
- Search functionality works properly

**Duration**: ~2-3 minutes

---

### 2. Model Lifecycle Management (`02_model_lifecycle_management.py`)
**Use Case**: MLOps engineers need to manage model deployments through different stages (draft → staging → production → archived) with proper validation.

**What it demonstrates**:
- Status transitions through the model lifecycle
- Promotion workflow with validation
- Production version limitations (only one per model)
- Model archival process
- Lifecycle rule enforcement

**Verification steps**:
- Status transitions work correctly
- Only one production version per model enforced
- Promotion validation works
- Archived models are handled properly

**Duration**: ~3-4 minutes

---

### 3. Evaluation and Metrics (`03_evaluation_and_metrics.py`)
**Use Case**: Data scientists and ML engineers need to track model performance across different evaluations, compare versions, and generate visualization data for monitoring dashboards.

**What it demonstrates**:
- Creating multiple evaluations for model versions
- Model comparison by different metrics
- Metrics visualization data generation
- Comprehensive performance tracking
- Business impact evaluation

**Verification steps**:
- Evaluations are created with proper metrics
- Model comparison works across versions
- Visualization data is structured correctly
- Evaluation retrieval and filtering work

**Duration**: ~4-5 minutes

---

### 4. Artifact Operations (`04_artifact_operations.py`)
**Use Case**: ML engineers need to store and retrieve model artifacts (trained models) in various formats with proper validation and file management.

**What it demonstrates**:
- Artifact upload in different formats (pickle, joblib, onnx, h5, etc.)
- Artifact download functionality
- File size validation and limits
- Format validation and support
- Artifact deletion and cleanup
- Multi-format support verification

**Verification steps**:
- Artifacts are uploaded successfully
- Downloads work and files maintain integrity
- File size validation functions properly
- Format validation works
- Artifact deletion is successful

**Duration**: ~3-4 minutes

---

### 5. End-to-End Workflow (`05_end_to_end_workflow.py`)
**Use Case**: Complete MLOps workflow from model development to production deployment, including experimentation, evaluation, artifact management, and lifecycle management.

**What it demonstrates**:
- Complete ML project simulation
- Multiple algorithm experiments and comparison
- Comprehensive evaluation and metrics tracking
- Artifact management with real trained models
- Full lifecycle management through production
- Advanced search and filtering capabilities
- Model governance and audit trail

**Verification steps**:
- Complete workflow executes without errors
- Models progress through proper lifecycle stages
- Best model is identified and promoted to production
- Audit trail is maintained throughout
- All registry features work together seamlessly

**Duration**: ~8-10 minutes

## Quick Start

### Prerequisites
1. **API Running**: Start the ML Model Registry application
   ```bash
   poetry run python -m app.main
   ```
   The API should be accessible at `http://localhost:8000`

2. **Python Dependencies**: Required packages (automatically checked)
   - `requests` - HTTP client for API calls
   - `scikit-learn` - Machine learning library (for demos 4 & 5)
   - `numpy` - Numerical computing (for demos 4 & 5) 
   - `joblib` - Model serialization (for artifact demos)

### Running Demos

#### Option 1: Using the Demo Runner (Recommended)
The demo runner provides the best experience with progress tracking, error handling, and comprehensive reporting:

```bash
# Check prerequisites
python demos/run_demos.py --check

# List all available demos
python demos/run_demos.py --list

# Run all demos
python demos/run_demos.py --all

# Run specific demo
python demos/run_demos.py --demo 1

# Run multiple demos
python demos/run_demos.py --demo 1,3,5

# Clean up demo data
python demos/run_demos.py --clean
```

#### Option 2: Running Individual Scripts
You can run demos individually for focused testing:

```bash
# Basic model registration
python demos/01_basic_model_registration.py

# Model lifecycle management  
python demos/02_model_lifecycle_management.py

# Evaluation and metrics
python demos/03_evaluation_and_metrics.py

# Artifact operations
python demos/04_artifact_operations.py

# End-to-end workflow
python demos/05_end_to_end_workflow.py
```

## Understanding Demo Results

### Success Indicators
Each demo script provides clear success/failure indicators:
- ✓ marks successful operations
- ✗ marks failed operations
- Final result: `SUCCESS` or `FAILED`

### Verification Sections
Every demo includes comprehensive verification:
1. **Operation Verification**: Checks that each API operation succeeded
2. **Data Integrity**: Verifies that data was stored and retrieved correctly
3. **Business Logic**: Confirms that application rules are enforced
4. **Performance Metrics**: Validates that metrics and comparisons work

### Sample Output
```
Demo Result: SUCCESS

Model ID for other demos: 550e8400-e29b-41d4-a716-446655440000
```

## Use Case Coverage

The demos comprehensively test these ML Model Registry use cases:

### Core Functionality
- ✅ Model registration and metadata management
- ✅ Version creation and management
- ✅ Model search and discovery
- ✅ Status lifecycle management
- ✅ Model promotion workflows

### Advanced Features
- ✅ Performance evaluation tracking
- ✅ Model comparison and ranking
- ✅ Metrics visualization data
- ✅ Multi-format artifact storage
- ✅ File upload/download operations
- ✅ Data validation and error handling

### MLOps Workflows
- ✅ Experimentation and algorithm comparison
- ✅ Model validation and testing
- ✅ Production deployment
- ✅ Model governance and audit trails
- ✅ A/B testing support
- ✅ Model retirement and archival

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   ```
   ✗ Cannot connect to API
   ```
   **Solution**: Ensure the application is running:
   ```bash
   poetry run python -m app.main
   ```

2. **Import Errors**
   ```
   ✗ sklearn is missing
   ```
   **Solution**: Install dependencies:
   ```bash
   poetry install
   # or individually:
   pip install scikit-learn numpy joblib
   ```

3. **Demo Script Failures**
   ```
   ✗ Failed to create model: 500 - Internal server error
   ```
   **Solution**: Check application logs and database connectivity

4. **File Size Errors** 
   ```
   ✗ File too large. Maximum size is 100MB
   ```
   **Solution**: This is expected behavior for the file size validation test

### Debug Mode
For debugging, you can modify the demo scripts to add more verbose output or run with Python's debug flags:

```bash
python -v demos/01_basic_model_registration.py
```

### Data Cleanup
After running demos, you may want to clean up test data:

```bash
# Using the demo runner
python demos/run_demos.py --clean

# Or manually through the API
curl -X DELETE http://localhost:8000/api/v1/models/{model_id}
```

## Integration with Development Workflow

These demos serve multiple purposes in the development lifecycle:

1. **Feature Testing**: Validate new features and bug fixes
2. **API Documentation**: Live examples of API usage
3. **User Onboarding**: Help new users understand the system
4. **Regression Testing**: Ensure changes don't break existing functionality
5. **Performance Benchmarking**: Measure system performance under realistic load

## Contributing

When adding new features to the ML Model Registry:

1. **Update Existing Demos**: Modify relevant demos to showcase new functionality
2. **Add New Demo Scripts**: Create new demos for major new features
3. **Update Verification**: Ensure all new functionality has proper verification steps
4. **Document Use Cases**: Update this README with new use cases and verification steps

### Demo Script Template
```python
#!/usr/bin/env python3
"""
Demo Script N: Feature Name
===========================

Use Case: Describe the real-world use case

What this demo achieves:
1. Feature 1
2. Feature 2

Verification Steps:
- Check 1
- Check 2
"""

# Implementation with comprehensive verification and error handling
```

## Additional Resources

- **API Documentation**: http://localhost:8000/docs (when app is running)
- **Main Project README**: ../README.md  
- **Training Examples**: ../examples/
- **Test Suite**: ../app/tests/

For questions or issues with the demos, please check the main project documentation or create an issue in the project repository.