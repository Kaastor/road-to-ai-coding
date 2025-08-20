"""Vector storage service using FAISS for efficient similarity search."""

import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import numpy as np
import faiss
import json

logger = logging.getLogger(__name__)


class VectorStorage:
    """Vector storage and similarity search using FAISS."""
    
    def __init__(self, dimension: int, index_type: str = "flat"):
        """Initialize the vector storage.
        
        Args:
            dimension: Dimensionality of the vectors to store.
            index_type: Type of FAISS index to use ('flat' for exact search).
        """
        self.dimension = dimension
        self.index_type = index_type
        self._index = None
        self._documents = []  # Store document metadata
        self._next_id = 0
        
        logger.info(f"Initializing vector storage with dimension: {dimension}, index_type: {index_type}")
    
    @property
    def index(self) -> faiss.Index:
        """Lazy load the FAISS index."""
        if self._index is None:
            if self.index_type == "flat":
                # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
                self._index = faiss.IndexFlatIP(self.dimension)
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            logger.info(f"Created FAISS {self.index_type} index with dimension {self.dimension}")
        return self._index
    
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]) -> List[int]:
        """Add document embeddings to the index.
        
        Args:
            embeddings: Array of shape (n_docs, dimension) containing embeddings.
            documents: List of document metadata dictionaries.
            
        Returns:
            List of document IDs assigned to the added documents.
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        if embeddings.size == 0:
            return []
        
        # Normalize embeddings for cosine similarity
        normalized_embeddings = embeddings.copy()
        norms = np.linalg.norm(normalized_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = normalized_embeddings / norms
        
        # Assign IDs and store metadata
        doc_ids = list(range(self._next_id, self._next_id + len(documents)))
        self._next_id += len(documents)
        
        # Add ID to each document
        for i, doc in enumerate(documents):
            doc_with_id = doc.copy()
            doc_with_id['id'] = doc_ids[i]
            self._documents.append(doc_with_id)
        
        # Add to FAISS index
        self.index.add(normalized_embeddings.astype(np.float32))
        
        logger.info(f"Added {len(documents)} documents to vector storage. Total: {len(self._documents)}")
        return doc_ids
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[float], List[Dict[str, Any]]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector.
            k: Number of similar documents to retrieve.
            
        Returns:
            Tuple of (similarities, documents) where similarities is a list of similarity scores
            and documents is a list of document metadata.
        """
        if len(self._documents) == 0:
            return [], []
        
        # Normalize query embedding
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            normalized_query = query_embedding
        else:
            normalized_query = query_embedding / query_norm
        
        # Reshape for FAISS (expects 2D array)
        query_vector = normalized_query.reshape(1, -1).astype(np.float32)
        
        # Search in FAISS index
        k = min(k, len(self._documents))  # Don't search for more than available
        similarities, indices = self.index.search(query_vector, k)
        
        # Get corresponding documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self._documents):  # Valid index
                results.append(self._documents[idx])
        
        logger.debug(f"Found {len(results)} similar documents")
        return similarities[0].tolist(), results
    
    def get_document_count(self) -> int:
        """Get the total number of documents in storage."""
        return len(self._documents)
    
    def save_index(self, filepath: Path) -> None:
        """Save the FAISS index and document metadata to disk.
        
        Args:
            filepath: Path to save the index (without extension).
        """
        if self._index is None:
            logger.warning("No index to save")
            return
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(filepath.with_suffix('.faiss')))
        
        # Save document metadata
        metadata = {
            'documents': self._documents,
            'next_id': self._next_id,
            'dimension': self.dimension,
            'index_type': self.index_type
        }
        with open(filepath.with_suffix('.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved index and metadata to {filepath}")
    
    def load_index(self, filepath: Path) -> None:
        """Load a FAISS index and document metadata from disk.
        
        Args:
            filepath: Path to load the index from (without extension).
        """
        filepath = Path(filepath)
        
        # Load FAISS index
        index_file = filepath.with_suffix('.faiss')
        if not index_file.exists():
            raise FileNotFoundError(f"Index file not found: {index_file}")
        
        self._index = faiss.read_index(str(index_file))
        
        # Load document metadata
        metadata_file = filepath.with_suffix('.json')
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self._documents = metadata['documents']
        self._next_id = metadata['next_id']
        
        # Validate dimensions match
        if metadata['dimension'] != self.dimension:
            raise ValueError(f"Loaded index dimension ({metadata['dimension']}) "
                           f"doesn't match expected dimension ({self.dimension})")
        
        logger.info(f"Loaded index with {len(self._documents)} documents from {filepath}")