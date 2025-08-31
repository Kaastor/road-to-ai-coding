from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.domain.models.schemas import (
    CreateModelRequest,
    CreateModelVersionRequest,
    UpdateModelStatusRequest,
    UpdateModelRequest,
    UpdateModelVersionMetadataRequest,
    FileUploadResponse,
    PromoteModelRequest,
    ModelResponse,
    ModelVersionResponse,
    CreateEvaluationRequest,
    ModelEvaluationSchema,
    ModelComparisonResponse,
    MetricsVisualizationResponse
)
from app.infrastructure.storage.file_storage import ModelFormat
from app.domain.models.mappers import model_to_response, model_version_to_response
from app.domain.exceptions.exceptions import (
    ModelNotFoundError,
    ModelVersionNotFoundError,
    DuplicateModelError,
    DuplicateVersionError
)
from app.services.model_service import ModelService
from app.infrastructure.repositories.sqlalchemy_repositories import (
    SQLAlchemyModelRepository,
    SQLAlchemyModelVersionRepository
)
from app.infrastructure.storage.database import get_db
from app.infrastructure.storage.storage_factory import StorageFactory
from app.config import get_settings

router = APIRouter(prefix="/models", tags=["models"])


def get_model_service(db: Session = Depends(get_db)) -> ModelService:
    """Dependency to get model service."""
    model_repo = SQLAlchemyModelRepository(db)
    version_repo = SQLAlchemyModelVersionRepository(db)
    settings = get_settings()
    file_storage = StorageFactory.create_file_storage(settings)
    return ModelService(model_repo, version_repo, file_storage)


@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(
    request: CreateModelRequest,
    service: ModelService = Depends(get_model_service)
):
    """Create a new model."""
    try:
        model = await service.create_model(request)
        return model_to_response(model)
    except DuplicateModelError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[ModelResponse])
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search models by name or description"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    service: ModelService = Depends(get_model_service)
):
    """List all models with pagination and optional search/filtering."""
    try:
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            models = await service.search_models_by_tags(tag_list)
            # Apply pagination to search results
            models = models[skip:skip + limit]
        elif search:
            # For now, delegate search to service layer
            models = await service.search_models(search, skip=skip, limit=limit)
        else:
            models = await service.list_models(skip=skip, limit=limit)
        return [model_to_response(model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: UUID,
    service: ModelService = Depends(get_model_service)
):
    """Get a model by ID."""
    try:
        model = await service.get_model(model_id)
        return model_to_response(model)
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: UUID,
    service: ModelService = Depends(get_model_service)
):
    """Delete a model."""
    try:
        deleted = await service.delete_model(model_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Model not found")
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: UUID,
    request: UpdateModelRequest,
    service: ModelService = Depends(get_model_service)
):
    """Update a model's basic information."""
    try:
        updated_model = await service.update_model(model_id, request)
        return model_to_response(updated_model)
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateModelError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{model_id}/versions", response_model=ModelVersionResponse, status_code=201)
async def create_model_version(
    model_id: UUID,
    request: CreateModelVersionRequest,
    service: ModelService = Depends(get_model_service)
):
    """Create a new version for a model."""
    try:
        version = await service.create_model_version(model_id, request)
        return model_version_to_response(version)
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateVersionError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/versions", response_model=list[ModelVersionResponse])
async def list_model_versions(
    model_id: UUID,
    service: ModelService = Depends(get_model_service)
):
    """List all versions for a model."""
    try:
        versions = await service.list_model_versions(model_id)
        return [model_version_to_response(version) for version in versions]
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/versions/{version}", response_model=ModelVersionResponse)
async def get_model_version(
    model_id: UUID,
    version: str,
    service: ModelService = Depends(get_model_service)
):
    """Get a specific version of a model."""
    try:
        model_version = await service.get_model_version(model_id, version)
        return ModelVersionResponse.from_orm(model_version)
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{model_id}/versions/{version}/status", response_model=ModelVersionResponse)
async def update_version_status(
    model_id: UUID,
    version: str,
    request: UpdateModelStatusRequest,
    service: ModelService = Depends(get_model_service)
):
    """Update the status of a model version."""
    try:
        updated_version = await service.update_version_status(model_id, version, request)
        return ModelVersionResponse.from_orm(updated_version)
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/versions/latest", response_model=Optional[ModelVersionResponse])
async def get_latest_version(
    model_id: UUID,
    service: ModelService = Depends(get_model_service)
):
    """Get the latest version of a model."""
    try:
        latest_version = await service.get_latest_version(model_id)
        if latest_version:
            return model_version_to_response(latest_version)
        return None
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{model_id}/versions/{version}/metadata", response_model=ModelVersionResponse)
async def update_version_metadata(
    model_id: UUID,
    version: str,
    request: UpdateModelVersionMetadataRequest,
    service: ModelService = Depends(get_model_service)
):
    """Update the metadata of a model version."""
    try:
        updated_version = await service.update_version_metadata(model_id, version, request)
        return model_version_to_response(updated_version)
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{model_id}/versions/{version}/artifact", response_model=FileUploadResponse)
async def upload_artifact(
    model_id: UUID,
    version: str,
    file: UploadFile = File(...),
    format: ModelFormat = Form(...),
    service: ModelService = Depends(get_model_service)
):
    """Upload an artifact file for a model version."""
    try:
        # Validate file size
        settings = get_settings()
        content = await file.read()
        if len(content) > settings.max_artifact_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.max_artifact_size_mb}MB"
            )
        
        # Create file-like object
        file_obj = BytesIO(content)
        
        result = await service.upload_artifact(model_id, version, file_obj, format)
        return result
        
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/versions/{version}/artifact")
async def download_artifact(
    model_id: UUID,
    version: str,
    service: ModelService = Depends(get_model_service)
):
    """Download an artifact file for a model version."""
    try:
        file_obj = await service.download_artifact(model_id, version)
        
        return StreamingResponse(
            file_obj,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=model-{version}.artifact"}
        )
        
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{model_id}/versions/{version}/artifact", status_code=204)
async def delete_artifact(
    model_id: UUID,
    version: str,
    service: ModelService = Depends(get_model_service)
):
    """Delete an artifact file for a model version."""
    try:
        deleted = await service.delete_artifact(model_id, version)
        if not deleted:
            raise HTTPException(status_code=404, detail="No artifact found for this model version")
            
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{model_id}/versions/{version}/promote", response_model=ModelVersionResponse)
async def promote_model_version(
    model_id: UUID,
    version: str,
    request: PromoteModelRequest,
    service: ModelService = Depends(get_model_service)
):
    """Promote a model version to a higher status."""
    try:
        updated_version = await service.promote_model_version(model_id, version, request)
        return model_version_to_response(updated_version)
        
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{model_id}/versions/{version}/evaluations", response_model=ModelEvaluationSchema, status_code=201)
async def create_evaluation(
    model_id: UUID,
    version: str,
    request: CreateEvaluationRequest,
    service: ModelService = Depends(get_model_service)
):
    """Create an evaluation for a model version."""
    try:
        evaluation = await service.create_evaluation(model_id, version, request)
        return ModelEvaluationSchema.from_orm(evaluation)
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/versions/{version}/evaluations", response_model=list[ModelEvaluationSchema])
async def get_model_evaluations(
    model_id: UUID,
    version: str,
    service: ModelService = Depends(get_model_service)
):
    """Get all evaluations for a model version."""
    try:
        evaluations = await service.get_model_evaluations(model_id, version)
        return [ModelEvaluationSchema.from_orm(eval) for eval in evaluations]
    except ModelVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/compare/{metric_name}", response_model=ModelComparisonResponse)
async def compare_model_versions(
    model_id: UUID,
    metric_name: str,
    service: ModelService = Depends(get_model_service)
):
    """Compare all versions of a model by a specific metric."""
    try:
        comparison = await service.compare_model_versions_by_metric(model_id, metric_name)
        return comparison
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/metrics/visualization", response_model=MetricsVisualizationResponse)
async def get_metrics_visualization(
    model_id: UUID,
    service: ModelService = Depends(get_model_service)
):
    """Get structured metrics data for visualization."""
    try:
        visualization_data = await service.get_metrics_visualization_data(model_id)
        return visualization_data
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))