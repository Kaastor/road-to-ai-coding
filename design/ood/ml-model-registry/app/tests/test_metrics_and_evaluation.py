"""Integration tests for metrics tracking and evaluation features."""

import pytest
from datetime import datetime
from uuid import uuid4
from io import BytesIO
import pickle

from app.domain.models.model import Model, ModelVersion, ModelEvaluation, ModelStatus
from app.domain.models.schemas import (
    CreateModelRequest,
    CreateModelVersionRequest,
    ModelMetadataSchema,
    CreateEvaluationRequest
)
from app.services.model_service import ModelService
from app.infrastructure.storage.file_storage import ModelFormat


class MockMLModel:
    """Mock ML model for testing."""
    
    def __init__(self, model_type: str = "classifier"):
        self.model_type = model_type
        self.trained = True
        self.version = "1.0.0"
        self.params = {"n_estimators": 100, "max_depth": 10}
    
    def predict(self, X):
        """Mock prediction method."""
        import numpy as np
        # Return random predictions for testing
        return np.random.choice([0, 1], size=len(X))
    
    def get_feature_importance(self):
        """Mock feature importance."""
        return {"feature_1": 0.3, "feature_2": 0.7}


@pytest.mark.asyncio
class TestMetricsAndEvaluation:
    """Test metrics tracking and evaluation functionality."""
    
    async def test_create_evaluation_for_model_version(self, model_service: ModelService):
        """Test creating an evaluation for a model version."""
        # Create model
        model_request = CreateModelRequest(
            name="test-evaluation-model",
            description="Model for evaluation testing"
        )
        model = await model_service.create_model(model_request)
        
        # Create version
        metadata = ModelMetadataSchema(
            author="test-user",
            description="Test version",
            tags=["test"],
            framework="scikit-learn",
            algorithm="RandomForest",
            dataset_name="test_dataset",
            performance_metrics={"accuracy": 0.85}
        )
        
        version_request = CreateModelVersionRequest(
            version="1.0.0",
            metadata=metadata
        )
        
        version = await model_service.create_model_version(model.id, version_request)
        
        # Create evaluation
        eval_request = CreateEvaluationRequest(
            evaluation_name="test_evaluation",
            dataset_name="validation_set",
            metrics={
                "accuracy": 0.87,
                "precision": 0.85,
                "recall": 0.89,
                "f1_score": 0.87
            },
            metadata={"evaluation_type": "holdout"}
        )
        
        evaluation = await model_service.create_evaluation(
            model.id, "1.0.0", eval_request
        )
        
        # Verify evaluation
        assert evaluation.model_version_id == version.id
        assert evaluation.evaluation_name == "test_evaluation"
        assert evaluation.dataset_name == "validation_set"
        assert evaluation.metrics["accuracy"] == 0.87
        assert evaluation.metrics["f1_score"] == 0.87
        assert evaluation.metadata["evaluation_type"] == "holdout"
        assert evaluation.created_at is not None
    
    async def test_get_model_evaluations(self, model_service: ModelService):
        """Test retrieving all evaluations for a model version."""
        # Create model and version
        model_request = CreateModelRequest(name="eval-test-model")
        model = await model_service.create_model(model_request)
        
        metadata = ModelMetadataSchema(author="test-user", tags=["test"])
        version_request = CreateModelVersionRequest(version="1.0.0", metadata=metadata)
        await model_service.create_model_version(model.id, version_request)
        
        # Create multiple evaluations
        evaluations_data = [
            {"name": "eval_1", "dataset": "train_set", "accuracy": 0.85},
            {"name": "eval_2", "dataset": "val_set", "accuracy": 0.82},
            {"name": "eval_3", "dataset": "test_set", "accuracy": 0.80}
        ]
        
        for eval_data in evaluations_data:
            eval_request = CreateEvaluationRequest(
                evaluation_name=eval_data["name"],
                dataset_name=eval_data["dataset"],
                metrics={"accuracy": eval_data["accuracy"]}
            )
            await model_service.create_evaluation(model.id, "1.0.0", eval_request)
        
        # Retrieve evaluations
        evaluations = await model_service.get_model_evaluations(model.id, "1.0.0")
        
        assert len(evaluations) == 3
        eval_names = [e.evaluation_name for e in evaluations]
        assert "eval_1" in eval_names
        assert "eval_2" in eval_names
        assert "eval_3" in eval_names
    
    async def test_model_version_comparison(self, model_service: ModelService):
        """Test comparing model versions by metrics."""
        # Create model
        model_request = CreateModelRequest(name="comparison-test-model")
        model = await model_service.create_model(model_request)
        
        # Create multiple versions with different performance
        versions_data = [
            {"version": "1.0.0", "accuracy": 0.80, "f1_score": 0.78},
            {"version": "1.1.0", "accuracy": 0.85, "f1_score": 0.83},
            {"version": "1.2.0", "accuracy": 0.88, "f1_score": 0.86},
            {"version": "2.0.0", "accuracy": 0.82, "f1_score": 0.80}
        ]
        
        for version_data in versions_data:
            metadata = ModelMetadataSchema(
                author="test-user",
                tags=["comparison"],
                performance_metrics={
                    "accuracy": version_data["accuracy"],
                    "f1_score": version_data["f1_score"]
                }
            )
            
            version_request = CreateModelVersionRequest(
                version=version_data["version"],
                metadata=metadata
            )
            
            await model_service.create_model_version(model.id, version_request)
        
        # Compare by accuracy
        comparison = await model_service.compare_model_versions_by_metric(
            model.id, "accuracy"
        )
        
        assert comparison.metric_name == "accuracy"
        assert len(comparison.versions) == 4
        
        # Should be sorted by accuracy descending (best first)
        accuracies = [v["metric_value"] for v in comparison.versions]
        assert accuracies == [0.88, 0.85, 0.82, 0.80]  # Sorted descending
        
        # Check version order
        versions = [v["version"] for v in comparison.versions]
        assert versions[0] == "1.2.0"  # Best performing
        assert versions[-1] == "1.0.0"  # Worst performing
    
    async def test_metrics_visualization_data(self, model_service: ModelService):
        """Test getting metrics visualization data."""
        # Create model
        model_request = CreateModelRequest(name="viz-test-model")
        model = await model_service.create_model(model_request)
        
        # Create version with metadata metrics
        metadata = ModelMetadataSchema(
            author="test-user",
            tags=["visualization"],
            performance_metrics={"accuracy": 0.85, "precision": 0.83}
        )
        
        version_request = CreateModelVersionRequest(
            version="1.0.0",
            metadata=metadata
        )
        
        await model_service.create_model_version(model.id, version_request)
        
        # Add evaluation with additional metrics
        eval_request = CreateEvaluationRequest(
            evaluation_name="comprehensive_eval",
            dataset_name="test_set",
            metrics={
                "accuracy": 0.87,  # Different from metadata
                "precision": 0.85,
                "recall": 0.89,
                "f1_score": 0.87
            }
        )
        
        await model_service.create_evaluation(model.id, "1.0.0", eval_request)
        
        # Get visualization data
        viz_data = await model_service.get_metrics_visualization_data(model.id)
        
        assert viz_data.model_id == model.id
        assert viz_data.model_name == "viz-test-model"
        
        metrics_data = viz_data.metrics_data
        assert "available_metrics" in metrics_data
        assert "versions" in metrics_data
        assert "total_versions" in metrics_data
        assert "total_evaluations" in metrics_data
        
        # Check available metrics includes all unique metrics
        available_metrics = set(metrics_data["available_metrics"])
        expected_metrics = {"accuracy", "precision", "recall", "f1_score"}
        assert expected_metrics.issubset(available_metrics)
        
        # Check version data
        version_data = metrics_data["versions"]["1.0.0"]
        assert version_data["version"] == "1.0.0"
        assert version_data["status"] == "draft"
        assert len(version_data["evaluations"]) == 1
        
        # Check evaluation data
        eval_data = version_data["evaluations"][0]
        assert eval_data["name"] == "comprehensive_eval"
        assert eval_data["dataset"] == "test_set"
        assert eval_data["metrics"]["f1_score"] == 0.87
    
    async def test_mock_ml_model_integration(self, model_service: ModelService):
        """Test integration with mock ML model including artifact storage."""
        # Create mock model
        mock_model = MockMLModel("classifier")
        
        # Create model in registry
        model_request = CreateModelRequest(
            name="mock-ml-model",
            description="Integration test with mock ML model"
        )
        model = await model_service.create_model(model_request)
        
        # Create version with mock model metadata
        metadata = ModelMetadataSchema(
            author="integration-test",
            description="Mock ML model for testing",
            tags=["mock", "integration", "test"],
            framework="test-framework",
            algorithm="MockClassifier",
            dataset_name="synthetic_data",
            hyperparameters=mock_model.params,
            performance_metrics={
                "accuracy": 0.92,
                "precision": 0.91,
                "recall": 0.93
            }
        )
        
        version_request = CreateModelVersionRequest(
            version=mock_model.version,
            metadata=metadata
        )
        
        version = await model_service.create_model_version(model.id, version_request)
        
        # Store mock model as artifact
        model_data = pickle.dumps(mock_model)
        model_file = BytesIO(model_data)
        
        upload_result = await model_service.upload_artifact(
            model.id, mock_model.version, model_file, ModelFormat.PICKLE
        )
        
        assert upload_result.format == ModelFormat.PICKLE
        assert upload_result.size > 0
        
        # Download and verify artifact
        downloaded_file = await model_service.download_artifact(
            model.id, mock_model.version
        )
        
        downloaded_model = pickle.load(downloaded_file)
        assert downloaded_model.model_type == mock_model.model_type
        assert downloaded_model.version == mock_model.version
        assert downloaded_model.params == mock_model.params
        
        # Create evaluation with mock predictions
        import numpy as np
        X_test = np.random.rand(100, 5)
        predictions = mock_model.predict(X_test)
        
        # Simulate evaluation metrics
        eval_metrics = {
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.91,
            "f1_score": 0.89,
            "samples_evaluated": len(X_test)
        }
        
        eval_request = CreateEvaluationRequest(
            evaluation_name="mock_model_evaluation",
            dataset_name="synthetic_test_data",
            metrics=eval_metrics,
            metadata={
                "model_type": mock_model.model_type,
                "prediction_samples": len(predictions),
                "feature_importance": mock_model.get_feature_importance()
            }
        )
        
        evaluation = await model_service.create_evaluation(
            model.id, mock_model.version, eval_request
        )
        
        assert evaluation.metrics["samples_evaluated"] == 100
        assert evaluation.metadata["model_type"] == "classifier"
        assert "feature_importance" in evaluation.metadata
    
    async def test_model_lifecycle_with_evaluations(self, model_service: ModelService):
        """Test model lifecycle progression with evaluation requirements."""
        # Create model
        model_request = CreateModelRequest(name="lifecycle-test-model")
        model = await model_service.create_model(model_request)
        
        # Create draft version
        metadata = ModelMetadataSchema(
            author="test-user",
            tags=["lifecycle"],
            performance_metrics={"accuracy": 0.75}
        )
        
        version_request = CreateModelVersionRequest(
            version="1.0.0",
            metadata=metadata,
            status=ModelStatus.DRAFT
        )
        
        version = await model_service.create_model_version(model.id, version_request)
        assert version.status == ModelStatus.DRAFT
        
        # Add evaluation before promotion
        eval_request = CreateEvaluationRequest(
            evaluation_name="validation_eval",
            dataset_name="validation_set",
            metrics={"accuracy": 0.88, "precision": 0.86, "recall": 0.90}
        )
        
        evaluation = await model_service.create_evaluation(
            model.id, "1.0.0", eval_request
        )
        
        # Promote to staging (simulating approval after evaluation)
        from app.domain.models.schemas import PromoteModelRequest
        promote_request = PromoteModelRequest(
            to_status=ModelStatus.STAGING,
            reason="Evaluation metrics meet staging criteria"
        )
        
        promoted_version = await model_service.promote_model_version(
            model.id, "1.0.0", promote_request
        )
        
        assert promoted_version.status == ModelStatus.STAGING
        assert len(promoted_version.evaluations) == 1
        assert promoted_version.evaluations[0].evaluation_name == "validation_eval"


@pytest.fixture
async def model_service(mock_model_repo, mock_version_repo, mock_file_storage):
    """Create a model service for testing."""
    return ModelService(mock_model_repo, mock_version_repo, mock_file_storage)