"""Adaptive embedding service with automatic fallback to lighter alternatives."""

import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)


class AdaptiveEmbeddingService:
    """Embedding service that automatically selects the best available implementation."""
    
    def __init__(self, preferred_model: str = "sentence-transformers", embedding_dim: int = 384):
        """Initialize the adaptive embedding service.
        
        Args:
            preferred_model: Preferred embedding approach ('sentence-transformers', 'tfidf', 'mock').
            embedding_dim: Target embedding dimensionality.
        """
        self.preferred_model = preferred_model
        self.embedding_dim = embedding_dim
        self._service = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize the best available embedding service."""
        # Use TF-IDF + SVD as primary approach (lightweight and effective)
        if self.preferred_model in ["tfidf", "sentence-transformers", "auto"]:
            try:
                from .tfidf_embedding_service import TfidfEmbeddingService
                self._service = TfidfEmbeddingService(embedding_dim=self.embedding_dim)
                logger.info("✅ Using TF-IDF + SVD embeddings (primary approach)")
                return
            except ImportError:
                logger.info("⚠️  scikit-learn not available, using mock embeddings...")
        
        # Final fallback to mock embeddings
        from .mock_embedding_service import MockEmbeddingService
        self._service = MockEmbeddingService(dimension=self.embedding_dim)
        logger.info("✅ Using mock embeddings as fallback")
    
    @property
    def model_name(self) -> str:
        """Get the name of the active embedding model."""
        return getattr(self._service, 'model_name', 'unknown')
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            numpy array of shape (n_texts, embedding_dim) containing embeddings.
        """
        return self._service.embed_texts(texts)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.
        
        Args:
            text: Text string to embed.
            
        Returns:
            1D numpy array containing the embedding.
        """
        return self._service.embed_text(text)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of the embeddings."""
        return self._service.get_embedding_dimension()
    
    def prepare_for_corpus(self, texts: List[str]) -> None:
        """Prepare the embedding service for a specific corpus (used by TF-IDF).
        
        Args:
            texts: Corpus of texts to prepare the model for.
        """
        if hasattr(self._service, 'fit'):
            self._service.fit(texts)
            logger.info("Embedding service prepared for corpus")
    
    def get_service_type(self) -> str:
        """Get the type of the active embedding service."""
        service_class = self._service.__class__.__name__
        return service_class.replace('EmbeddingService', '').lower()