"""File storage abstraction and implementations for model artifacts."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import UUID
import shutil
import os
from enum import Enum


class ModelFormat(str, Enum):
    """Supported model artifact formats."""
    PICKLE = "pickle"
    JOBLIB = "joblib"
    ONNX = "onnx"
    H5 = "h5"
    PYTORCH = "pt"
    TENSORFLOW = "pb"


class FileStorageError(Exception):
    """Base exception for file storage operations."""
    pass


class FileNotFoundError(FileStorageError):
    """Raised when a file is not found in storage."""
    pass


class StorageError(FileStorageError):
    """Raised when storage operation fails."""
    pass


class FileStorage(ABC):
    """Abstract base class for file storage operations."""

    @abstractmethod
    async def store_file(
        self, 
        file: BinaryIO, 
        model_id: UUID, 
        version: str, 
        format: ModelFormat
    ) -> str:
        """
        Store a model artifact file.
        
        Args:
            file: Binary file object to store
            model_id: ID of the model
            version: Version string
            format: Format of the model file
            
        Returns:
            str: Path or identifier of the stored file
            
        Raises:
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def retrieve_file(self, artifact_path: str) -> BinaryIO:
        """
        Retrieve a model artifact file.
        
        Args:
            artifact_path: Path or identifier of the file
            
        Returns:
            BinaryIO: Binary file object
            
        Raises:
            FileNotFoundError: If file is not found
            StorageError: If retrieval operation fails
        """
        pass

    @abstractmethod
    async def delete_file(self, artifact_path: str) -> bool:
        """
        Delete a model artifact file.
        
        Args:
            artifact_path: Path or identifier of the file
            
        Returns:
            bool: True if file was deleted, False if not found
            
        Raises:
            StorageError: If deletion operation fails
        """
        pass

    @abstractmethod
    async def file_exists(self, artifact_path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            artifact_path: Path or identifier of the file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_file_size(self, artifact_path: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            artifact_path: Path or identifier of the file
            
        Returns:
            int: File size in bytes
            
        Raises:
            FileNotFoundError: If file is not found
        """
        pass


class LocalFileStorage(FileStorage):
    """Local filesystem implementation of file storage."""

    def __init__(self, base_path: Path):
        """
        Initialize local file storage.
        
        Args:
            base_path: Base directory for storing model artifacts
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, model_id: UUID, version: str, format: ModelFormat) -> Path:
        """Generate file path for a model artifact."""
        model_dir = self.base_path / str(model_id)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{version}.{format.value}"
        return model_dir / filename

    def _get_absolute_path(self, artifact_path: str) -> Path:
        """Convert artifact path to absolute filesystem path."""
        if artifact_path.startswith('/'):
            return Path(artifact_path)
        return self.base_path / artifact_path

    async def store_file(
        self, 
        file: BinaryIO, 
        model_id: UUID, 
        version: str, 
        format: ModelFormat
    ) -> str:
        """Store a model artifact file locally."""
        try:
            file_path = self._get_file_path(model_id, version, format)
            
            # Write file content
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file, f)
            
            # Return relative path from base_path
            return str(file_path.relative_to(self.base_path))
            
        except Exception as e:
            raise StorageError(f"Failed to store file: {str(e)}") from e

    async def retrieve_file(self, artifact_path: str) -> BinaryIO:
        """Retrieve a model artifact file."""
        try:
            file_path = self._get_absolute_path(artifact_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {artifact_path}")
            
            return open(file_path, 'rb')
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve file: {str(e)}") from e

    async def delete_file(self, artifact_path: str) -> bool:
        """Delete a model artifact file."""
        try:
            file_path = self._get_absolute_path(artifact_path)
            
            if file_path.exists():
                os.remove(file_path)
                
                # Also remove empty parent directories
                try:
                    file_path.parent.rmdir()
                except OSError:
                    # Directory not empty or other issue, ignore
                    pass
                    
                return True
            
            return False
            
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}") from e

    async def file_exists(self, artifact_path: str) -> bool:
        """Check if a file exists."""
        try:
            file_path = self._get_absolute_path(artifact_path)
            return file_path.exists()
        except Exception:
            return False

    async def get_file_size(self, artifact_path: str) -> int:
        """Get file size in bytes."""
        try:
            file_path = self._get_absolute_path(artifact_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {artifact_path}")
            
            return file_path.stat().st_size
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to get file size: {str(e)}") from e