from typing import Optional
from uuid import UUID

from app.domain.models.model import Model, ModelVersion, ModelStatus
from app.domain.models.schemas import CreateModelRequest, CreateModelVersionRequest, UpdateModelStatusRequest
from app.domain.models.model import ModelMetadata
from app.domain.exceptions.exceptions import (
    ModelNotFoundError, 
    ModelVersionNotFoundError, 
    DuplicateModelError, 
    DuplicateVersionError
)
from app.infrastructure.repositories.base import ModelRepository, ModelVersionRepository


class ModelService:
    """Service layer for model operations."""
    
    def __init__(self, model_repo: ModelRepository, version_repo: ModelVersionRepository):
        self.model_repo = model_repo
        self.version_repo = version_repo
    
    async def create_model(self, request: CreateModelRequest) -> Model:
        """Create a new model."""
        existing_model = await self.model_repo.get_by_name(request.name)
        if existing_model:
            raise DuplicateModelError(request.name)
        
        model = Model.create(name=request.name, description=request.description)
        return await self.model_repo.create(model)
    
    async def get_model(self, model_id: UUID) -> Model:
        """Get a model by ID."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        return model
    
    async def get_model_by_name(self, name: str) -> Optional[Model]:
        """Get a model by name."""
        return await self.model_repo.get_by_name(name)
    
    async def list_models(self, skip: int = 0, limit: int = 100) -> list[Model]:
        """List all models with pagination."""
        return await self.model_repo.list_all(skip=skip, limit=limit)
    
    async def delete_model(self, model_id: UUID) -> bool:
        """Delete a model."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        return await self.model_repo.delete(model_id)
    
    async def create_model_version(
        self, 
        model_id: UUID, 
        request: CreateModelVersionRequest
    ) -> ModelVersion:
        """Create a new version for a model."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        
        existing_version = await self.version_repo.get_by_model_and_version(
            model_id, request.version
        )
        if existing_version:
            raise DuplicateVersionError(model_id, request.version)
        
        metadata = ModelMetadata(
            author=request.metadata.author,
            description=request.metadata.description,
            tags=request.metadata.tags,
            framework=request.metadata.framework,
            algorithm=request.metadata.algorithm,
            dataset_name=request.metadata.dataset_name,
            hyperparameters=request.metadata.hyperparameters,
            performance_metrics=request.metadata.performance_metrics
        )
        
        version = ModelVersion.create(
            model_id=model_id,
            version=request.version,
            metadata=metadata,
            status=request.status,
            artifact_path=request.artifact_path
        )
        
        created_version = await self.version_repo.create(version)
        
        # Update the model's updated_at timestamp
        model.updated_at = created_version.created_at
        await self.model_repo.update(model)
        
        return created_version
    
    async def get_model_version(self, model_id: UUID, version: str) -> ModelVersion:
        """Get a specific version of a model."""
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        return model_version
    
    async def list_model_versions(self, model_id: UUID) -> list[ModelVersion]:
        """List all versions for a model."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        return await self.version_repo.list_by_model(model_id)
    
    async def update_version_status(
        self, 
        model_id: UUID, 
        version: str, 
        request: UpdateModelStatusRequest
    ) -> ModelVersion:
        """Update the status of a model version."""
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        model_version.update_status(request.status)
        return await self.version_repo.update(model_version)
    
    async def get_latest_version(self, model_id: UUID) -> Optional[ModelVersion]:
        """Get the latest version of a model."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        return await self.version_repo.get_latest_by_model(model_id)
    
    async def search_models_by_tags(self, tags: list[str]) -> list[Model]:
        """Search models by tags."""
        return await self.model_repo.search_by_tags(tags)