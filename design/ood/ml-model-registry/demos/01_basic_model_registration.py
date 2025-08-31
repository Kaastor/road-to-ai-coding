#!/usr/bin/env python3
"""
Demo Script 1: Basic Model Registration
======================================

This script demonstrates the core functionality of registering models and creating versions.

Use Case: Data scientists need to register their trained models in the registry
with proper metadata and versioning.

What this demo achieves:
1. Creates a new model with name and description
2. Creates multiple versions with different metadata
3. Lists models and versions
4. Shows model search functionality

Verification Steps:
- Check that models are created with unique IDs
- Verify model metadata is stored correctly
- Confirm version information is accurate
- Test search functionality works
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"


def check_health() -> bool:
    """Check if the API is healthy."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200 and response.json().get("status") == "healthy"
    except:
        return False


def create_model(name: str, description: str) -> Dict[str, Any]:
    """Create a new model."""
    payload = {
        "name": name,
        "description": description
    }
    
    print(f"Creating model: {name}")
    response = requests.post(f"{BASE_URL}/models/", json=payload)
    
    if response.status_code == 201:
        model_data = response.json()
        print(f"✓ Model created successfully with ID: {model_data['id']}")
        return model_data
    else:
        print(f"✗ Failed to create model: {response.status_code} - {response.text}")
        return {}


def create_model_version(model_id: str, version: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create a model version."""
    payload = {
        "version": version,
        "status": "draft",
        "metadata": metadata
    }
    
    print(f"Creating version {version} for model {model_id}")
    response = requests.post(f"{BASE_URL}/models/{model_id}/versions", json=payload)
    
    if response.status_code == 201:
        version_data = response.json()
        print(f"✓ Version {version} created successfully")
        return version_data
    else:
        print(f"✗ Failed to create version: {response.status_code} - {response.text}")
        return {}


def list_models() -> list:
    """List all models."""
    print("\nListing all models:")
    response = requests.get(f"{BASE_URL}/models/")
    
    if response.status_code == 200:
        models = response.json()
        print(f"✓ Found {len(models)} models")
        for model in models:
            print(f"  - {model['name']} (ID: {model['id'][:8]}...)")
        return models
    else:
        print(f"✗ Failed to list models: {response.status_code}")
        return []


def list_model_versions(model_id: str) -> list:
    """List versions for a specific model."""
    print(f"\nListing versions for model {model_id}:")
    response = requests.get(f"{BASE_URL}/models/{model_id}/versions")
    
    if response.status_code == 200:
        versions = response.json()
        print(f"✓ Found {len(versions)} versions")
        for version in versions:
            print(f"  - Version {version['version']} ({version['status']})")
            print(f"    Author: {version['metadata']['author']}")
        return versions
    else:
        print(f"✗ Failed to list versions: {response.status_code}")
        return []


def search_models(query: str) -> list:
    """Search models by name or description."""
    print(f"\nSearching models with query: '{query}'")
    response = requests.get(f"{BASE_URL}/models/", params={"search": query})
    
    if response.status_code == 200:
        models = response.json()
        print(f"✓ Search returned {len(models)} results")
        for model in models:
            print(f"  - {model['name']}: {model['description']}")
        return models
    else:
        print(f"✗ Search failed: {response.status_code}")
        return []


def verify_model_data(model: Dict[str, Any], expected_name: str, expected_description: str) -> bool:
    """Verify model data matches expectations."""
    checks = [
        ("name", model.get("name") == expected_name),
        ("description", model.get("description") == expected_description),
        ("id", "id" in model and len(model["id"]) == 36),  # UUID format
        ("created_at", "created_at" in model),
        ("updated_at", "updated_at" in model)
    ]
    
    print(f"\nVerifying model data:")
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def verify_version_data(version: Dict[str, Any], expected_version: str, expected_author: str) -> bool:
    """Verify version data matches expectations."""
    metadata = version.get("metadata", {})
    checks = [
        ("version", version.get("version") == expected_version),
        ("status", version.get("status") == "draft"),
        ("author", metadata.get("author") == expected_author),
        ("id", "id" in version and len(version["id"]) == 36),
        ("created_at", "created_at" in version),
        ("model_id", "model_id" in version)
    ]
    
    print(f"\nVerifying version data:")
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run the basic model registration demo."""
    print("=" * 50)
    print("Demo 1: Basic Model Registration")
    print("=" * 50)
    
    # Check API health
    print("Checking API health...")
    if not check_health():
        print("✗ API is not healthy. Please start the application first:")
        print("  poetry run python -m app.main")
        return
    print("✓ API is healthy")
    
    # Create a model with unique name
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    model_data = create_model(
        name=f"demo-classification-model-{timestamp}",
        description="A demonstration classification model for testing the registry"
    )
    
    if not model_data:
        return
    
    model_id = model_data["id"]
    
    # Verify model data
    verify_model_data(
        model_data, 
        "demo-classification-model",
        "A demonstration classification model for testing the registry"
    )
    
    # Create version 1
    version1_metadata = {
        "author": "demo-user",
        "description": "Initial version with basic features",
        "framework": "scikit-learn",
        "algorithm": "random-forest",
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 10
        },
        "performance_metrics": {
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87
        },
        "tags": ["classification", "demo", "v1"]
    }
    
    version1_data = create_model_version(model_id, "v1.0.0", version1_metadata)
    if version1_data:
        verify_version_data(version1_data, "v1.0.0", "demo-user")
    
    # Create version 2 with improved metrics
    version2_metadata = {
        "author": "demo-user",
        "description": "Improved version with feature engineering",
        "framework": "scikit-learn",
        "algorithm": "random-forest",
        "hyperparameters": {
            "n_estimators": 200,
            "max_depth": 15
        },
        "performance_metrics": {
            "accuracy": 0.89,
            "precision": 0.88,
            "recall": 0.90
        },
        "tags": ["classification", "demo", "v2", "improved"]
    }
    
    version2_data = create_model_version(model_id, "v2.0.0", version2_metadata)
    if version2_data:
        verify_version_data(version2_data, "v2.0.0", "demo-user")
    
    # List all models
    models = list_models()
    
    # List versions for our model
    versions = list_model_versions(model_id)
    
    # Test search functionality
    search_results = search_models("classification")
    
    # Final verification
    print("\n" + "=" * 50)
    print("DEMO VERIFICATION SUMMARY")
    print("=" * 50)
    
    checks = [
        ("Model created", bool(model_data)),
        ("Version 1 created", bool(version1_data)),
        ("Version 2 created", bool(version2_data)),
        ("Models listed", len(models) > 0),
        ("Versions listed", len(versions) == 2),
        ("Search works", len(search_results) > 0)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\nDemo Result: {'SUCCESS' if all_passed else 'FAILED'}")
    
    # Print model ID for use in other demos
    if model_data:
        print(f"\nModel ID for other demos: {model_id}")


if __name__ == "__main__":
    main()