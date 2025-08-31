from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from uuid import UUID, uuid4


class ModelStatus(str, Enum):
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelEvaluation:
    """Comprehensive evaluation results for a model version."""
    id: UUID
    model_version_id: UUID
    evaluation_name: str
    dataset_name: str
    metrics: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        model_version_id: UUID,
        evaluation_name: str,
        dataset_name: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ModelEvaluation":
        """Create a new model evaluation."""
        return cls(
            id=uuid4(),
            model_version_id=model_version_id,
            evaluation_name=evaluation_name,
            dataset_name=dataset_name,
            metrics=metrics,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )


@dataclass
class ModelMetadata:
    """Metadata associated with a model."""
    author: str
    description: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    framework: Optional[str] = None
    algorithm: Optional[str] = None
    dataset_name: Optional[str] = None
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.author.strip():
            raise ValueError("Author cannot be empty")


@dataclass
class ModelVersion:
    """Represents a specific version of a model."""
    id: UUID
    model_id: UUID
    version: str
    status: ModelStatus
    artifact_path: Optional[str]
    metadata: ModelMetadata
    created_at: datetime
    updated_at: datetime
    evaluations: list[ModelEvaluation] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        model_id: UUID,
        version: str,
        metadata: ModelMetadata,
        status: ModelStatus = ModelStatus.DRAFT,
        artifact_path: Optional[str] = None
    ) -> ModelVersion:
        """Create a new model version."""
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            model_id=model_id,
            version=version,
            status=status,
            artifact_path=artifact_path,
            metadata=metadata,
            created_at=now,
            updated_at=now
        )
    
    def update_status(self, status: ModelStatus) -> None:
        """Update the status of the model version."""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def add_evaluation(self, evaluation: ModelEvaluation) -> None:
        """Add an evaluation to this model version."""
        if evaluation.model_version_id != self.id:
            raise ValueError("Evaluation model_version_id must match this version's id")
        self.evaluations.append(evaluation)
        self.update_timestamp()
    
    def get_evaluation(self, evaluation_name: str) -> Optional[ModelEvaluation]:
        """Get an evaluation by name."""
        return next((e for e in self.evaluations if e.evaluation_name == evaluation_name), None)
    
    def get_latest_evaluation(self) -> Optional[ModelEvaluation]:
        """Get the most recent evaluation."""
        if not self.evaluations:
            return None
        return max(self.evaluations, key=lambda e: e.created_at)


@dataclass
class Model:
    """Represents a machine learning model."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    versions: list[ModelVersion] = field(default_factory=list)
    
    @classmethod
    def create(cls, name: str, description: Optional[str] = None) -> Model:
        """Create a new model."""
        if not name.strip():
            raise ValueError("Model name cannot be empty")
        
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            created_at=now,
            updated_at=now
        )
    
    def add_version(self, version: ModelVersion) -> None:
        """Add a new version to this model."""
        if version.model_id != self.id:
            raise ValueError("Version model_id must match this model's id")
        
        if any(v.version == version.version for v in self.versions):
            raise ValueError(f"Version {version.version} already exists for this model")
        
        self.versions.append(version)
        self.updated_at = datetime.utcnow()
    
    def get_version(self, version: str) -> Optional[ModelVersion]:
        """Get a specific version of the model."""
        return next((v for v in self.versions if v.version == version), None)
    
    def get_latest_version(self) -> Optional[ModelVersion]:
        """Get the latest version of the model."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.created_at)
    
    def get_production_version(self) -> Optional[ModelVersion]:
        """Get the production version of the model."""
        return next(
            (v for v in self.versions if v.status == ModelStatus.PRODUCTION),
            None
        )
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def get_all_evaluations(self) -> list[ModelEvaluation]:
        """Get all evaluations across all versions."""
        evaluations = []
        for version in self.versions:
            evaluations.extend(version.evaluations)
        return evaluations
    
    def compare_versions_by_metric(self, metric_name: str) -> list[tuple[str, Optional[float]]]:
        """Compare all versions by a specific metric."""
        comparisons = []
        for version in self.versions:
            latest_eval = version.get_latest_evaluation()
            metric_value = latest_eval.metrics.get(metric_name) if latest_eval else None
            if metric_value is None and version.metadata.performance_metrics:
                metric_value = version.metadata.performance_metrics.get(metric_name)
            comparisons.append((version.version, metric_value))
        return comparisons