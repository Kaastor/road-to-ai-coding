"""Tests for BM25 search service."""

import pytest
from app.services.bm25_search import BM25Search


class TestBM25Search:
    """Test cases for BM25 search service."""
    
    def test_initialization(self):
        """Test BM25 search service initialization."""
        bm25 = BM25Search()
        assert bm25.get_document_count() == 0
        assert not bm25.is_indexed()
    
    def test_tokenization(self):
        """Test text tokenization."""
        bm25 = BM25Search()
        
        # Basic tokenization
        tokens = bm25._tokenize("Hello world, this is a test!")
        assert tokens == ["hello", "world", "this", "is", "a", "test"]
        
        # Empty text
        tokens = bm25._tokenize("")
        assert tokens == []
        
        # Numbers and symbols
        tokens = bm25._tokenize("Test 123 & symbols @#$")
        assert tokens == ["test", "123", "symbols"]
    
    def test_index_documents(self):
        """Test document indexing."""
        bm25 = BM25Search()
        
        documents = [
            {"chunk_text": "Machine learning is a subset of artificial intelligence"},
            {"chunk_text": "Python is a programming language for data science"},
            {"chunk_text": "Natural language processing involves understanding text"}
        ]
        
        bm25.index_documents(documents)
        
        assert bm25.get_document_count() == 3
        assert bm25.is_indexed()
    
    def test_empty_documents(self):
        """Test indexing with empty document list."""
        bm25 = BM25Search()
        bm25.index_documents([])
        
        assert bm25.get_document_count() == 0
        assert not bm25.is_indexed()
    
    def test_search_basic(self):
        """Test basic BM25 search."""
        bm25 = BM25Search()
        
        documents = [
            {"chunk_text": "Machine learning algorithms for classification", "id": 1},
            {"chunk_text": "Python programming for beginners", "id": 2},
            {"chunk_text": "Deep learning neural networks", "id": 3}
        ]
        
        bm25.index_documents(documents)
        
        # Search for relevant term
        scores, results = bm25.search("machine learning", k=2)
        
        assert len(scores) == 2
        assert len(results) == 2
        assert scores[0] > 0  # Should have positive scores
        assert results[0]["id"] == 1  # Most relevant should be first
    
    def test_search_no_index(self):
        """Test search without indexing."""
        bm25 = BM25Search()
        scores, results = bm25.search("test query")
        
        assert scores == []
        assert results == []
    
    def test_search_empty_query(self):
        """Test search with empty query."""
        bm25 = BM25Search()
        
        documents = [{"chunk_text": "Some test content", "id": 1}]
        bm25.index_documents(documents)
        
        scores, results = bm25.search("")
        assert scores == []
        assert results == []
        
        scores, results = bm25.search("   ")  # Only whitespace
        assert scores == []
        assert results == []
    
    def test_search_relevance_ranking(self):
        """Test that search results are properly ranked by relevance."""
        bm25 = BM25Search()
        
        documents = [
            {"chunk_text": "Python is great for machine learning", "title": "ML with Python", "id": 1},
            {"chunk_text": "Java is used in enterprise applications", "title": "Enterprise Java", "id": 2},
            {"chunk_text": "Python programming language features", "title": "Python Features", "id": 3}
        ]
        
        bm25.index_documents(documents)
        
        # Search for "python" - should return python-related docs first
        scores, results = bm25.search("python programming", k=3)
        
        assert len(results) == 3
        # Scores should be in descending order
        assert scores[0] >= scores[1] >= scores[2]
        # Python-related documents should rank higher
        assert results[0]["id"] in [1, 3]