from uuid import UUID


class ModelRegistryException(Exception):
    """Base exception for model registry operations."""
    pass


class ModelNotFoundError(ModelRegistryException):
    """Raised when a model is not found."""
    
    def __init__(self, model_id: UUID):
        self.model_id = model_id
        super().__init__(f"Model with id {model_id} not found")


class ModelVersionNotFoundError(ModelRegistryException):
    """Raised when a model version is not found."""
    
    def __init__(self, model_id: UUID, version: str):
        self.model_id = model_id
        self.version = version
        super().__init__(f"Version {version} not found for model {model_id}")


class DuplicateModelError(ModelRegistryException):
    """Raised when trying to create a model that already exists."""
    
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Model with name '{name}' already exists")


class DuplicateVersionError(ModelRegistryException):
    """Raised when trying to create a version that already exists."""
    
    def __init__(self, model_id: UUID, version: str):
        self.model_id = model_id
        self.version = version
        super().__init__(f"Version {version} already exists for model {model_id}")


class ValidationError(ModelRegistryException):
    """Raised when validation fails."""
    pass