import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, VARCHAR
import uuid

from app.domain.models.model import ModelStatus
from .database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = VARCHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(VARCHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class JSONType(TypeDecorator):
    """JSON type that handles serialization/deserialization."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class ModelTable(Base):
    """SQLAlchemy model for Model entity."""
    __tablename__ = "models"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("ModelVersionTable", back_populates="model", cascade="all, delete-orphan")


class ModelVersionTable(Base):
    """SQLAlchemy model for ModelVersion entity."""
    __tablename__ = "model_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID(), ForeignKey("models.id"), nullable=False, index=True)
    version = Column(String(100), nullable=False, index=True)
    status = Column(Enum(ModelStatus), nullable=False, default=ModelStatus.DRAFT, index=True)
    artifact_path = Column(Text, nullable=True)
    
    # Metadata fields
    author = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSONType, nullable=False, default=list)
    framework = Column(String(100), nullable=True)
    algorithm = Column(String(100), nullable=True)
    dataset_name = Column(String(255), nullable=True)
    hyperparameters = Column(JSONType, nullable=False, default=dict)
    performance_metrics = Column(JSONType, nullable=False, default=dict)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    model = relationship("ModelTable", back_populates="versions")
    evaluations = relationship("ModelEvaluationTable", back_populates="model_version", cascade="all, delete-orphan")


class ModelEvaluationTable(Base):
    """SQLAlchemy model for ModelEvaluation entity."""
    __tablename__ = "model_evaluations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    model_version_id = Column(GUID(), ForeignKey("model_versions.id"), nullable=False, index=True)
    evaluation_name = Column(String(255), nullable=False, index=True)
    dataset_name = Column(String(255), nullable=False)
    metrics = Column(JSONType, nullable=False)
    evaluation_metadata = Column(JSONType, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    model_version = relationship("ModelVersionTable", back_populates="evaluations")