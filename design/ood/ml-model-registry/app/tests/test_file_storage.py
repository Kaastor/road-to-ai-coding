"""Tests for file storage functionality."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from io import BytesIO

from app.infrastructure.storage.file_storage import (
    LocalFileStorage, 
    ModelFormat, 
    FileStorageError,
    FileNotFoundError
)


@pytest.fixture
def temp_storage():
    """Create a temporary file storage instance."""
    with TemporaryDirectory() as temp_dir:
        storage = LocalFileStorage(Path(temp_dir))
        yield storage


class TestLocalFileStorage:
    """Test cases for LocalFileStorage."""

    async def test_store_and_retrieve_file(self, temp_storage):
        """Test storing and retrieving a file."""
        model_id = uuid4()
        version = "1.0.0"
        format = ModelFormat.PICKLE
        content = b"test model content"
        
        # Store file
        file_obj = BytesIO(content)
        artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
        
        assert artifact_path is not None
        assert artifact_path.endswith(".pickle")
        
        # Retrieve file
        retrieved_file = await temp_storage.retrieve_file(artifact_path)
        retrieved_content = retrieved_file.read()
        retrieved_file.close()
        
        assert retrieved_content == content

    async def test_file_exists(self, temp_storage):
        """Test checking if a file exists."""
        model_id = uuid4()
        version = "1.0.0"
        format = ModelFormat.JOBLIB
        content = b"test content"
        
        # File should not exist initially
        artifact_path = f"{model_id}/1.0.0.joblib"
        exists = await temp_storage.file_exists(artifact_path)
        assert not exists
        
        # Store file
        file_obj = BytesIO(content)
        artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
        
        # File should exist now
        exists = await temp_storage.file_exists(artifact_path)
        assert exists

    async def test_get_file_size(self, temp_storage):
        """Test getting file size."""
        model_id = uuid4()
        version = "2.0.0"
        format = ModelFormat.ONNX
        content = b"test model content with more data"
        
        # Store file
        file_obj = BytesIO(content)
        artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
        
        # Get file size
        size = await temp_storage.get_file_size(artifact_path)
        assert size == len(content)

    async def test_delete_file(self, temp_storage):
        """Test deleting a file."""
        model_id = uuid4()
        version = "1.0.0"
        format = ModelFormat.H5
        content = b"test content"
        
        # Store file
        file_obj = BytesIO(content)
        artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
        
        # Verify file exists
        exists = await temp_storage.file_exists(artifact_path)
        assert exists
        
        # Delete file
        deleted = await temp_storage.delete_file(artifact_path)
        assert deleted
        
        # Verify file no longer exists
        exists = await temp_storage.file_exists(artifact_path)
        assert not exists
        
        # Trying to delete again should return False
        deleted_again = await temp_storage.delete_file(artifact_path)
        assert not deleted_again

    async def test_retrieve_nonexistent_file(self, temp_storage):
        """Test retrieving a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            await temp_storage.retrieve_file("nonexistent/file.pickle")

    async def test_get_size_nonexistent_file(self, temp_storage):
        """Test getting size of a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            await temp_storage.get_file_size("nonexistent/file.pickle")

    async def test_different_model_formats(self, temp_storage):
        """Test storing files with different formats."""
        model_id = uuid4()
        test_cases = [
            (ModelFormat.PICKLE, "1.0.0", b"pickle content"),
            (ModelFormat.JOBLIB, "1.1.0", b"joblib content"),
            (ModelFormat.ONNX, "1.2.0", b"onnx content"),
            (ModelFormat.H5, "1.3.0", b"h5 content"),
            (ModelFormat.PYTORCH, "1.4.0", b"pytorch content"),
            (ModelFormat.TENSORFLOW, "1.5.0", b"tensorflow content"),
        ]
        
        for format, version, content in test_cases:
            file_obj = BytesIO(content)
            artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
            
            # Verify file path contains correct extension
            assert artifact_path.endswith(f".{format.value}")
            
            # Verify content
            retrieved_file = await temp_storage.retrieve_file(artifact_path)
            retrieved_content = retrieved_file.read()
            retrieved_file.close()
            
            assert retrieved_content == content

    async def test_multiple_versions_same_model(self, temp_storage):
        """Test storing multiple versions of the same model."""
        model_id = uuid4()
        format = ModelFormat.PICKLE
        
        versions_and_content = [
            ("1.0.0", b"version 1 content"),
            ("1.1.0", b"version 1.1 content"),
            ("2.0.0", b"version 2 content"),
        ]
        
        stored_paths = []
        
        for version, content in versions_and_content:
            file_obj = BytesIO(content)
            artifact_path = await temp_storage.store_file(file_obj, model_id, version, format)
            stored_paths.append((artifact_path, content))
        
        # Verify all files exist and have correct content
        for artifact_path, expected_content in stored_paths:
            retrieved_file = await temp_storage.retrieve_file(artifact_path)
            retrieved_content = retrieved_file.read()
            retrieved_file.close()
            
            assert retrieved_content == expected_content