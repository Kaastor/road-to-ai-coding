"""Tests for the mock embedding service."""

import pytest
import numpy as np
from app.services.mock_embedding_service import MockEmbeddingService


class TestMockEmbeddingService:
    """Test cases for MockEmbeddingService."""
    
    @pytest.fixture
    def embedding_service(self):
        """Create a mock embedding service for testing."""
        return MockEmbeddingService(dimension=384)
    
    def test_init(self):
        """Test service initialization."""
        service = MockEmbeddingService(model_name="test-mock", dimension=256)
        assert service.model_name == "test-mock"
        assert service.dimension == 256
    
    def test_embed_single_text(self, embedding_service):
        """Test embedding a single text."""
        text = "This is a test document."
        embedding = embedding_service.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1  # 1D array
        assert embedding.shape[0] == 384  # Correct dimension
        
        # Test that embedding is normalized
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6  # Should be unit vector
    
    def test_embed_multiple_texts(self, embedding_service):
        """Test embedding multiple texts."""
        texts = [
            "This is the first document.",
            "Here is another document.",
            "And a third one."
        ]
        embeddings = embedding_service.embed_texts(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] == 384
        
        # Test that all embeddings are normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert all(abs(norm - 1.0) < 1e-6 for norm in norms)
    
    def test_embed_empty_list(self, embedding_service):
        """Test embedding empty list returns empty array."""
        embeddings = embedding_service.embed_texts([])
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.size == 0
    
    def test_get_embedding_dimension(self, embedding_service):
        """Test getting embedding dimension."""
        dimension = embedding_service.get_embedding_dimension()
        assert isinstance(dimension, int)
        assert dimension == 384
        
        # Should match actual embedding dimension
        test_embedding = embedding_service.embed_text("test")
        assert dimension == test_embedding.shape[0]
    
    def test_deterministic_embeddings(self, embedding_service):
        """Test that same text produces same embedding."""
        text = "Deterministic test text"
        embedding1 = embedding_service.embed_text(text)
        embedding2 = embedding_service.embed_text(text)
        
        np.testing.assert_array_equal(embedding1, embedding2)
    
    def test_different_texts_different_embeddings(self, embedding_service):
        """Test that different texts produce different embeddings."""
        text1 = "First unique text"
        text2 = "Second different text"
        
        embedding1 = embedding_service.embed_text(text1)
        embedding2 = embedding_service.embed_text(text2)
        
        # Embeddings should not be identical
        assert not np.array_equal(embedding1, embedding2)
    
    def test_custom_dimension(self):
        """Test creating service with custom dimension."""
        service = MockEmbeddingService(dimension=256)
        embedding = service.embed_text("test text")
        
        assert embedding.shape[0] == 256
        assert service.get_embedding_dimension() == 256