import pytest
from datetime import datetime
from uuid import uuid4

from app.domain.models.model import Model, ModelVersion, ModelMetadata, ModelStatus


class TestModelMetadata:
    """Test ModelMetadata domain model."""
    
    def test_create_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = ModelMetadata(
            author="test-author",
            description="Test model",
            tags=["ml", "test"],
            framework="scikit-learn",
            algorithm="random-forest",
            dataset_name="test-dataset",
            hyperparameters={"n_estimators": 100},
            performance_metrics={"accuracy": 0.95}
        )
        
        assert metadata.author == "test-author"
        assert metadata.description == "Test model"
        assert metadata.tags == ["ml", "test"]
        assert metadata.framework == "scikit-learn"
        assert metadata.hyperparameters["n_estimators"] == 100
        assert metadata.performance_metrics["accuracy"] == 0.95
    
    def test_empty_author_raises_error(self):
        """Test that empty author raises ValueError."""
        with pytest.raises(ValueError, match="Author cannot be empty"):
            ModelMetadata(author="")


class TestModel:
    """Test Model domain model."""
    
    def test_create_model(self):
        """Test creating a new model."""
        model = Model.create(name="test-model", description="Test description")
        
        assert model.name == "test-model"
        assert model.description == "Test description"
        assert isinstance(model.id, type(uuid4()))
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        assert len(model.versions) == 0
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            Model.create(name="")
    
    def test_add_version(self):
        """Test adding a version to a model."""
        model = Model.create(name="test-model")
        metadata = ModelMetadata(author="test-author")
        version = ModelVersion.create(
            model_id=model.id,
            version="v1.0.0",
            metadata=metadata
        )
        
        model.add_version(version)
        
        assert len(model.versions) == 1
        assert model.versions[0].version == "v1.0.0"
    
    def test_add_duplicate_version_raises_error(self):
        """Test that adding duplicate version raises error."""
        model = Model.create(name="test-model")
        metadata = ModelMetadata(author="test-author")
        version1 = ModelVersion.create(
            model_id=model.id,
            version="v1.0.0",
            metadata=metadata
        )
        version2 = ModelVersion.create(
            model_id=model.id,
            version="v1.0.0",
            metadata=metadata
        )
        
        model.add_version(version1)
        
        with pytest.raises(ValueError, match="Version v1.0.0 already exists"):
            model.add_version(version2)
    
    def test_get_latest_version(self):
        """Test getting the latest version."""
        model = Model.create(name="test-model")
        metadata = ModelMetadata(author="test-author")
        
        version1 = ModelVersion.create(
            model_id=model.id,
            version="v1.0.0",
            metadata=metadata
        )
        model.add_version(version1)
        
        # Add a slight delay to ensure different timestamps
        import time
        time.sleep(0.001)
        
        version2 = ModelVersion.create(
            model_id=model.id,
            version="v2.0.0",
            metadata=metadata
        )
        model.add_version(version2)
        
        latest = model.get_latest_version()
        assert latest.version == "v2.0.0"


class TestModelVersion:
    """Test ModelVersion domain model."""
    
    def test_create_version(self):
        """Test creating a new model version."""
        model_id = uuid4()
        metadata = ModelMetadata(author="test-author")
        
        version = ModelVersion.create(
            model_id=model_id,
            version="v1.0.0",
            metadata=metadata,
            status=ModelStatus.DRAFT
        )
        
        assert version.model_id == model_id
        assert version.version == "v1.0.0"
        assert version.status == ModelStatus.DRAFT
        assert version.metadata.author == "test-author"
        assert isinstance(version.id, type(uuid4()))
        assert isinstance(version.created_at, datetime)
    
    def test_update_status(self):
        """Test updating version status."""
        model_id = uuid4()
        metadata = ModelMetadata(author="test-author")
        
        version = ModelVersion.create(
            model_id=model_id,
            version="v1.0.0",
            metadata=metadata,
            status=ModelStatus.DRAFT
        )
        
        old_updated_at = version.updated_at
        import time
        time.sleep(0.001)  # Ensure different timestamp
        
        version.update_status(ModelStatus.PRODUCTION)
        
        assert version.status == ModelStatus.PRODUCTION
        assert version.updated_at > old_updated_at