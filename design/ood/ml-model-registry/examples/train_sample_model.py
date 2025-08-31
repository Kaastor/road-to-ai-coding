#!/usr/bin/env python3
"""Sample ML model training script for demonstration purposes."""

import asyncio
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from io import BytesIO

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Add the app directory to path so we can import from it
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.domain.models.schemas import (
    CreateModelRequest, 
    CreateModelVersionRequest, 
    ModelMetadataSchema,
    CreateEvaluationRequest
)
from app.services.model_service import ModelService
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SQLAlchemyModelRepository,
    SQLAlchemyModelVersionRepository
)
from app.infrastructure.storage.database import get_db_session
from app.infrastructure.storage.storage_factory import StorageFactory
from app.infrastructure.storage.file_storage import ModelFormat
from app.config import get_settings


class SampleModelTrainer:
    """Sample model trainer to demonstrate the ML registry usage."""
    
    def __init__(self):
        self.settings = get_settings()
        
    async def get_model_service(self) -> ModelService:
        """Get the model service instance."""
        async with get_db_session() as db:
            model_repo = SQLAlchemyModelRepository(db)
            version_repo = SQLAlchemyModelVersionRepository(db)
            file_storage = StorageFactory.create_file_storage(self.settings)
            return ModelService(model_repo, version_repo, file_storage)
    
    def create_synthetic_data(self, n_samples: int = 1000, n_features: int = 20) -> tuple:
        """Create synthetic classification dataset."""
        print(f"Creating synthetic dataset with {n_samples} samples and {n_features} features...")
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=15,
            n_redundant=5,
            n_classes=2,
            random_state=42
        )
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """Train a Random Forest model."""
        print("Training Random Forest model...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model: RandomForestClassifier, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate the trained model."""
        print("Evaluating model...")
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted')
        }
        
        print(f"Model metrics: {metrics}")
        return metrics
    
    async def register_model(self, model_name: str, description: str) -> str:
        """Register a new model in the registry."""
        service = await self.get_model_service()
        
        request = CreateModelRequest(
            name=model_name,
            description=description
        )
        
        created_model = await service.create_model(request)
        print(f"Created model: {created_model.name} (ID: {created_model.id})")
        return str(created_model.id)
    
    async def register_model_version(
        self, 
        model_id: str, 
        version: str, 
        model_obj: Any, 
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any]
    ) -> str:
        """Register a model version with artifact."""
        service = await self.get_model_service()
        
        metadata = ModelMetadataSchema(
            author="sample-trainer",
            description=f"Random Forest v{version} trained on synthetic data",
            tags=["sample", "random-forest", "classification"],
            framework="scikit-learn",
            algorithm="RandomForest",
            dataset_name="synthetic_classification",
            hyperparameters=hyperparameters,
            performance_metrics=metrics
        )
        
        version_request = CreateModelVersionRequest(
            version=version,
            metadata=metadata
        )
        
        created_version = await service.create_model_version(model_id, version_request)
        
        # Upload the model artifact
        model_data = pickle.dumps(model_obj)
        model_file = BytesIO(model_data)
        
        await service.upload_artifact(
            model_id, 
            version, 
            model_file, 
            ModelFormat.PICKLE
        )
        
        print(f"Created version: {version} for model {model_id}")
        return str(created_version.id)
    
    async def create_evaluation(
        self, 
        model_id: str, 
        version: str, 
        evaluation_name: str,
        dataset_name: str,
        metrics: Dict[str, float]
    ):
        """Create an evaluation record for the model version."""
        service = await self.get_model_service()
        
        eval_request = CreateEvaluationRequest(
            evaluation_name=evaluation_name,
            dataset_name=dataset_name,
            metrics=metrics,
            metadata={
                "evaluated_at": datetime.utcnow().isoformat(),
                "evaluation_type": "holdout_test"
            }
        )
        
        evaluation = await service.create_evaluation(model_id, version, eval_request)
        print(f"Created evaluation: {evaluation_name} for version {version}")
    
    async def run_training_pipeline(self):
        """Run the complete training pipeline."""
        print("Starting ML model training pipeline...")
        
        # Create data
        X_train, X_test, y_train, y_test = self.create_synthetic_data()
        
        # Train model
        model = self.train_model(X_train, y_train)
        
        # Evaluate model
        metrics = self.evaluate_model(model, X_test, y_test)
        
        # Hyperparameters
        hyperparams = {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        }
        
        # Register in model registry
        model_id = await self.register_model(
            "sample-random-forest",
            "Sample Random Forest classifier for demonstration"
        )
        
        version = "1.0.0"
        version_id = await self.register_model_version(
            model_id, version, model, metrics, hyperparams
        )
        
        # Create evaluation record
        await self.create_evaluation(
            model_id, version, "initial_evaluation", "synthetic_test_set", metrics
        )
        
        print(f"✅ Pipeline completed! Model ID: {model_id}, Version: {version}")
        
        return model_id, version


async def main():
    """Main function to run the training pipeline."""
    trainer = SampleModelTrainer()
    try:
        model_id, version = await trainer.run_training_pipeline()
        print(f"\n🎉 Successfully trained and registered model!")
        print(f"   Model ID: {model_id}")
        print(f"   Version: {version}")
        print(f"\nYou can now use the API to:")
        print(f"   - View model: GET /api/v1/models/{model_id}")
        print(f"   - Compare versions: GET /api/v1/models/{model_id}/compare/accuracy")
        print(f"   - View metrics: GET /api/v1/models/{model_id}/metrics/visualization")
        
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())