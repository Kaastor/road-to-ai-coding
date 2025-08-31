from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.domain.models.model import Model, ModelVersion, ModelMetadata, ModelStatus
from app.domain.exceptions.exceptions import ModelNotFoundError, ModelVersionNotFoundError
from app.infrastructure.repositories.base import ModelRepository, ModelVersionRepository
from app.infrastructure.storage.models import ModelTable, ModelVersionTable


class SQLAlchemyModelRepository(ModelRepository):
    """SQLAlchemy implementation of ModelRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create(self, entity: Model) -> Model:
        """Create a new model."""
        db_model = ModelTable(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        self.session.add(db_model)
        self.session.commit()
        self.session.refresh(db_model)
        return self._to_domain_model(db_model)
    
    async def get_by_id(self, entity_id: UUID) -> Optional[Model]:
        """Get model by ID."""
        db_model = self.session.query(ModelTable).options(
            joinedload(ModelTable.versions)
        ).filter(ModelTable.id == entity_id).first()
        
        if not db_model:
            return None
        
        return self._to_domain_model(db_model)
    
    async def get_by_name(self, name: str) -> Optional[Model]:
        """Get model by name."""
        db_model = self.session.query(ModelTable).options(
            joinedload(ModelTable.versions)
        ).filter(ModelTable.name == name).first()
        
        if not db_model:
            return None
        
        return self._to_domain_model(db_model)
    
    async def update(self, entity: Model) -> Model:
        """Update an existing model."""
        db_model = self.session.query(ModelTable).filter(ModelTable.id == entity.id).first()
        if not db_model:
            raise ModelNotFoundError(entity.id)
        
        db_model.name = entity.name
        db_model.description = entity.description
        db_model.updated_at = entity.updated_at
        
        self.session.commit()
        self.session.refresh(db_model)
        return self._to_domain_model(db_model)
    
    async def delete(self, entity_id: UUID) -> bool:
        """Delete a model by ID."""
        db_model = self.session.query(ModelTable).filter(ModelTable.id == entity_id).first()
        if not db_model:
            return False
        
        self.session.delete(db_model)
        self.session.commit()
        return True
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Model]:
        """List all models with pagination."""
        db_models = self.session.query(ModelTable).options(
            joinedload(ModelTable.versions)
        ).offset(skip).limit(limit).all()
        
        return [self._to_domain_model(db_model) for db_model in db_models]
    
    async def search_by_tags(self, tags: list[str]) -> list[Model]:
        """Search models by tags."""
        db_models = self.session.query(ModelTable).join(ModelVersionTable).filter(
            ModelVersionTable.tags.contains(tags)
        ).distinct().all()
        
        return [self._to_domain_model(db_model) for db_model in db_models]
    
    def _to_domain_model(self, db_model: ModelTable) -> Model:
        """Convert SQLAlchemy model to domain model."""
        domain_model = Model(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            versions=[]
        )
        
        for db_version in db_model.versions:
            domain_version = self._to_domain_version(db_version)
            domain_model.versions.append(domain_version)
        
        return domain_model
    
    def _to_domain_version(self, db_version: ModelVersionTable) -> ModelVersion:
        """Convert SQLAlchemy version to domain version."""
        metadata = ModelMetadata(
            author=db_version.author,
            description=db_version.description,
            tags=db_version.tags or [],
            framework=db_version.framework,
            algorithm=db_version.algorithm,
            dataset_name=db_version.dataset_name,
            hyperparameters=db_version.hyperparameters or {},
            performance_metrics=db_version.performance_metrics or {}
        )
        
        return ModelVersion(
            id=db_version.id,
            model_id=db_version.model_id,
            version=db_version.version,
            status=db_version.status,
            artifact_path=db_version.artifact_path,
            metadata=metadata,
            created_at=db_version.created_at,
            updated_at=db_version.updated_at
        )


class SQLAlchemyModelVersionRepository(ModelVersionRepository):
    """SQLAlchemy implementation of ModelVersionRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create(self, entity: ModelVersion) -> ModelVersion:
        """Create a new model version."""
        db_version = ModelVersionTable(
            id=entity.id,
            model_id=entity.model_id,
            version=entity.version,
            status=entity.status,
            artifact_path=entity.artifact_path,
            author=entity.metadata.author,
            description=entity.metadata.description,
            tags=entity.metadata.tags,
            framework=entity.metadata.framework,
            algorithm=entity.metadata.algorithm,
            dataset_name=entity.metadata.dataset_name,
            hyperparameters=entity.metadata.hyperparameters,
            performance_metrics=entity.metadata.performance_metrics,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        self.session.add(db_version)
        self.session.commit()
        self.session.refresh(db_version)
        return self._to_domain_version(db_version)
    
    async def get_by_id(self, entity_id: UUID) -> Optional[ModelVersion]:
        """Get version by ID."""
        db_version = self.session.query(ModelVersionTable).filter(
            ModelVersionTable.id == entity_id
        ).first()
        
        if not db_version:
            return None
        
        return self._to_domain_version(db_version)
    
    async def get_by_model_and_version(self, model_id: UUID, version: str) -> Optional[ModelVersion]:
        """Get version by model ID and version string."""
        db_version = self.session.query(ModelVersionTable).filter(
            and_(ModelVersionTable.model_id == model_id, ModelVersionTable.version == version)
        ).first()
        
        if not db_version:
            return None
        
        return self._to_domain_version(db_version)
    
    async def update(self, entity: ModelVersion) -> ModelVersion:
        """Update an existing model version."""
        db_version = self.session.query(ModelVersionTable).filter(
            ModelVersionTable.id == entity.id
        ).first()
        
        if not db_version:
            raise ModelVersionNotFoundError(entity.model_id, entity.version)
        
        db_version.status = entity.status
        db_version.artifact_path = entity.artifact_path
        db_version.author = entity.metadata.author
        db_version.description = entity.metadata.description
        db_version.tags = entity.metadata.tags
        db_version.framework = entity.metadata.framework
        db_version.algorithm = entity.metadata.algorithm
        db_version.dataset_name = entity.metadata.dataset_name
        db_version.hyperparameters = entity.metadata.hyperparameters
        db_version.performance_metrics = entity.metadata.performance_metrics
        db_version.updated_at = entity.updated_at
        
        self.session.commit()
        self.session.refresh(db_version)
        return self._to_domain_version(db_version)
    
    async def delete(self, entity_id: UUID) -> bool:
        """Delete a version by ID."""
        db_version = self.session.query(ModelVersionTable).filter(
            ModelVersionTable.id == entity_id
        ).first()
        
        if not db_version:
            return False
        
        self.session.delete(db_version)
        self.session.commit()
        return True
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelVersion]:
        """List all versions with pagination."""
        db_versions = self.session.query(ModelVersionTable).offset(skip).limit(limit).all()
        return [self._to_domain_version(db_version) for db_version in db_versions]
    
    async def list_by_model(self, model_id: UUID) -> list[ModelVersion]:
        """List all versions for a specific model."""
        db_versions = self.session.query(ModelVersionTable).filter(
            ModelVersionTable.model_id == model_id
        ).order_by(ModelVersionTable.created_at.desc()).all()
        
        return [self._to_domain_version(db_version) for db_version in db_versions]
    
    async def get_latest_by_model(self, model_id: UUID) -> Optional[ModelVersion]:
        """Get the latest version for a specific model."""
        db_version = self.session.query(ModelVersionTable).filter(
            ModelVersionTable.model_id == model_id
        ).order_by(ModelVersionTable.created_at.desc()).first()
        
        if not db_version:
            return None
        
        return self._to_domain_version(db_version)
    
    def _to_domain_version(self, db_version: ModelVersionTable) -> ModelVersion:
        """Convert SQLAlchemy version to domain version."""
        metadata = ModelMetadata(
            author=db_version.author,
            description=db_version.description,
            tags=db_version.tags or [],
            framework=db_version.framework,
            algorithm=db_version.algorithm,
            dataset_name=db_version.dataset_name,
            hyperparameters=db_version.hyperparameters or {},
            performance_metrics=db_version.performance_metrics or {}
        )
        
        return ModelVersion(
            id=db_version.id,
            model_id=db_version.model_id,
            version=db_version.version,
            status=db_version.status,
            artifact_path=db_version.artifact_path,
            metadata=metadata,
            created_at=db_version.created_at,
            updated_at=db_version.updated_at
        )