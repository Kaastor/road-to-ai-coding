"""Mock embedding service for testing without sentence-transformers dependency."""

import logging
from typing import List
import numpy as np
import hashlib

logger = logging.getLogger(__name__)


class MockEmbeddingService:
    """Mock service for generating text embeddings without external dependencies."""
    
    def __init__(self, model_name: str = "mock-embeddings", dimension: int = 384):
        """Initialize the mock embedding service.
        
        Args:
            model_name: Name of the mock model.
            dimension: Dimensionality of embeddings to generate.
        """
        self.model_name = model_name
        self.dimension = dimension
        logger.info(f"Initialized mock embedding service: {model_name} (dim={dimension})")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate mock embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            numpy array of shape (n_texts, embedding_dim) containing mock embeddings.
        """
        if not texts:
            return np.array([])
        
        embeddings = []
        for text in texts:
            # Create deterministic embeddings based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convert hash to seed for reproducible random embeddings
            seed = int(text_hash[:8], 16)
            np.random.seed(seed)
            
            # Generate normalized random vector
            embedding = np.random.randn(self.dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            
            embeddings.append(embedding)
        
        result = np.array(embeddings)
        logger.debug(f"Generated mock embeddings shape: {result.shape}")
        return result
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate mock embedding for a single text.
        
        Args:
            text: Text string to embed.
            
        Returns:
            1D numpy array containing the mock embedding.
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of the embeddings."""
        return self.dimension