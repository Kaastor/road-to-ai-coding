"""Tests for the adaptive embedding service."""

import pytest
import numpy as np
from app.services.adaptive_embedding_service import AdaptiveEmbeddingService


class TestAdaptiveEmbeddingService:
    """Test cases for AdaptiveEmbeddingService."""
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return [
            "This is a test document about embeddings.",
            "Vector search and similarity matching are important.",
            "Machine learning models process text data."
        ]
    
    def test_init_with_tfidf_preference(self):
        """Test initialization with TF-IDF preference."""
        service = AdaptiveEmbeddingService(preferred_model="tfidf", embedding_dim=256)
        assert service.embedding_dim == 256
        assert service.preferred_model == "tfidf"
        
        # Should initialize with TF-IDF service
        service_type = service.get_service_type()
        assert service_type in ["tfidf", "mock"]  # Fallback to mock if scikit-learn issues
    
    def test_init_with_sentence_transformers_fallback(self):
        """Test initialization falls back when sentence-transformers unavailable."""
        service = AdaptiveEmbeddingService(preferred_model="sentence-transformers")
        
        # Should fallback to TF-IDF or mock
        service_type = service.get_service_type()
        assert service_type in ["tfidf", "mock"]
    
    def test_embed_texts(self, sample_texts):
        """Test embedding multiple texts."""
        service = AdaptiveEmbeddingService(preferred_model="tfidf")
        embeddings = service.embed_texts(sample_texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] > 0
    
    def test_embed_single_text(self, sample_texts):
        """Test embedding a single text."""
        service = AdaptiveEmbeddingService(preferred_model="tfidf")
        
        # Prepare with corpus first
        service.prepare_for_corpus(sample_texts)
        
        text = "This is a test text for embedding."
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert embedding.shape[0] > 0
    
    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""
        service = AdaptiveEmbeddingService(embedding_dim=128)
        dimension = service.get_embedding_dimension()
        
        assert isinstance(dimension, int)
        assert dimension > 0
    
    def test_prepare_for_corpus(self, sample_texts):
        """Test preparing service for corpus."""
        service = AdaptiveEmbeddingService(preferred_model="tfidf")
        
        # Should not raise error
        service.prepare_for_corpus(sample_texts)
        
        # Should be able to embed after preparation
        embeddings = service.embed_texts(sample_texts)
        assert embeddings.shape[0] == len(sample_texts)
    
    def test_model_name_property(self):
        """Test that model name property works."""
        service = AdaptiveEmbeddingService()
        model_name = service.model_name
        
        assert isinstance(model_name, str)
        assert len(model_name) > 0
    
    def test_get_service_type(self):
        """Test getting the active service type."""
        service = AdaptiveEmbeddingService(preferred_model="tfidf")
        service_type = service.get_service_type()
        
        assert service_type in ["tfidf", "mock"]
        assert isinstance(service_type, str)
    
    def test_fallback_chain(self):
        """Test the complete fallback chain works."""
        # This should work regardless of what's available
        service = AdaptiveEmbeddingService(preferred_model="sentence-transformers")
        
        # Basic functionality should work
        texts = ["test text one", "test text two"]
        embeddings = service.embed_texts(texts)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] > 0
        
        # Single text embedding should work
        single_embedding = service.embed_text("single test")
        assert single_embedding.shape[0] > 0
    
    def test_empty_texts_handling(self):
        """Test handling of empty text lists."""
        service = AdaptiveEmbeddingService()
        embeddings = service.embed_texts([])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.size == 0