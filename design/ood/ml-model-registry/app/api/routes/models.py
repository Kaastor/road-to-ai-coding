from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.domain.models.schemas import (
    CreateModelRequest,
    CreateModelVersionRequest,
    UpdateModelStatusRequest,
    ModelResponse,
    ModelVersionResponse
)
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

router = APIRouter(prefix="/models", tags=["models"])


def get_model_service(db: Session = Depends(get_db)) -> ModelService:
    """Dependency to get model service."""
    model_repo = SQLAlchemyModelRepository(db)
    version_repo = SQLAlchemyModelVersionRepository(db)
    return ModelService(model_repo, version_repo)


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
    service: ModelService = Depends(get_model_service)
):
    """List all models with pagination."""
    try:
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