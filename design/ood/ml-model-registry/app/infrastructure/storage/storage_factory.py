"""Factory for creating storage instances."""

from pathlib import Path
from app.config import Settings
from app.infrastructure.storage.file_storage import FileStorage, LocalFileStorage


class StorageFactory:
    """Factory for creating file storage instances."""

    @staticmethod
    def create_file_storage(settings: Settings) -> FileStorage:
        """
        Create a file storage instance based on configuration.
        
        Args:
            settings: Application settings
            
        Returns:
            FileStorage: File storage implementation instance
        """
        # For now, we only support local file storage
        # In the future, this could be extended to support cloud storage
        return LocalFileStorage(settings.artifact_storage_path)