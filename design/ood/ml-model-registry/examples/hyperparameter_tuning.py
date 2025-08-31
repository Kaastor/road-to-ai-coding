#!/usr/bin/env python3
"""Hyperparameter tuning script that creates multiple model versions."""

import asyncio
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from io import BytesIO

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV
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


class HyperparameterTuner:
    """Hyperparameter tuning pipeline that creates multiple model versions."""
    
    def __init__(self):
        self.settings = get_settings()
        
    async def get_model_service(self) -> ModelService:
        """Get the model service instance."""
        async with get_db_session() as db:
            model_repo = SQLAlchemyModelRepository(db)
            version_repo = SQLAlchemyModelVersionRepository(db)
            file_storage = StorageFactory.create_file_storage(self.settings)
            return ModelService(model_repo, version_repo, file_storage)
    
    def create_synthetic_data(self, n_samples: int = 2000) -> tuple:
        """Create synthetic classification dataset."""
        print(f"Creating synthetic dataset with {n_samples} samples...")
        X, y = make_classification(
            n_samples=n_samples,
            n_features=25,
            n_informative=20,
            n_redundant=5,
            n_classes=3,  # Multi-class problem
            n_clusters_per_class=1,
            random_state=42
        )
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate the trained model."""
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted')
        }
        
        return metrics
    
    async def create_model_if_not_exists(self, model_name: str) -> str:
        """Create model if it doesn't exist, otherwise return existing model ID."""
        service = await self.get_model_service()
        
        # Try to get existing model
        existing_model = await service.get_model_by_name(model_name)
        if existing_model:
            print(f"Using existing model: {model_name} (ID: {existing_model.id})")
            return str(existing_model.id)
        
        # Create new model
        request = CreateModelRequest(
            name=model_name,
            description="Random Forest with hyperparameter tuning experiments"
        )
        
        created_model = await service.create_model(request)
        print(f"Created new model: {model_name} (ID: {created_model.id})")
        return str(created_model.id)
    
    async def train_and_register_version(
        self,
        model_id: str,
        version: str,
        hyperparams: Dict[str, Any],
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """Train a model with specific hyperparameters and register it."""
        print(f"Training version {version} with hyperparameters: {hyperparams}")
        
        # Train model
        model = RandomForestClassifier(**hyperparams, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        metrics = self.evaluate_model(model, X_test, y_test)
        print(f"Version {version} metrics: {metrics}")
        
        # Register version
        service = await self.get_model_service()
        
        metadata = ModelMetadataSchema(
            author="hyperparameter-tuner",
            description=f"RandomForest v{version} with tuned hyperparameters",
            tags=["tuning", "random-forest", "multi-class"],
            framework="scikit-learn",
            algorithm="RandomForest",
            dataset_name="synthetic_multiclass",
            hyperparameters=hyperparams,
            performance_metrics=metrics
        )
        
        version_request = CreateModelVersionRequest(
            version=version,
            metadata=metadata
        )
        
        created_version = await service.create_model_version(model_id, version_request)
        
        # Upload artifact
        model_data = pickle.dumps(model)
        model_file = BytesIO(model_data)
        
        await service.upload_artifact(
            model_id, 
            version, 
            model_file, 
            ModelFormat.PICKLE
        )
        
        # Create evaluation
        eval_request = CreateEvaluationRequest(
            evaluation_name=f"tuning_evaluation_{version.replace('.', '_')}",
            dataset_name="synthetic_multiclass_test",
            metrics=metrics,
            metadata={
                "hyperparameters": hyperparams,
                "evaluation_type": "hyperparameter_tuning",
                "evaluated_at": datetime.utcnow().isoformat()
            }
        )
        
        await service.create_evaluation(model_id, version, eval_request)
        
        return metrics
    
    async def run_hyperparameter_tuning(self):
        """Run hyperparameter tuning experiment."""
        print("Starting hyperparameter tuning pipeline...")
        
        # Create data
        X_train, X_test, y_train, y_test = self.create_synthetic_data()
        
        # Create or get model
        model_id = await self.create_model_if_not_exists("tuned-random-forest")
        
        # Define hyperparameter combinations to try
        hyperparameter_sets = [
            {
                "n_estimators": 50,
                "max_depth": 5,
                "min_samples_split": 2,
                "min_samples_leaf": 1
            },
            {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "min_samples_leaf": 2
            },
            {
                "n_estimators": 150,
                "max_depth": 15,
                "min_samples_split": 10,
                "min_samples_leaf": 4
            },
            {
                "n_estimators": 200,
                "max_depth": None,
                "min_samples_split": 20,
                "min_samples_leaf": 8
            }
        ]
        
        results = []
        
        # Train and register each version
        for i, hyperparams in enumerate(hyperparameter_sets, 1):
            version = f"2.{i}.0"
            
            try:
                metrics = await self.train_and_register_version(
                    model_id, version, hyperparams, X_train, y_train, X_test, y_test
                )
                
                results.append({
                    "version": version,
                    "hyperparams": hyperparams,
                    "metrics": metrics
                })
                
            except Exception as e:
                print(f"❌ Failed to train version {version}: {e}")
                continue
        
        # Find best performing version
        if results:
            best_result = max(results, key=lambda x: x["metrics"]["f1_score"])
            print(f"\n🏆 Best performing version: {best_result['version']}")
            print(f"   F1 Score: {best_result['metrics']['f1_score']:.4f}")
            print(f"   Hyperparameters: {best_result['hyperparams']}")
        
        print(f"\n✅ Hyperparameter tuning completed!")
        print(f"   Model ID: {model_id}")
        print(f"   Versions created: {len(results)}")
        print(f"\nYou can now compare versions using:")
        print(f"   GET /api/v1/models/{model_id}/compare/f1_score")
        
        return model_id, results


async def main():
    """Main function to run the hyperparameter tuning."""
    tuner = HyperparameterTuner()
    
    try:
        model_id, results = await tuner.run_hyperparameter_tuning()
        
        print(f"\n📊 Summary of all versions:")
        for result in results:
            print(f"   {result['version']}: F1={result['metrics']['f1_score']:.4f}, "
                  f"Acc={result['metrics']['accuracy']:.4f}")
                  
    except Exception as e:
        print(f"❌ Hyperparameter tuning failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())