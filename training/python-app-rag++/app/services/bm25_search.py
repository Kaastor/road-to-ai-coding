"""BM25 keyword search service for document retrieval."""

import logging
from typing import List, Dict, Any, Tuple
import re
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Search:
    """BM25 keyword search service for document retrieval."""
    
    def __init__(self):
        """Initialize the BM25 search service."""
        self._corpus = None
        self._documents = []
        self._bm25 = None
        logger.info("BM25 search service initialized")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25 search.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of tokens.
        """
        # Simple tokenization - split on whitespace and punctuation, lowercase
        tokens = re.findall(r'\w+', text.lower())
        return tokens
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Index documents for BM25 search.
        
        Args:
            documents: List of document dictionaries with 'chunk_text' field.
        """
        if not documents:
            logger.warning("No documents provided for indexing")
            return
        
        self._documents = documents
        
        # Extract and tokenize text from documents
        corpus = []
        for doc in documents:
            text = doc.get('chunk_text', '')
            tokens = self._tokenize(text)
            corpus.append(tokens)
        
        # Create BM25 index
        self._corpus = corpus
        self._bm25 = BM25Okapi(corpus)
        
        logger.info(f"Indexed {len(documents)} documents for BM25 search")
    
    def search(self, query: str, k: int = 5) -> Tuple[List[float], List[Dict[str, Any]]]:
        """Search for documents using BM25.
        
        Args:
            query: Search query text.
            k: Number of results to return.
            
        Returns:
            Tuple of (scores, documents) where scores is a list of BM25 scores
            and documents is a list of document metadata.
        """
        if self._bm25 is None or not self._documents:
            logger.warning("No BM25 index available for search")
            return [], []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            logger.warning("Empty query after tokenization")
            return [], []
        
        # Get BM25 scores for all documents
        scores = self._bm25.get_scores(query_tokens)
        
        # Get top k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        # Prepare results
        result_scores = [float(scores[i]) for i in top_indices]
        result_documents = [self._documents[i] for i in top_indices]
        
        logger.debug(f"BM25 search for '{query}' returned {len(result_documents)} results")
        return result_scores, result_documents
    
    def get_document_count(self) -> int:
        """Get the total number of documents indexed."""
        return len(self._documents) if self._documents else 0
    
    def is_indexed(self) -> bool:
        """Check if documents are indexed and ready for search."""
        return self._bm25 is not None and bool(self._documents)