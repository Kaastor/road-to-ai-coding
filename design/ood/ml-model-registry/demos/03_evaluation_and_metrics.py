#!/usr/bin/env python3
"""
Demo Script 3: Model Evaluation and Metrics
===========================================

This script demonstrates the evaluation and metrics tracking functionality
including creating evaluations, comparing model versions, and visualization data.

Use Case: Data scientists and ML engineers need to track model performance
across different evaluations, compare versions, and generate visualization data
for monitoring dashboards.

What this demo achieves:
1. Creates a model with multiple versions
2. Creates multiple evaluations for each version
3. Demonstrates model comparison by metrics
4. Shows metrics visualization data generation
5. Validates evaluation tracking and retrieval

Verification Steps:
- Verify evaluations are created with proper metrics
- Confirm model comparison works across versions
- Check visualization data is structured correctly
- Validate evaluation retrieval and filtering
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

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
        print(f"✓ Model created with ID: {model_data['id']}")
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
    
    print(f"Creating version {version}")
    response = requests.post(f"{BASE_URL}/models/{model_id}/versions", json=payload)
    
    if response.status_code == 201:
        version_data = response.json()
        print(f"✓ Version {version} created")
        return version_data
    else:
        print(f"✗ Failed to create version: {response.status_code} - {response.text}")
        return {}


def create_evaluation(model_id: str, version: str, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an evaluation for a model version."""
    print(f"Creating evaluation '{evaluation_data['evaluation_name']}' for version {version}")
    response = requests.post(f"{BASE_URL}/models/{model_id}/versions/{version}/evaluations", json=evaluation_data)
    
    if response.status_code == 201:
        eval_data = response.json()
        print(f"✓ Evaluation created with ID: {eval_data['id']}")
        return eval_data
    else:
        print(f"✗ Failed to create evaluation: {response.status_code} - {response.text}")
        return {}


def get_model_evaluations(model_id: str, version: str) -> List[Dict[str, Any]]:
    """Get all evaluations for a model version."""
    print(f"Retrieving evaluations for version {version}")
    response = requests.get(f"{BASE_URL}/models/{model_id}/versions/{version}/evaluations")
    
    if response.status_code == 200:
        evaluations = response.json()
        print(f"✓ Found {len(evaluations)} evaluations")
        return evaluations
    else:
        print(f"✗ Failed to get evaluations: {response.status_code}")
        return []


def compare_model_versions(model_id: str, metric_name: str) -> Dict[str, Any]:
    """Compare all versions of a model by a specific metric."""
    print(f"Comparing model versions by metric: {metric_name}")
    response = requests.get(f"{BASE_URL}/models/{model_id}/compare/{metric_name}")
    
    if response.status_code == 200:
        comparison_data = response.json()
        print(f"✓ Comparison data retrieved for {len(comparison_data.get('comparisons', []))} versions")
        return comparison_data
    else:
        print(f"✗ Failed to get comparison: {response.status_code} - {response.text}")
        return {}


def get_metrics_visualization(model_id: str) -> Dict[str, Any]:
    """Get structured metrics data for visualization."""
    print("Retrieving metrics visualization data")
    response = requests.get(f"{BASE_URL}/models/{model_id}/metrics/visualization")
    
    if response.status_code == 200:
        viz_data = response.json()
        print(f"✓ Visualization data retrieved")
        return viz_data
    else:
        print(f"✗ Failed to get visualization data: {response.status_code} - {response.text}")
        return {}


def print_evaluation_summary(evaluations: List[Dict[str, Any]]):
    """Print a summary of evaluations."""
    print("\nEvaluation Summary:")
    print("-" * 70)
    for eval_data in evaluations:
        print(f"Evaluation: {eval_data['evaluation_name']}")
        print(f"  Dataset: {eval_data['dataset_name']}")
        print(f"  Metrics: {json.dumps(eval_data['metrics'], indent=2)}")
        if eval_data.get('metadata'):
            print(f"  Metadata: {json.dumps(eval_data['metadata'], indent=2)}")
        print()


def print_comparison_results(comparison_data: Dict[str, Any]):
    """Print model comparison results."""
    if not comparison_data:
        return
    
    metric = comparison_data.get('metric_name', 'unknown')
    comparisons = comparison_data.get('comparisons', [])
    
    print(f"\nModel Comparison Results - {metric}:")
    print("-" * 50)
    
    # Sort by metric value (descending, handling None values)
    sorted_comparisons = sorted(
        comparisons, 
        key=lambda x: x.get('value') if x.get('value') is not None else -1,
        reverse=True
    )
    
    for comp in sorted_comparisons:
        version = comp.get('version', 'unknown')
        value = comp.get('value')
        source = comp.get('source', 'unknown')
        
        if value is not None:
            print(f"  Version {version:8} | {metric}: {value:.4f} (from {source})")
        else:
            print(f"  Version {version:8} | {metric}: No data")


def print_visualization_data(viz_data: Dict[str, Any]):
    """Print visualization data summary."""
    if not viz_data:
        return
    
    print("\nVisualization Data Summary:")
    print("-" * 50)
    
    model_info = viz_data.get('model_info', {})
    print(f"Model: {model_info.get('name', 'Unknown')} (ID: {model_info.get('id', 'Unknown')[:8]}...)")
    
    versions_data = viz_data.get('versions_data', [])
    print(f"Versions: {len(versions_data)}")
    
    for version_data in versions_data:
        version = version_data.get('version', 'unknown')
        status = version_data.get('status', 'unknown')
        evaluations = version_data.get('evaluations', [])
        
        print(f"\n  Version {version} ({status}):")
        
        # Show metadata metrics
        metadata = version_data.get('metadata', {})
        perf_metrics = metadata.get('performance_metrics', {})
        if perf_metrics:
            print(f"    Metadata Metrics: {json.dumps(perf_metrics, indent=6)}")
        
        # Show evaluation metrics
        if evaluations:
            print(f"    Evaluations ({len(evaluations)}):")
            for eval_data in evaluations:
                eval_name = eval_data.get('evaluation_name', 'unknown')
                metrics = eval_data.get('metrics', {})
                print(f"      {eval_name}: {json.dumps(metrics, indent=8)}")


def verify_evaluation_data(eval_data: Dict[str, Any], expected_name: str, expected_dataset: str) -> bool:
    """Verify evaluation data matches expectations."""
    checks = [
        ("evaluation_name", eval_data.get('evaluation_name') == expected_name),
        ("dataset_name", eval_data.get('dataset_name') == expected_dataset),
        ("id", "id" in eval_data and len(eval_data["id"]) == 36),  # UUID format
        ("model_version_id", "model_version_id" in eval_data),
        ("metrics", isinstance(eval_data.get("metrics"), dict)),
        ("created_at", "created_at" in eval_data)
    ]
    
    print(f"\nVerifying evaluation data:")
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run the evaluation and metrics demo."""
    print("=" * 60)
    print("Demo 3: Model Evaluation and Metrics")
    print("=" * 60)
    
    # Check API health
    print("Checking API health...")
    if not check_health():
        print("✗ API is not healthy. Please start the application first:")
        print("  poetry run python -m app.main")
        return
    print("✓ API is healthy")
    
    # Create a model for evaluation testing with unique name
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    model_data = create_model(
        name=f"evaluation-demo-model-{timestamp}",
        description="Model for demonstrating evaluation and metrics tracking"
    )
    
    if not model_data:
        return
    
    model_id = model_data["id"]
    
    # Phase 1: Create multiple versions with metadata
    print("\n" + "=" * 40)
    print("PHASE 1: Creating Model Versions")
    print("=" * 40)
    
    # Version 1.0.0 - baseline
    v1_metadata = {
        "author": "eval-demo-user",
        "framework": "scikit-learn",
        "algorithm": "random-forest",
        "dataset_name": "customer-churn-dataset",
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        },
        "performance_metrics": {
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87,
            "f1_score": 0.85,
            "auc_roc": 0.89
        },
        "tags": ["baseline", "v1", "evaluation-demo"]
    }
    
    v1_data = create_model_version(model_id, "v1.0.0", v1_metadata)
    if not v1_data:
        return
    
    # Version 2.0.0 - improved
    v2_metadata = {
        "author": "eval-demo-user",
        "framework": "scikit-learn", 
        "algorithm": "gradient-boosting",
        "dataset_name": "customer-churn-dataset",
        "hyperparameters": {
            "n_estimators": 150,
            "learning_rate": 0.1,
            "max_depth": 8,
            "random_state": 42
        },
        "performance_metrics": {
            "accuracy": 0.89,
            "precision": 0.88,
            "recall": 0.90,
            "f1_score": 0.89,
            "auc_roc": 0.93
        },
        "tags": ["improved", "v2", "evaluation-demo", "gradient-boosting"]
    }
    
    v2_data = create_model_version(model_id, "v2.0.0", v2_metadata)
    if not v2_data:
        return
    
    # Version 3.0.0 - experimental
    v3_metadata = {
        "author": "eval-demo-user",
        "framework": "scikit-learn",
        "algorithm": "xgboost", 
        "dataset_name": "customer-churn-dataset",
        "hyperparameters": {
            "n_estimators": 200,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "random_state": 42
        },
        "performance_metrics": {
            "accuracy": 0.91,
            "precision": 0.90,
            "recall": 0.92,
            "f1_score": 0.91,
            "auc_roc": 0.95
        },
        "tags": ["experimental", "v3", "evaluation-demo", "xgboost"]
    }
    
    v3_data = create_model_version(model_id, "v3.0.0", v3_metadata)
    
    # Phase 2: Create evaluations for each version
    print("\n" + "=" * 40)
    print("PHASE 2: Creating Model Evaluations")
    print("=" * 40)
    
    # Create evaluations for v1.0.0
    print("\nCreating evaluations for v1.0.0...")
    
    v1_eval1_data = {
        "evaluation_name": "validation-set-evaluation",
        "dataset_name": "validation-dataset",
        "metrics": {
            "accuracy": 0.84,
            "precision": 0.82,
            "recall": 0.86,
            "f1_score": 0.84,
            "auc_roc": 0.88
        },
        "metadata": {
            "dataset_size": 5000,
            "evaluation_date": "2024-01-15",
            "evaluator": "auto-validation-system",
            "cross_validation_folds": 5
        }
    }
    
    v1_eval1 = create_evaluation(model_id, "v1.0.0", v1_eval1_data)
    if v1_eval1:
        verify_evaluation_data(v1_eval1, "validation-set-evaluation", "validation-dataset")
    
    v1_eval2_data = {
        "evaluation_name": "test-set-evaluation", 
        "dataset_name": "test-dataset",
        "metrics": {
            "accuracy": 0.83,
            "precision": 0.81,
            "recall": 0.85,
            "f1_score": 0.83,
            "auc_roc": 0.87
        },
        "metadata": {
            "dataset_size": 2000,
            "evaluation_date": "2024-01-20",
            "evaluator": "manual-testing",
            "notes": "Final test before staging deployment"
        }
    }
    
    v1_eval2 = create_evaluation(model_id, "v1.0.0", v1_eval2_data)
    
    # Create evaluations for v2.0.0
    print("\nCreating evaluations for v2.0.0...")
    
    v2_eval1_data = {
        "evaluation_name": "validation-set-evaluation",
        "dataset_name": "validation-dataset", 
        "metrics": {
            "accuracy": 0.88,
            "precision": 0.87,
            "recall": 0.89,
            "f1_score": 0.88,
            "auc_roc": 0.92
        },
        "metadata": {
            "dataset_size": 5000,
            "evaluation_date": "2024-02-15",
            "evaluator": "auto-validation-system",
            "cross_validation_folds": 5,
            "improvement_over_v1": "3.4% accuracy increase"
        }
    }
    
    v2_eval1 = create_evaluation(model_id, "v2.0.0", v2_eval1_data)
    
    v2_eval2_data = {
        "evaluation_name": "production-a-b-test",
        "dataset_name": "production-sample",
        "metrics": {
            "accuracy": 0.87,
            "precision": 0.86,
            "recall": 0.88,
            "f1_score": 0.87,
            "auc_roc": 0.91,
            "conversion_rate": 0.156,
            "revenue_impact": 15.2
        },
        "metadata": {
            "dataset_size": 10000,
            "evaluation_date": "2024-02-25",
            "evaluator": "a-b-testing-system",
            "test_duration_days": 14,
            "statistical_significance": 0.95
        }
    }
    
    v2_eval2 = create_evaluation(model_id, "v2.0.0", v2_eval2_data)
    
    # Create evaluations for v3.0.0 (experimental)
    print("\nCreating evaluations for v3.0.0...")
    
    v3_eval1_data = {
        "evaluation_name": "validation-set-evaluation",
        "dataset_name": "validation-dataset",
        "metrics": {
            "accuracy": 0.90,
            "precision": 0.89,
            "recall": 0.91,
            "f1_score": 0.90,
            "auc_roc": 0.94
        },
        "metadata": {
            "dataset_size": 5000,
            "evaluation_date": "2024-03-10",
            "evaluator": "auto-validation-system", 
            "cross_validation_folds": 5,
            "improvement_over_v2": "2.3% accuracy increase"
        }
    }
    
    v3_eval1 = create_evaluation(model_id, "v3.0.0", v3_eval1_data)
    
    # Phase 3: Retrieve and verify evaluations
    print("\n" + "=" * 40)
    print("PHASE 3: Retrieving Evaluations")
    print("=" * 40)
    
    v1_evaluations = get_model_evaluations(model_id, "v1.0.0")
    print_evaluation_summary(v1_evaluations)
    
    v2_evaluations = get_model_evaluations(model_id, "v2.0.0")
    print_evaluation_summary(v2_evaluations)
    
    v3_evaluations = get_model_evaluations(model_id, "v3.0.0")
    print_evaluation_summary(v3_evaluations)
    
    # Phase 4: Model comparison by different metrics
    print("\n" + "=" * 40)
    print("PHASE 4: Model Version Comparison")
    print("=" * 40)
    
    # Compare by accuracy
    accuracy_comparison = compare_model_versions(model_id, "accuracy")
    print_comparison_results(accuracy_comparison)
    
    # Compare by f1_score
    f1_comparison = compare_model_versions(model_id, "f1_score")
    print_comparison_results(f1_comparison)
    
    # Compare by auc_roc
    auc_comparison = compare_model_versions(model_id, "auc_roc")
    print_comparison_results(auc_comparison)
    
    # Phase 5: Visualization data
    print("\n" + "=" * 40)
    print("PHASE 5: Metrics Visualization Data")
    print("=" * 40)
    
    viz_data = get_metrics_visualization(model_id)
    print_visualization_data(viz_data)
    
    # Final verification
    print("\n" + "=" * 50)
    print("DEMO VERIFICATION SUMMARY")
    print("=" * 50)
    
    total_evaluations = len(v1_evaluations) + len(v2_evaluations) + len(v3_evaluations)
    
    checks = [
        ("Model created", bool(model_data)),
        ("3 versions created", v3_data is not None),
        ("Evaluations created", total_evaluations >= 5),
        ("V1 evaluations", len(v1_evaluations) >= 2),
        ("V2 evaluations", len(v2_evaluations) >= 2), 
        ("V3 evaluations", len(v3_evaluations) >= 1),
        ("Accuracy comparison works", bool(accuracy_comparison)),
        ("F1 comparison works", bool(f1_comparison)),
        ("AUC comparison works", bool(auc_comparison)),
        ("Visualization data generated", bool(viz_data))
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\nDemo Result: {'SUCCESS' if all_passed else 'FAILED'}")
    
    # Print summary statistics
    print(f"\nSummary Statistics:")
    print(f"Model ID: {model_id}")
    print(f"Versions Created: 3")
    print(f"Total Evaluations: {total_evaluations}")
    print(f"Metrics Tracked: accuracy, precision, recall, f1_score, auc_roc")
    
    # Show best performing version by accuracy
    if accuracy_comparison and accuracy_comparison.get('comparisons'):
        best_version = max(
            accuracy_comparison['comparisons'],
            key=lambda x: x.get('value', 0) if x.get('value') is not None else 0
        )
        print(f"Best Version (by accuracy): {best_version.get('version')} ({best_version.get('value', 0):.3f})")


if __name__ == "__main__":
    main()