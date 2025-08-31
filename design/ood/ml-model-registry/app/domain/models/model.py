from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, field
from uuid import UUID, uuid4


class ModelStatus(str, Enum):
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


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