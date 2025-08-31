from app.domain.models.model import Model, ModelVersion, ModelMetadata
from app.domain.models.schemas import (
    ModelResponse, 
    ModelVersionResponse, 
    ModelMetadataSchema
)


def model_to_response(model: Model) -> ModelResponse:
    """Convert domain Model to response schema."""
    versions = [model_version_to_response(version) for version in model.versions]
    
    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at,
        versions=versions
    )


def model_version_to_response(version: ModelVersion) -> ModelVersionResponse:
    """Convert domain ModelVersion to response schema."""
    metadata = model_metadata_to_schema(version.metadata)
    
    return ModelVersionResponse(
        id=version.id,
        model_id=version.model_id,
        version=version.version,
        status=version.status,
        artifact_path=version.artifact_path,
        metadata=metadata,
        created_at=version.created_at,
        updated_at=version.updated_at
    )


def model_metadata_to_schema(metadata: ModelMetadata) -> ModelMetadataSchema:
    """Convert domain ModelMetadata to schema."""
    return ModelMetadataSchema(
        author=metadata.author,
        description=metadata.description,
        tags=metadata.tags,
        framework=metadata.framework,
        algorithm=metadata.algorithm,
        dataset_name=metadata.dataset_name,
        hyperparameters=metadata.hyperparameters,
        performance_metrics=metadata.performance_metrics
    )