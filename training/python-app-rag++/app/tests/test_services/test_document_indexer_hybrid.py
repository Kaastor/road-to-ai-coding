"""Tests for document indexer with hybrid search capabilities."""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.services.document_indexer import DocumentIndexer


class TestDocumentIndexerHybrid:
    """Test cases for document indexer with hybrid search."""
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory with sample markdown files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample markdown files
        (temp_dir / "ml_intro.md").write_text("""
# Machine Learning Introduction

Machine learning is a subset of artificial intelligence (AI) that provides systems 
the ability to automatically learn and improve from experience without being explicitly programmed.

## Types of Machine Learning
- Supervised learning
- Unsupervised learning  
- Reinforcement learning
""")
        
        (temp_dir / "python_guide.md").write_text("""
# Python Programming Guide

Python is a high-level, interpreted programming language with dynamic semantics.
It is particularly popular for data science and machine learning applications.

## Key Features
- Easy to learn syntax
- Extensive libraries
- Cross-platform compatibility
""")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_hybrid_search_integration(self, temp_docs_dir):
        """Test that document indexer properly integrates hybrid search."""
        indexer = DocumentIndexer()
        
        # Index documents
        stats = indexer.index_documents(temp_docs_dir)
        
        # Verify indexing stats include hybrid search
        assert 'hybrid_search_ready' in stats
        assert stats['hybrid_search_ready'] is True
        assert stats['total_documents'] == 2
        assert stats['total_chunks'] > 0
    
    def test_hybrid_search_documents(self, temp_docs_dir):
        """Test hybrid search functionality through document indexer."""
        indexer = DocumentIndexer()
        indexer.index_documents(temp_docs_dir)
        
        # Perform hybrid search
        results = indexer.hybrid_search_documents("machine learning", k=3)
        
        assert isinstance(results, list)
        if results:
            # Check result structure
            result = results[0]
            assert 'hybrid_score' in result
            assert 'bm25_score' in result  
            assert 'vector_score' in result
            assert 'source_file' in result
            assert 'chunk_text' in result
            assert 'title' in result
            
            # Verify scores are numeric
            assert isinstance(result['hybrid_score'], (int, float))
            assert isinstance(result['bm25_score'], (int, float))
            assert isinstance(result['vector_score'], (int, float))
    
    def test_bm25_search_documents(self, temp_docs_dir):
        """Test BM25-only search functionality through document indexer.""" 
        indexer = DocumentIndexer()
        indexer.index_documents(temp_docs_dir)
        
        # Perform BM25 search
        results = indexer.bm25_search_documents("python programming", k=3)
        
        assert isinstance(results, list)
        if results:
            # Check result structure
            result = results[0]
            assert 'bm25_score' in result
            assert 'source_file' in result
            assert 'chunk_text' in result
            assert 'title' in result
            
            # Verify BM25 score is numeric
            assert isinstance(result['bm25_score'], (int, float))
    
    def test_search_comparison(self, temp_docs_dir):
        """Test that different search methods return different results."""
        indexer = DocumentIndexer()
        indexer.index_documents(temp_docs_dir)
        
        query = "machine learning"
        
        # Get results from different search methods
        vector_results = indexer.search_documents(query, k=3)
        bm25_results = indexer.bm25_search_documents(query, k=3)
        hybrid_results = indexer.hybrid_search_documents(query, k=3)
        
        # All should return some results for this query
        assert len(vector_results) > 0
        assert len(bm25_results) > 0 
        assert len(hybrid_results) > 0
        
        # Results should have different scoring schemes
        if vector_results:
            assert 'similarity' in vector_results[0]
        if bm25_results:
            assert 'bm25_score' in bm25_results[0]
        if hybrid_results:
            assert 'hybrid_score' in hybrid_results[0]
    
    def test_search_before_indexing(self):
        """Test search methods before documents are indexed."""
        indexer = DocumentIndexer()
        
        # All search methods should return empty results
        assert indexer.search_documents("test") == []
        assert indexer.bm25_search_documents("test") == []
        assert indexer.hybrid_search_documents("test") == []
    
    def test_save_load_with_hybrid_search(self, temp_docs_dir):
        """Test saving and loading index maintains hybrid search capability."""
        indexer = DocumentIndexer()
        indexer.index_documents(temp_docs_dir)
        
        # Perform search before saving
        original_results = indexer.hybrid_search_documents("python", k=2)
        
        # Save index
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "test_index"
            indexer.save_index(index_path)
            
            # Create new indexer and load
            new_indexer = DocumentIndexer()
            new_indexer.load_index(index_path)
            
            # Perform search after loading
            loaded_results = new_indexer.hybrid_search_documents("python", k=2)
            
            # Should have similar results
            assert len(loaded_results) == len(original_results)
            
            if loaded_results and original_results:
                # Check that hybrid search is working
                assert 'hybrid_score' in loaded_results[0]
                assert 'bm25_score' in loaded_results[0]
                assert 'vector_score' in loaded_results[0]