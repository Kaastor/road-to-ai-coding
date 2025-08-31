"""Tests for artifact upload/download operations."""

import pytest
from io import BytesIO
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.domain.models.model import Model, ModelVersion, ModelStatus, ModelMetadata
from app.domain.models.schemas import FileUploadResponse
from app.domain.exceptions.exceptions import ModelVersionNotFoundError
from app.infrastructure.storage.file_storage import ModelFormat, FileStorageError
from app.services.model_service import ModelService


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    model_repo = Mock()
    version_repo = Mock()
    return model_repo, version_repo


@pytest.fixture
def mock_file_storage():
    """Create mock file storage."""
    storage = Mock()
    storage.store_file = AsyncMock()
    storage.retrieve_file = AsyncMock()
    storage.delete_file = AsyncMock()
    storage.get_file_size = AsyncMock()
    return storage


@pytest.fixture
def mock_audit_logger():
    """Create mock audit logger."""
    logger = Mock()
    logger.log_version_operation = AsyncMock()
    return logger


@pytest.fixture
def model_service(mock_repositories, mock_file_storage, mock_audit_logger):
    """Create model service with mocks."""
    model_repo, version_repo = mock_repositories
    return ModelService(model_repo, version_repo, mock_file_storage, mock_audit_logger)


@pytest.fixture
def sample_model():
    """Create a sample model for testing."""
    return Model.create("test-model", "Test model description")


@pytest.fixture
def sample_metadata():
    """Create sample metadata for testing."""
    return ModelMetadata(
        author="test-author",
        description="Test version",
        tags=["test"],
        framework="sklearn"
    )


@pytest.fixture
def sample_model_version(sample_model, sample_metadata):
    """Create a sample model version for testing."""
    return ModelVersion.create(
        model_id=sample_model.id,
        version="1.0.0",
        metadata=sample_metadata,
        status=ModelStatus.DRAFT
    )


class TestArtifactUpload:
    """Test cases for artifact upload functionality."""

    async def test_upload_artifact_success(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage, 
        mock_audit_logger,
        sample_model, 
        sample_model_version
    ):
        """Test successful artifact upload."""
        model_repo, version_repo = mock_repositories
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        version_repo.update = AsyncMock(return_value=sample_model_version)
        
        # Mock file storage responses
        artifact_path = f"{sample_model.id}/1.0.0.pickle"
        mock_file_storage.store_file.return_value = artifact_path
        mock_file_storage.get_file_size.return_value = 1024
        
        # Create test file
        file_content = b"test model binary data"
        file_obj = BytesIO(file_content)
        
        # Upload artifact
        result = await model_service.upload_artifact(
            sample_model.id, "1.0.0", file_obj, ModelFormat.PICKLE
        )
        
        # Verify result
        assert isinstance(result, FileUploadResponse)
        assert result.artifact_path == artifact_path
        assert result.size == 1024
        assert result.format == ModelFormat.PICKLE
        assert isinstance(result.uploaded_at, datetime)
        
        # Verify storage was called
        mock_file_storage.store_file.assert_called_once_with(
            file_obj, sample_model.id, "1.0.0", ModelFormat.PICKLE
        )
        
        # Verify version was updated
        version_repo.update.assert_called_once()
        
        # Verify audit logging
        mock_audit_logger.log_version_operation.assert_called_once()

    async def test_upload_artifact_version_not_found(
        self, 
        model_service, 
        mock_repositories, 
        sample_model
    ):
        """Test upload when model version doesn't exist."""
        model_repo, version_repo = mock_repositories
        
        # Mock repository to return None (version not found)
        version_repo.get_by_model_and_version = AsyncMock(return_value=None)
        
        # Create test file
        file_obj = BytesIO(b"test data")
        
        # Try to upload artifact
        with pytest.raises(ModelVersionNotFoundError):
            await model_service.upload_artifact(
                sample_model.id, "nonexistent", file_obj, ModelFormat.PICKLE
            )

    async def test_upload_artifact_storage_error(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage,
        sample_model, 
        sample_model_version
    ):
        """Test upload when storage operation fails."""
        model_repo, version_repo = mock_repositories
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Mock storage to raise error
        mock_file_storage.store_file.side_effect = FileStorageError("Storage failed")
        
        # Create test file
        file_obj = BytesIO(b"test data")
        
        # Try to upload artifact
        with pytest.raises(ValueError, match="Failed to upload artifact"):
            await model_service.upload_artifact(
                sample_model.id, "1.0.0", file_obj, ModelFormat.PICKLE
            )

    async def test_upload_without_file_storage(
        self, 
        mock_repositories,
        sample_model
    ):
        """Test upload when file storage is not configured."""
        model_repo, version_repo = mock_repositories
        service = ModelService(model_repo, version_repo, None)  # No file storage
        
        file_obj = BytesIO(b"test data")
        
        with pytest.raises(ValueError, match="File storage not configured"):
            await service.upload_artifact(
                sample_model.id, "1.0.0", file_obj, ModelFormat.PICKLE
            )


class TestArtifactDownload:
    """Test cases for artifact download functionality."""

    async def test_download_artifact_success(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage, 
        mock_audit_logger,
        sample_model, 
        sample_model_version
    ):
        """Test successful artifact download."""
        model_repo, version_repo = mock_repositories
        
        # Set artifact path on version
        artifact_path = f"{sample_model.id}/1.0.0.pickle"
        sample_model_version.artifact_path = artifact_path
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Mock file storage response
        file_content = b"test model binary data"
        mock_file_obj = BytesIO(file_content)
        mock_file_storage.retrieve_file.return_value = mock_file_obj
        
        # Download artifact
        result = await model_service.download_artifact(sample_model.id, "1.0.0")
        
        # Verify result
        assert result == mock_file_obj
        
        # Verify storage was called
        mock_file_storage.retrieve_file.assert_called_once_with(artifact_path)
        
        # Verify audit logging
        mock_audit_logger.log_version_operation.assert_called_once()

    async def test_download_artifact_no_artifact(
        self, 
        model_service, 
        mock_repositories, 
        sample_model, 
        sample_model_version
    ):
        """Test download when no artifact is available."""
        model_repo, version_repo = mock_repositories
        
        # Version has no artifact path
        sample_model_version.artifact_path = None
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Try to download artifact
        with pytest.raises(ValueError, match="No artifact available"):
            await model_service.download_artifact(sample_model.id, "1.0.0")

    async def test_download_artifact_storage_error(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage,
        sample_model, 
        sample_model_version
    ):
        """Test download when storage operation fails."""
        model_repo, version_repo = mock_repositories
        
        # Set artifact path on version
        artifact_path = f"{sample_model.id}/1.0.0.pickle"
        sample_model_version.artifact_path = artifact_path
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Mock storage to raise error
        mock_file_storage.retrieve_file.side_effect = FileStorageError("Retrieval failed")
        
        # Try to download artifact
        with pytest.raises(ValueError, match="Failed to download artifact"):
            await model_service.download_artifact(sample_model.id, "1.0.0")


class TestArtifactDeletion:
    """Test cases for artifact deletion functionality."""

    async def test_delete_artifact_success(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage, 
        mock_audit_logger,
        sample_model, 
        sample_model_version
    ):
        """Test successful artifact deletion."""
        model_repo, version_repo = mock_repositories
        
        # Set artifact path on version
        artifact_path = f"{sample_model.id}/1.0.0.pickle"
        sample_model_version.artifact_path = artifact_path
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        version_repo.update = AsyncMock(return_value=sample_model_version)
        
        # Mock storage response
        mock_file_storage.delete_file.return_value = True
        
        # Delete artifact
        result = await model_service.delete_artifact(sample_model.id, "1.0.0")
        
        # Verify result
        assert result is True
        
        # Verify storage was called
        mock_file_storage.delete_file.assert_called_once_with(artifact_path)
        
        # Verify version was updated (artifact_path set to None)
        version_repo.update.assert_called_once()
        assert sample_model_version.artifact_path is None
        
        # Verify audit logging
        mock_audit_logger.log_version_operation.assert_called_once()

    async def test_delete_artifact_no_artifact(
        self, 
        model_service, 
        mock_repositories, 
        sample_model, 
        sample_model_version
    ):
        """Test delete when no artifact is available."""
        model_repo, version_repo = mock_repositories
        
        # Version has no artifact path
        sample_model_version.artifact_path = None
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Try to delete artifact
        result = await model_service.delete_artifact(sample_model.id, "1.0.0")
        
        # Should return False since no artifact exists
        assert result is False

    async def test_delete_artifact_file_not_found(
        self, 
        model_service, 
        mock_repositories, 
        mock_file_storage,
        sample_model, 
        sample_model_version
    ):
        """Test delete when file is not found in storage."""
        model_repo, version_repo = mock_repositories
        
        # Set artifact path on version
        artifact_path = f"{sample_model.id}/1.0.0.pickle"
        sample_model_version.artifact_path = artifact_path
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=sample_model_version)
        
        # Mock storage to return False (file not found)
        mock_file_storage.delete_file.return_value = False
        
        # Delete artifact
        result = await model_service.delete_artifact(sample_model.id, "1.0.0")
        
        # Should return False since file was not found
        assert result is False