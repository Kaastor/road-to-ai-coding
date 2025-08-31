"""Tests for model lifecycle and promotion functionality."""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock

from app.domain.models.model import Model, ModelVersion, ModelStatus, ModelMetadata
from app.domain.models.schemas import PromoteModelRequest
from app.domain.exceptions.exceptions import ModelVersionNotFoundError
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
    return Mock()


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


class TestModelPromotion:
    """Test cases for model promotion functionality."""

    async def test_promote_draft_to_staging(self, model_service, mock_repositories, sample_model, sample_metadata):
        """Test promoting a model from draft to staging."""
        model_repo, version_repo = mock_repositories
        
        # Create a draft version
        model_version = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.DRAFT
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=model_version)
        version_repo.update = AsyncMock(return_value=model_version)
        
        # Create promotion request
        request = PromoteModelRequest(to_status=ModelStatus.STAGING)
        
        # Promote the version
        result = await model_service.promote_model_version(
            sample_model.id, "1.0.0", request
        )
        
        # Verify the promotion
        assert result.status == ModelStatus.STAGING
        version_repo.update.assert_called_once()

    async def test_promote_staging_to_production(self, model_service, mock_repositories, sample_model, sample_metadata):
        """Test promoting a model from staging to production."""
        model_repo, version_repo = mock_repositories
        
        # Create a staging version
        model_version = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.STAGING
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=model_version)
        version_repo.get_by_model_and_status = AsyncMock(return_value=None)  # No existing production version
        version_repo.update = AsyncMock(return_value=model_version)
        
        # Create promotion request
        request = PromoteModelRequest(to_status=ModelStatus.PRODUCTION)
        
        # Promote the version
        result = await model_service.promote_model_version(
            sample_model.id, "1.0.0", request
        )
        
        # Verify the promotion
        assert result.status == ModelStatus.PRODUCTION
        version_repo.update.assert_called_once()

    async def test_promote_production_to_archived(self, model_service, mock_repositories, sample_model, sample_metadata):
        """Test promoting a model from production to archived."""
        model_repo, version_repo = mock_repositories
        
        # Create a production version
        model_version = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.PRODUCTION
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=model_version)
        version_repo.update = AsyncMock(return_value=model_version)
        
        # Create promotion request
        request = PromoteModelRequest(to_status=ModelStatus.ARCHIVED)
        
        # Promote the version
        result = await model_service.promote_model_version(
            sample_model.id, "1.0.0", request
        )
        
        # Verify the promotion
        assert result.status == ModelStatus.ARCHIVED
        version_repo.update.assert_called_once()

    async def test_invalid_promotion_path(self, model_service, mock_repositories, sample_model, sample_metadata):
        """Test invalid promotion path raises error."""
        model_repo, version_repo = mock_repositories
        
        # Create a draft version
        model_version = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.DRAFT
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=model_version)
        
        # Try to promote directly from draft to production (invalid)
        request = PromoteModelRequest(to_status=ModelStatus.PRODUCTION)
        
        with pytest.raises(ValueError, match="Cannot promote from draft to production"):
            await model_service.promote_model_version(
                sample_model.id, "1.0.0", request
            )

    async def test_prevent_multiple_production_versions(self, model_service, mock_repositories, sample_model, sample_metadata):
        """Test that only one version can be in production."""
        model_repo, version_repo = mock_repositories
        
        # Create a staging version
        staging_version = ModelVersion.create(
            model_id=sample_model.id,
            version="2.0.0",
            metadata=sample_metadata,
            status=ModelStatus.STAGING
        )
        
        # Create an existing production version
        existing_production = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.PRODUCTION
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=staging_version)
        version_repo.get_by_model_and_status = AsyncMock(return_value=existing_production)
        
        # Try to promote to production when another version is already in production
        request = PromoteModelRequest(to_status=ModelStatus.PRODUCTION)
        
        with pytest.raises(ValueError, match="Another version .* is already in production"):
            await model_service.promote_model_version(
                sample_model.id, "2.0.0", request
            )

    async def test_promote_nonexistent_version(self, model_service, mock_repositories, sample_model):
        """Test promoting a version that doesn't exist."""
        model_repo, version_repo = mock_repositories
        
        # Mock repository to return None (version not found)
        version_repo.get_by_model_and_version = AsyncMock(return_value=None)
        
        # Try to promote non-existent version
        request = PromoteModelRequest(to_status=ModelStatus.STAGING)
        
        with pytest.raises(ModelVersionNotFoundError):
            await model_service.promote_model_version(
                sample_model.id, "nonexistent", request
            )

    async def test_promotion_with_reason(self, model_service, mock_repositories, mock_audit_logger, sample_model, sample_metadata):
        """Test promotion with a reason is properly logged."""
        model_repo, version_repo = mock_repositories
        
        # Create a draft version
        model_version = ModelVersion.create(
            model_id=sample_model.id,
            version="1.0.0",
            metadata=sample_metadata,
            status=ModelStatus.DRAFT
        )
        
        # Mock repository responses
        version_repo.get_by_model_and_version = AsyncMock(return_value=model_version)
        version_repo.update = AsyncMock(return_value=model_version)
        
        # Create promotion request with reason
        reason = "Model passed all validation tests"
        request = PromoteModelRequest(to_status=ModelStatus.STAGING, reason=reason)
        
        # Promote the version
        await model_service.promote_model_version(
            sample_model.id, "1.0.0", request
        )
        
        # Verify audit logging was called with reason
        mock_audit_logger.log_version_operation.assert_called_once()
        call_args = mock_audit_logger.log_version_operation.call_args
        
        assert call_args[1]['details']['reason'] == reason