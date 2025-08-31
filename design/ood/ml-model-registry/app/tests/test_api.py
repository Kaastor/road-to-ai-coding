import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.infrastructure.storage.database import get_db, Base


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    
    # Create test engine and session
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


class TestModelAPI:
    """Test Model API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_model(self, client):
        """Test creating a new model."""
        model_data = {
            "name": "test-model",
            "description": "Test model description"
        }
        
        response = client.post("/api/v1/models/", json=model_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "test-model"
        assert data["description"] == "Test model description"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_duplicate_model(self, client):
        """Test creating duplicate model returns 409."""
        model_data = {
            "name": "duplicate-model",
            "description": "Test model"
        }
        
        # Create first model
        response1 = client.post("/api/v1/models/", json=model_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/models/", json=model_data)
        assert response2.status_code == 409
    
    def test_list_models(self, client):
        """Test listing models."""
        # Create a model first
        model_data = {
            "name": "list-test-model",
            "description": "Test model for listing"
        }
        client.post("/api/v1/models/", json=model_data)
        
        response = client.get("/api/v1/models/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_model(self, client):
        """Test getting a specific model."""
        # Create a model first
        model_data = {
            "name": "get-test-model",
            "description": "Test model for getting"
        }
        create_response = client.post("/api/v1/models/", json=model_data)
        model_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/models/{model_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == model_id
        assert data["name"] == "get-test-model"
    
    def test_get_nonexistent_model(self, client):
        """Test getting nonexistent model returns 404."""
        from uuid import uuid4
        fake_id = str(uuid4())
        
        response = client.get(f"/api/v1/models/{fake_id}")
        assert response.status_code == 404
    
    def test_create_model_version(self, client):
        """Test creating a model version."""
        # Create a model first
        model_data = {
            "name": "version-test-model",
            "description": "Test model for versions"
        }
        create_response = client.post("/api/v1/models/", json=model_data)
        model_id = create_response.json()["id"]
        
        # Create a version
        version_data = {
            "version": "v1.0.0",
            "status": "draft",
            "metadata": {
                "author": "test-author",
                "description": "First version",
                "tags": ["ml", "test"],
                "framework": "scikit-learn",
                "hyperparameters": {"n_estimators": 100},
                "performance_metrics": {"accuracy": 0.95}
            }
        }
        
        response = client.post(f"/api/v1/models/{model_id}/versions", json=version_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["status"] == "draft"
        assert data["model_id"] == model_id
        assert data["metadata"]["author"] == "test-author"
    
    def test_list_model_versions(self, client):
        """Test listing model versions."""
        # Create model and version
        model_data = {"name": "version-list-model"}
        create_response = client.post("/api/v1/models/", json=model_data)
        model_id = create_response.json()["id"]
        
        version_data = {
            "version": "v1.0.0",
            "metadata": {"author": "test-author"}
        }
        client.post(f"/api/v1/models/{model_id}/versions", json=version_data)
        
        response = client.get(f"/api/v1/models/{model_id}/versions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["version"] == "v1.0.0"
    
    def test_search_models(self, client):
        """Test searching models."""
        # Create a couple of models
        model_data_1 = {"name": "search-test-model", "description": "A model for testing search"}
        model_data_2 = {"name": "another-model", "description": "Another model with different content"}
        
        client.post("/api/v1/models/", json=model_data_1)
        client.post("/api/v1/models/", json=model_data_2)
        
        # Search by name
        response = client.get("/api/v1/models/?search=search-test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(model["name"] == "search-test-model" for model in data)
        
        # Search by description
        response = client.get("/api/v1/models/?search=testing search")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_update_model_metadata(self, client):
        """Test updating model metadata."""
        # Create model and version
        model_data = {"name": "update-test-model", "description": "Test model for updating"}
        create_response = client.post("/api/v1/models/", json=model_data)
        model_id = create_response.json()["id"]
        
        version_data = {
            "version": "v1.0.0",
            "metadata": {"author": "original-author", "framework": "scikit-learn"}
        }
        client.post(f"/api/v1/models/{model_id}/versions", json=version_data)
        
        # Update model basic info
        update_data = {"name": "updated-model-name", "description": "Updated description"}
        response = client.patch(f"/api/v1/models/{model_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "updated-model-name"
        assert data["description"] == "Updated description"
        
        # Update version metadata
        metadata_update = {
            "metadata": {
                "author": "updated-author",
                "framework": "pytorch", 
                "tags": ["updated", "test"],
                "performance_metrics": {"accuracy": 0.98}
            }
        }
        response = client.patch(f"/api/v1/models/{model_id}/versions/v1.0.0/metadata", json=metadata_update)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["author"] == "updated-author"
        assert data["metadata"]["framework"] == "pytorch"
        assert "updated" in data["metadata"]["tags"]
        assert data["metadata"]["performance_metrics"]["accuracy"] == 0.98