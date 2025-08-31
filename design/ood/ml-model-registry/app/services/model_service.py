from typing import Optional, BinaryIO
from uuid import UUID
from datetime import datetime

from app.domain.models.model import Model, ModelVersion, ModelStatus
from app.domain.models.schemas import (
    CreateModelRequest, 
    CreateModelVersionRequest, 
    UpdateModelStatusRequest,
    UpdateModelRequest,
    UpdateModelVersionMetadataRequest,
    FileUploadResponse,
    PromoteModelRequest
)
from app.domain.models.model import ModelMetadata
from app.domain.models.audit import AuditLogger, AuditAction
from app.domain.exceptions.exceptions import (
    ModelNotFoundError, 
    ModelVersionNotFoundError, 
    DuplicateModelError, 
    DuplicateVersionError
)
from app.infrastructure.repositories.base import ModelRepository, ModelVersionRepository
from app.infrastructure.storage.file_storage import FileStorage, ModelFormat, FileStorageError


class ModelService:
    """Service layer for model operations."""
    
    def __init__(
        self, 
        model_repo: ModelRepository, 
        version_repo: ModelVersionRepository,
        file_storage: Optional[FileStorage] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        self.model_repo = model_repo
        self.version_repo = version_repo
        self.file_storage = file_storage
        self.audit_logger = audit_logger or AuditLogger()
    
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
    
    async def search_models(self, query: str, skip: int = 0, limit: int = 100) -> list[Model]:
        """Search models by name or description."""
        return await self.model_repo.search(query, skip=skip, limit=limit)
    
    async def update_model(self, model_id: UUID, request: UpdateModelRequest) -> Model:
        """Update a model's basic information."""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundError(model_id)
        
        if request.name is not None:
            existing_model = await self.model_repo.get_by_name(request.name)
            if existing_model and existing_model.id != model_id:
                raise DuplicateModelError(request.name)
            model.name = request.name
            
        if request.description is not None:
            model.description = request.description
        
        model.update_timestamp()
        return await self.model_repo.update(model)
    
    async def update_version_metadata(
        self, 
        model_id: UUID, 
        version: str, 
        request: UpdateModelVersionMetadataRequest
    ) -> ModelVersion:
        """Update model version metadata."""
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        # Update metadata
        model_version.metadata = ModelMetadata(
            author=request.metadata.author,
            description=request.metadata.description,
            tags=request.metadata.tags,
            framework=request.metadata.framework,
            algorithm=request.metadata.algorithm,
            dataset_name=request.metadata.dataset_name,
            hyperparameters=request.metadata.hyperparameters,
            performance_metrics=request.metadata.performance_metrics
        )
        
        model_version.update_timestamp()
        return await self.version_repo.update(model_version)
    
    async def upload_artifact(
        self,
        model_id: UUID,
        version: str,
        file: BinaryIO,
        format: ModelFormat
    ) -> FileUploadResponse:
        """Upload an artifact file for a model version."""
        if not self.file_storage:
            raise ValueError("File storage not configured")
        
        # Verify model version exists
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        try:
            # Store the file
            artifact_path = await self.file_storage.store_file(file, model_id, version, format)
            
            # Update model version with artifact path
            model_version.artifact_path = artifact_path
            model_version.update_timestamp()
            await self.version_repo.update(model_version)
            
            # Get file size
            file_size = await self.file_storage.get_file_size(artifact_path)
            
            # Log the operation
            await self.audit_logger.log_version_operation(
                action=AuditAction.UPLOAD_ARTIFACT,
                version_id=model_version.id,
                details={
                    "model_id": str(model_id),
                    "version": version,
                    "format": format.value,
                    "artifact_path": artifact_path,
                    "file_size": file_size
                }
            )
            
            return FileUploadResponse(
                artifact_path=artifact_path,
                size=file_size,
                format=format,
                uploaded_at=datetime.utcnow()
            )
            
        except FileStorageError as e:
            raise ValueError(f"Failed to upload artifact: {str(e)}")
    
    async def download_artifact(self, model_id: UUID, version: str) -> BinaryIO:
        """Download an artifact file for a model version."""
        if not self.file_storage:
            raise ValueError("File storage not configured")
        
        # Get model version
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        if not model_version.artifact_path:
            raise ValueError("No artifact available for this model version")
        
        try:
            # Log the operation
            await self.audit_logger.log_version_operation(
                action=AuditAction.DOWNLOAD_ARTIFACT,
                version_id=model_version.id,
                details={
                    "model_id": str(model_id),
                    "version": version,
                    "artifact_path": model_version.artifact_path
                }
            )
            
            return await self.file_storage.retrieve_file(model_version.artifact_path)
            
        except FileStorageError as e:
            raise ValueError(f"Failed to download artifact: {str(e)}")
    
    async def delete_artifact(self, model_id: UUID, version: str) -> bool:
        """Delete an artifact file for a model version."""
        if not self.file_storage:
            raise ValueError("File storage not configured")
        
        # Get model version
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        if not model_version.artifact_path:
            return False
        
        try:
            # Delete the file
            deleted = await self.file_storage.delete_file(model_version.artifact_path)
            
            if deleted:
                # Remove artifact path from model version
                artifact_path = model_version.artifact_path
                model_version.artifact_path = None
                model_version.update_timestamp()
                await self.version_repo.update(model_version)
                
                # Log the operation
                await self.audit_logger.log_version_operation(
                    action=AuditAction.DELETE_ARTIFACT,
                    version_id=model_version.id,
                    details={
                        "model_id": str(model_id),
                        "version": version,
                        "artifact_path": artifact_path
                    }
                )
            
            return deleted
            
        except FileStorageError as e:
            raise ValueError(f"Failed to delete artifact: {str(e)}")
    
    async def promote_model_version(
        self,
        model_id: UUID,
        version: str,
        request: PromoteModelRequest
    ) -> ModelVersion:
        """Promote a model version to a higher status."""
        model_version = await self.version_repo.get_by_model_and_version(model_id, version)
        if not model_version:
            raise ModelVersionNotFoundError(model_id, version)
        
        # Validate promotion path
        current_status = model_version.status
        target_status = request.to_status
        
        # Define valid promotion paths
        valid_promotions = {
            ModelStatus.DRAFT: [ModelStatus.STAGING],
            ModelStatus.STAGING: [ModelStatus.PRODUCTION],
            ModelStatus.PRODUCTION: [ModelStatus.ARCHIVED]
        }
        
        if target_status not in valid_promotions.get(current_status, []):
            raise ValueError(
                f"Cannot promote from {current_status.value} to {target_status.value}. "
                f"Valid targets: {[s.value for s in valid_promotions.get(current_status, [])]}"
            )
        
        # If promoting to production, ensure no other version is in production
        if target_status == ModelStatus.PRODUCTION:
            existing_production = await self.version_repo.get_by_model_and_status(
                model_id, ModelStatus.PRODUCTION
            )
            if existing_production and existing_production.id != model_version.id:
                raise ValueError(
                    f"Another version ({existing_production.version}) is already in production. "
                    "Archive it first before promoting a new version."
                )
        
        # Store previous state for audit
        previous_state = {"status": current_status.value}
        new_state = {"status": target_status.value}
        
        # Update status
        model_version.update_status(target_status)
        updated_version = await self.version_repo.update(model_version)
        
        # Log the operation
        await self.audit_logger.log_version_operation(
            action=AuditAction.PROMOTE_MODEL,
            version_id=model_version.id,
            details={
                "model_id": str(model_id),
                "version": version,
                "from_status": current_status.value,
                "to_status": target_status.value,
                "reason": request.reason
            },
            previous_state=previous_state,
            new_state=new_state
        )
        
        return updated_version