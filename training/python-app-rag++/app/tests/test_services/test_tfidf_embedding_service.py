"""Tests for the TF-IDF embedding service."""

import pytest
import numpy as np
from app.services.tfidf_embedding_service import TfidfEmbeddingService


class TestTfidfEmbeddingService:
    """Test cases for TfidfEmbeddingService."""
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return [
            "This is a document about machine learning and artificial intelligence.",
            "Vector embeddings are used for semantic search and similarity matching.",
            "BM25 is a ranking function for information retrieval systems.",
            "Feedback systems help improve search quality over time.",
            "API design is important for building scalable applications."
        ]
    
    def test_init(self):
        """Test service initialization."""
        service = TfidfEmbeddingService(max_features=1000, embedding_dim=256)
        assert service.max_features == 1000
        assert service.embedding_dim == 256
        assert not service.is_fitted()
        assert "tfidf-svd-256d" in service.model_name
    
    def test_fit_and_embed(self, sample_texts):
        """Test fitting model and generating embeddings."""
        service = TfidfEmbeddingService(embedding_dim=128)
        
        # Fit the model
        service.fit(sample_texts)
        assert service.is_fitted()
        
        # Generate embeddings
        embeddings = service.embed_texts(sample_texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] <= 128  # May be less due to SVD
        
        # Check that embeddings are normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert all(abs(norm - 1.0) < 1e-5 for norm in norms)
    
    def test_auto_fit(self, sample_texts):
        """Test that model auto-fits when not previously fitted."""
        service = TfidfEmbeddingService(embedding_dim=64)
        
        # Should auto-fit on first call
        embeddings = service.embed_texts(sample_texts)
        
        assert service.is_fitted()
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] > 0
    
    def test_embed_single_text(self, sample_texts):
        """Test embedding a single text."""
        service = TfidfEmbeddingService()
        service.fit(sample_texts)
        
        text = "This is a test document about search."
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1  # 1D array
        assert embedding.shape[0] > 0
        
        # Should be normalized
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-5
    
    def test_embed_empty_list(self, sample_texts):
        """Test embedding empty list returns empty array."""
        service = TfidfEmbeddingService()
        service.fit(sample_texts)
        
        embeddings = service.embed_texts([])
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.size == 0
    
    def test_fit_empty_texts(self):
        """Test that fitting with empty texts raises error."""
        service = TfidfEmbeddingService()
        
        with pytest.raises(ValueError, match="Cannot fit on empty"):
            service.fit([])
    
    def test_get_embedding_dimension(self, sample_texts):
        """Test getting embedding dimension."""
        service = TfidfEmbeddingService(embedding_dim=200)
        
        # Before fitting, returns target dimension
        assert service.get_embedding_dimension() == 200
        
        # After fitting, returns actual dimension
        service.fit(sample_texts)
        actual_dim = service.get_embedding_dimension()
        assert isinstance(actual_dim, int)
        assert actual_dim > 0
        assert actual_dim <= 200  # May be reduced by SVD
    
    def test_semantic_similarity(self, sample_texts):
        """Test that semantically similar texts have higher similarity."""
        service = TfidfEmbeddingService()
        service.fit(sample_texts)
        
        # Test texts with different levels of similarity
        text1 = "machine learning algorithms and models"
        text2 = "artificial intelligence and deep learning"  # Similar to text1
        text3 = "web server configuration and deployment"    # Different topic
        
        emb1 = service.embed_text(text1)
        emb2 = service.embed_text(text2)
        emb3 = service.embed_text(text3)
        
        # Calculate cosine similarities
        sim_1_2 = np.dot(emb1, emb2)  # Similar topics
        sim_1_3 = np.dot(emb1, emb3)  # Different topics
        
        # Similar topics should have higher similarity
        assert sim_1_2 > sim_1_3
    
    def test_consistent_embeddings(self, sample_texts):
        """Test that same text produces consistent embeddings."""
        service = TfidfEmbeddingService()
        service.fit(sample_texts)
        
        text = "consistent embedding test"
        embedding1 = service.embed_text(text)
        embedding2 = service.embed_text(text)
        
        np.testing.assert_array_almost_equal(embedding1, embedding2, decimal=6)