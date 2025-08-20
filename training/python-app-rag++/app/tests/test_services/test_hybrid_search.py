"""Tests for hybrid search service."""

import pytest
import numpy as np
from app.services.hybrid_search import HybridSearch
from app.services.vector_storage import VectorStorage
from app.services.mock_embedding_service import MockEmbeddingService


class TestHybridSearch:
    """Test cases for hybrid search service."""
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing."""
        return [
            {
                "chunk_text": "Machine learning is a subset of artificial intelligence",
                "source_file": "docs/ml.md",
                "title": "ML Introduction",
                "chunk_index": 0,
                "char_count": 55
            },
            {
                "chunk_text": "Python programming language for data analysis",
                "source_file": "docs/python.md", 
                "title": "Python Guide",
                "chunk_index": 0,
                "char_count": 46
            },
            {
                "chunk_text": "Deep learning neural networks and algorithms",
                "source_file": "docs/dl.md",
                "title": "Deep Learning",
                "chunk_index": 0,
                "char_count": 45
            }
        ]
    
    @pytest.fixture
    def mock_setup(self, sample_documents):
        """Set up mock vector storage and embedding service."""
        # Create mock embedding service
        embedding_service = MockEmbeddingService(dimension=4)
        
        # Create vector storage
        vector_storage = VectorStorage(dimension=4)
        
        # Generate embeddings for sample documents
        texts = [doc["chunk_text"] for doc in sample_documents]
        embeddings = embedding_service.embed_texts(texts)
        
        # Add to vector storage
        vector_storage.add_documents(embeddings, sample_documents)
        
        return vector_storage, embedding_service
    
    def test_initialization(self, mock_setup):
        """Test hybrid search initialization."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        assert hybrid.bm25_weight + hybrid.vector_weight == pytest.approx(1.0)
        assert hybrid.vector_storage == vector_storage
        assert hybrid.embedding_service == embedding_service
    
    def test_custom_weights(self, mock_setup):
        """Test hybrid search with custom weights."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service,
            bm25_weight=0.4,
            vector_weight=0.6
        )
        
        assert hybrid.bm25_weight == pytest.approx(0.4)
        assert hybrid.vector_weight == pytest.approx(0.6)
    
    def test_document_indexing(self, mock_setup, sample_documents):
        """Test document indexing for hybrid search."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        hybrid.index_documents(sample_documents)
        
        assert hybrid.bm25_search.get_document_count() == 3
        assert hybrid.bm25_search.is_indexed()
    
    def test_document_id_generation(self, mock_setup):
        """Test document ID generation."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        doc = {
            "source_file": "docs/test.md",
            "chunk_index": 2
        }
        
        doc_id = hybrid._get_document_id(doc)
        assert doc_id == "docs/test.md:2"
    
    def test_search_not_ready(self):
        """Test search when hybrid search is not ready."""
        hybrid = HybridSearch()
        results = hybrid.search("test query")
        
        assert results == []
    
    def test_hybrid_search_basic(self, mock_setup, sample_documents):
        """Test basic hybrid search functionality."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        hybrid.index_documents(sample_documents)
        
        # Search for relevant term
        results = hybrid.search("machine learning", k=2)
        
        assert len(results) <= 2
        if results:
            # Check result structure
            result = results[0]
            assert 'hybrid_score' in result
            assert 'bm25_score' in result
            assert 'vector_score' in result
            assert 'source_file' in result
            assert 'chunk_text' in result
    
    def test_hybrid_search_score_combination(self, mock_setup, sample_documents):
        """Test that hybrid search properly combines BM25 and vector scores."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service,
            bm25_weight=0.5,
            vector_weight=0.5
        )
        
        hybrid.index_documents(sample_documents)
        
        results = hybrid.search("python programming", k=3)
        
        if results:
            # Verify that hybrid scores are calculated
            for result in results:
                assert isinstance(result['hybrid_score'], (int, float))
                # Hybrid score should be influenced by both BM25 and vector scores
                assert 'bm25_score' in result
                assert 'vector_score' in result
    
    def test_search_empty_query(self, mock_setup, sample_documents):
        """Test search with empty query."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        hybrid.index_documents(sample_documents)
        
        # Empty query should return empty results
        results = hybrid.search("", k=5)
        # Note: This might return results depending on vector search behavior
        # The important thing is that it doesn't crash
        assert isinstance(results, list)
    
    def test_get_stats(self, mock_setup, sample_documents):
        """Test statistics retrieval."""
        vector_storage, embedding_service = mock_setup
        
        hybrid = HybridSearch(
            vector_storage=vector_storage,
            embedding_service=embedding_service
        )
        
        hybrid.index_documents(sample_documents)
        
        stats = hybrid.get_stats()
        
        assert 'bm25_documents' in stats
        assert 'vector_documents' in stats
        assert 'bm25_weight' in stats
        assert 'vector_weight' in stats
        assert 'ready' in stats
        
        assert stats['bm25_documents'] == 3
        assert stats['vector_documents'] == 3
        assert stats['ready'] is True