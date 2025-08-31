from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Protocol
from uuid import UUID

from app.domain.models.model import Model, ModelVersion

T = TypeVar('T')


class Repository(Generic[T], ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List all entities with pagination."""
        pass


class ModelRepository(Repository[Model]):
    """Repository interface for Model entities."""
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Model]:
        """Get model by name."""
        pass
    
    @abstractmethod
    async def search_by_tags(self, tags: list[str]) -> list[Model]:
        """Search models by tags."""
        pass
    
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[Model]:
        """Search models by name or description."""
        pass


class ModelVersionRepository(Repository[ModelVersion]):
    """Repository interface for ModelVersion entities."""
    
    @abstractmethod
    async def get_by_model_and_version(self, model_id: UUID, version: str) -> Optional[ModelVersion]:
        """Get version by model ID and version string."""
        pass
    
    @abstractmethod
    async def list_by_model(self, model_id: UUID) -> list[ModelVersion]:
        """List all versions for a specific model."""
        pass
    
    @abstractmethod
    async def get_latest_by_model(self, model_id: UUID) -> Optional[ModelVersion]:
        """Get the latest version for a specific model."""
        pass