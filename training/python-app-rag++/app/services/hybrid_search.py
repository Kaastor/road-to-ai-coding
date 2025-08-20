"""Hybrid search service combining BM25 keyword search and vector similarity search."""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from .bm25_search import BM25Search
from .vector_storage import VectorStorage
from .adaptive_embedding_service import AdaptiveEmbeddingService

logger = logging.getLogger(__name__)


class HybridSearch:
    """Hybrid search service combining BM25 and vector search with score fusion."""
    
    def __init__(
        self,
        vector_storage: Optional[VectorStorage] = None,
        embedding_service: Optional[AdaptiveEmbeddingService] = None,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7
    ):
        """Initialize the hybrid search service.
        
        Args:
            vector_storage: Vector storage instance for semantic search.
            embedding_service: Embedding service for query encoding.
            bm25_weight: Weight for BM25 scores in hybrid ranking (0-1).
            vector_weight: Weight for vector scores in hybrid ranking (0-1).
        """
        self.vector_storage = vector_storage
        self.embedding_service = embedding_service
        self.bm25_search = BM25Search()
        
        # Normalize weights
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight
        
        logger.info(f"Hybrid search initialized with BM25 weight: {self.bm25_weight:.2f}, "
                   f"Vector weight: {self.vector_weight:.2f}")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Index documents for both BM25 and vector search.
        
        Args:
            documents: List of document dictionaries with metadata.
        """
        if not documents:
            logger.warning("No documents provided for indexing")
            return
        
        # Index for BM25 search
        logger.info("Indexing documents for BM25 search...")
        self.bm25_search.index_documents(documents)
        
        # Note: Vector storage indexing is handled by the DocumentIndexer
        # since it requires embeddings to be generated first
        
        logger.info(f"Hybrid search indexing complete for {len(documents)} documents")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining BM25 and vector search.
        
        Args:
            query: Search query text.
            k: Number of results to return.
            
        Returns:
            List of search results with combined scores and metadata.
        """
        logger.debug(f"Hybrid search for: '{query}' (k={k})")
        
        if not self._is_ready():
            logger.warning("Hybrid search not fully initialized")
            return []
        
        # Perform BM25 search
        bm25_scores, bm25_documents = self.bm25_search.search(query, k=k*2)  # Get more for fusion
        
        # Perform vector search
        query_embedding = self.embedding_service.embed_text(query)
        vector_similarities, vector_documents = self.vector_storage.search(query_embedding, k=k*2)
        
        # Create document score mapping for fusion
        doc_scores = {}
        
        # Process BM25 results
        for score, doc in zip(bm25_scores, bm25_documents):
            doc_id = self._get_document_id(doc)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {'doc': doc, 'bm25_score': 0.0, 'vector_score': 0.0}
            doc_scores[doc_id]['bm25_score'] = score
        
        # Process vector results
        for similarity, doc in zip(vector_similarities, vector_documents):
            doc_id = self._get_document_id(doc)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {'doc': doc, 'bm25_score': 0.0, 'vector_score': 0.0}
            doc_scores[doc_id]['vector_score'] = similarity
        
        # Normalize scores to [0, 1] range
        if doc_scores:
            bm25_scores_list = [info['bm25_score'] for info in doc_scores.values()]
            vector_scores_list = [info['vector_score'] for info in doc_scores.values()]
            
            bm25_max = max(bm25_scores_list) if max(bm25_scores_list) > 0 else 1.0
            vector_max = max(vector_scores_list) if max(vector_scores_list) > 0 else 1.0
            
            # Calculate hybrid scores
            hybrid_results = []
            for doc_id, info in doc_scores.items():
                normalized_bm25 = info['bm25_score'] / bm25_max
                normalized_vector = info['vector_score'] / vector_max
                
                hybrid_score = (self.bm25_weight * normalized_bm25 + 
                              self.vector_weight * normalized_vector)
                
                result = {
                    'hybrid_score': float(hybrid_score),
                    'bm25_score': float(info['bm25_score']),
                    'vector_score': float(info['vector_score']),
                    'source_file': info['doc'].get('source_file', ''),
                    'title': info['doc'].get('title', ''),
                    'chunk_index': info['doc'].get('chunk_index', 0),
                    'chunk_text': info['doc'].get('chunk_text', ''),
                    'char_count': info['doc'].get('char_count', 0)
                }
                hybrid_results.append(result)
            
            # Sort by hybrid score and return top k
            hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
            results = hybrid_results[:k]
            
            logger.debug(f"Hybrid search returned {len(results)} results")
            return results
        
        return []
    
    def _get_document_id(self, doc: Dict[str, Any]) -> str:
        """Generate a unique identifier for a document chunk.
        
        Args:
            doc: Document metadata dictionary.
            
        Returns:
            Unique document identifier.
        """
        source = doc.get('source_file', '')
        chunk_idx = doc.get('chunk_index', 0)
        return f"{source}:{chunk_idx}"
    
    def _is_ready(self) -> bool:
        """Check if hybrid search is ready to perform searches.
        
        Returns:
            True if both BM25 and vector search are ready.
        """
        bm25_ready = self.bm25_search.is_indexed()
        vector_ready = (self.vector_storage is not None and 
                       self.vector_storage.get_document_count() > 0 and
                       self.embedding_service is not None)
        
        return bm25_ready and vector_ready
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hybrid search statistics.
        
        Returns:
            Dictionary with current statistics.
        """
        return {
            'bm25_documents': self.bm25_search.get_document_count(),
            'vector_documents': self.vector_storage.get_document_count() if self.vector_storage else 0,
            'bm25_weight': self.bm25_weight,
            'vector_weight': self.vector_weight,
            'ready': self._is_ready()
        }