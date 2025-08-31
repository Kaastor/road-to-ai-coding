from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from app.domain.models.model import ModelStatus


class ModelMetadataSchema(BaseModel):
    """Pydantic schema for ModelMetadata."""
    author: str = Field(..., min_length=1, description="Author of the model")
    description: Optional[str] = Field(None, description="Model description")
    tags: list[str] = Field(default_factory=list, description="Model tags")
    framework: Optional[str] = Field(None, description="ML framework used")
    algorithm: Optional[str] = Field(None, description="Algorithm used")
    dataset_name: Optional[str] = Field(None, description="Training dataset name")
    hyperparameters: dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    performance_metrics: dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    
    @field_validator('author')
    @classmethod
    def author_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Author cannot be empty')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        return [tag.strip() for tag in v if tag.strip()]


class CreateModelVersionRequest(BaseModel):
    """Request schema for creating a new model version."""
    version: str = Field(..., min_length=1, description="Version identifier")
    status: ModelStatus = Field(ModelStatus.DRAFT, description="Version status")
    artifact_path: Optional[str] = Field(None, description="Path to model artifact")
    metadata: ModelMetadataSchema = Field(..., description="Version metadata")
    
    @field_validator('version')
    @classmethod
    def version_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Version cannot be empty')
        return v.strip()


class ModelVersionResponse(BaseModel):
    """Response schema for model version."""
    id: UUID
    model_id: UUID
    version: str
    status: ModelStatus
    artifact_path: Optional[str]
    metadata: ModelMetadataSchema
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class CreateModelRequest(BaseModel):
    """Request schema for creating a new model."""
    name: str = Field(..., min_length=1, description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip()


class ModelResponse(BaseModel):
    """Response schema for model."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    versions: list[ModelVersionResponse] = Field(default_factory=list)
    
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class UpdateModelStatusRequest(BaseModel):
    """Request schema for updating model version status."""
    status: ModelStatus = Field(..., description="New status")


class UpdateModelRequest(BaseModel):
    """Request schema for updating a model."""
    name: Optional[str] = Field(None, min_length=1, description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip() if v is not None else v


class UpdateModelVersionMetadataRequest(BaseModel):
    """Request schema for updating model version metadata."""
    metadata: ModelMetadataSchema = Field(..., description="Updated metadata")