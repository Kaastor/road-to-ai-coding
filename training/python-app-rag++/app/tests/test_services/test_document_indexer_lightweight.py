"""Tests for the document indexer with lightweight embeddings."""

import pytest
import tempfile
from pathlib import Path
from app.services.document_indexer import DocumentIndexer


class TestDocumentIndexerLightweight:
    """Test cases for DocumentIndexer with TF-IDF embeddings."""
    
    @pytest.fixture
    def indexer(self):
        """Create a document indexer for testing."""
        return DocumentIndexer(
            embedding_model="tfidf",
            chunk_size=200,
            chunk_overlap=50
        )
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary directory with test documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir()
            
            # Create test markdown files
            (docs_dir / "doc1.md").write_text(
                "# Vector Embeddings\n\nVector embeddings are numerical representations of text that capture semantic meaning in high-dimensional space."
            )
            (docs_dir / "doc2.md").write_text(
                "# API Design\n\nWell-designed APIs are crucial for building scalable applications. RESTful endpoints provide clear interfaces."
            )
            (docs_dir / "doc3.md").write_text(
                "# BM25 Search\n\nBM25 is a ranking function used in information retrieval systems for scoring document relevance."
            )
            
            yield docs_dir
    
    def test_init(self):
        """Test indexer initialization."""
        indexer = DocumentIndexer(embedding_model="tfidf")
        
        assert indexer.embedding_service.get_service_type() == "tfidf"
        assert indexer.vector_storage is None  # Initialized lazily
    
    def test_index_documents(self, indexer, temp_docs_dir):
        """Test indexing documents from directory."""
        stats = indexer.index_documents(temp_docs_dir)
        
        assert "total_documents" in stats
        assert "total_chunks" in stats
        assert "embedding_dimension" in stats
        assert "indexed_document_ids" in stats
        
        assert stats["total_documents"] == 3
        assert stats["total_chunks"] >= 3  # At least one chunk per document
        assert stats["embedding_dimension"] > 0
        assert len(stats["indexed_document_ids"]) == stats["total_chunks"]
        
        # Check that vector storage was initialized
        assert indexer.vector_storage is not None
        assert indexer.vector_storage.get_document_count() == stats["total_chunks"]
    
    def test_search_documents(self, indexer, temp_docs_dir):
        """Test searching indexed documents."""
        # Index documents first
        indexer.index_documents(temp_docs_dir)
        
        # Search for content related to vector embeddings
        results = indexer.search_documents("vector embeddings semantic meaning", k=2)
        
        assert len(results) > 0
        assert len(results) <= 2
        
        # Check result structure
        result = results[0]
        assert "similarity" in result
        assert "source_file" in result
        assert "title" in result
        assert "chunk_index" in result
        assert "chunk_text" in result
        assert "char_count" in result
        
        assert isinstance(result["similarity"], float)
        assert result["similarity"] >= 0
        
        # Should find the vector embeddings document
        assert "vector" in result["title"].lower() or "vector" in result["chunk_text"].lower()
    
    def test_search_different_topics(self, indexer, temp_docs_dir):
        """Test searching for different topics returns different results."""
        indexer.index_documents(temp_docs_dir)
        
        # Search for different topics
        api_results = indexer.search_documents("API design RESTful endpoints", k=1)
        bm25_results = indexer.search_documents("BM25 ranking information retrieval", k=1)
        
        assert len(api_results) > 0
        assert len(bm25_results) > 0
        
        # Should find different documents
        api_result = api_results[0]
        bm25_result = bm25_results[0]
        
        # Should contain relevant keywords
        assert "api" in api_result["title"].lower() or "api" in api_result["chunk_text"].lower()
        assert "bm25" in bm25_result["title"].lower() or "bm25" in bm25_result["chunk_text"].lower()
    
    def test_get_stats(self, indexer, temp_docs_dir):
        """Test getting indexer statistics."""
        # Before indexing
        stats = indexer.get_stats()
        assert stats["total_documents_indexed"] == 0
        assert stats["service_type"] == "tfidf"
        assert "tfidf" in stats["model_name"].lower()
        
        # After indexing
        indexer.index_documents(temp_docs_dir)
        stats = indexer.get_stats()
        assert stats["total_documents_indexed"] > 0
        assert stats["embedding_dimension"] > 0
    
    def test_save_and_load_index(self, indexer, temp_docs_dir):
        """Test saving and loading index."""
        # Index documents
        original_stats = indexer.index_documents(temp_docs_dir)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "test_index"
            
            # Save index
            indexer.save_index(index_path)
            
            # Verify files were created
            assert index_path.with_suffix('.faiss').exists()
            assert index_path.with_suffix('.json').exists()
            
            # Create new indexer with same embedding model and load
            new_indexer = DocumentIndexer(embedding_model="tfidf")
            new_indexer.load_index(index_path)
            
            # Verify loaded index works
            loaded_stats = new_indexer.get_stats()
            assert loaded_stats["total_documents_indexed"] == original_stats["total_chunks"]
            assert loaded_stats["embedding_dimension"] == original_stats["embedding_dimension"]
            
            # Test search works with loaded index
            results = new_indexer.search_documents("vector embeddings", k=1)
            assert len(results) > 0
    
    def test_search_empty_index(self, indexer):
        """Test searching without indexing documents."""
        results = indexer.search_documents("test query", k=5)
        assert results == []
    
    def test_save_without_index(self, indexer):
        """Test saving without indexing raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "empty_index"
            
            with pytest.raises(ValueError, match="No index to save"):
                indexer.save_index(index_path)
    
    def test_semantic_search_quality(self, indexer, temp_docs_dir):
        """Test that TF-IDF provides reasonable semantic search."""
        indexer.index_documents(temp_docs_dir)
        
        # Test queries with related terms (TF-IDF works better with exact matches)
        test_cases = [
            ("vector embeddings", "vector"),           # Should find vector embeddings doc
            ("API design", "api"),                     # Should find API design doc  
            ("BM25 ranking", "bm25"),                  # Should find BM25 doc
        ]
        
        for query, expected_keyword in test_cases:
            results = indexer.search_documents(query, k=1)
            assert len(results) > 0
            
            result = results[0]
            found_keyword = expected_keyword.lower() in (
                result["title"].lower() + " " + result["chunk_text"].lower()
            )
            assert found_keyword, f"Query '{query}' should find content with '{expected_keyword}'"
    
    def test_chunk_metadata_preservation(self, indexer, temp_docs_dir):
        """Test that document metadata is preserved through indexing."""
        indexer.index_documents(temp_docs_dir)
        
        # Search and verify metadata
        results = indexer.search_documents("embeddings", k=3)
        assert len(results) > 0
        
        for result in results:
            # Check all required metadata fields
            assert "source_file" in result
            assert "title" in result
            assert "chunk_index" in result
            assert isinstance(result["chunk_index"], int)
            assert result["chunk_index"] >= 0
            
            # Source file should be a valid path
            source_path = Path(result["source_file"])
            assert source_path.name.endswith('.md')