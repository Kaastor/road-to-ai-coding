"""TF-IDF based embedding service as a lightweight fallback."""

import logging
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


class TfidfEmbeddingService:
    """Lightweight embedding service using TF-IDF + SVD dimensionality reduction."""
    
    def __init__(self, max_features: int = 5000, embedding_dim: int = 384):
        """Initialize the TF-IDF embedding service.
        
        Args:
            max_features: Maximum number of TF-IDF features.
            embedding_dim: Target embedding dimensionality.
        """
        self.model_name = f"tfidf-svd-{embedding_dim}d"
        self.max_features = max_features
        self.embedding_dim = embedding_dim
        self._fitted = False
        
        # Create TF-IDF + SVD pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),  # Include bigrams
                lowercase=True,
                strip_accents='ascii'
            )),
            ('svd', TruncatedSVD(
                n_components=min(embedding_dim, max_features - 1),  # Leave room for SVD
                random_state=42
            ))
        ])
        
        logger.info(f"Initialized TF-IDF embedding service: {self.model_name}")
    
    def fit(self, texts: List[str]) -> None:
        """Fit the TF-IDF model on a corpus of texts.
        
        Args:
            texts: List of text strings to fit the model on.
        """
        if not texts:
            raise ValueError("Cannot fit on empty text corpus")
        
        logger.info(f"Fitting TF-IDF model on {len(texts)} texts...")
        
        # First fit TF-IDF to see actual vocabulary size
        tfidf_matrix = self.pipeline['tfidf'].fit_transform(texts)
        actual_features = tfidf_matrix.shape[1]
        
        # Adjust SVD components based on actual features
        max_components = min(self.embedding_dim, actual_features - 1, len(texts) - 1)
        if max_components <= 0:
            max_components = min(actual_features, len(texts)) - 1
        
        # Update SVD component count
        self.pipeline['svd'].n_components = max(1, max_components)
        
        # Now fit the SVD on the TF-IDF matrix
        self.pipeline['svd'].fit(tfidf_matrix)
        self._fitted = True
        
        # Get actual dimensions after fitting
        actual_dim = self.pipeline['svd'].n_components
        logger.info(f"Model fitted with {actual_dim} dimensions (from {actual_features} TF-IDF features)")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            numpy array of shape (n_texts, embedding_dim) containing embeddings.
        """
        if not texts:
            return np.array([])
        
        if not self._fitted:
            # Auto-fit on the provided texts
            logger.info("Model not fitted, auto-fitting on provided texts...")
            self.fit(texts)
        
        # Generate TF-IDF features and apply SVD
        tfidf_features = self.pipeline['tfidf'].transform(texts)
        embeddings = self.pipeline['svd'].transform(tfidf_features)
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embeddings / norms
        
        logger.debug(f"Generated TF-IDF embeddings shape: {normalized_embeddings.shape}")
        return normalized_embeddings.astype(np.float32)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.
        
        Args:
            text: Text string to embed.
            
        Returns:
            1D numpy array containing the embedding.
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of the embeddings."""
        if self._fitted:
            return self.pipeline['svd'].n_components
        return self.embedding_dim
    
    def is_fitted(self) -> bool:
        """Check if the model is fitted."""
        return self._fitted