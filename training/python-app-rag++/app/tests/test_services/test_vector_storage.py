"""Tests for the vector storage service."""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from app.services.vector_storage import VectorStorage


class TestVectorStorage:
    """Test cases for VectorStorage."""
    
    @pytest.fixture
    def vector_storage(self):
        """Create a vector storage for testing."""
        return VectorStorage(dimension=384)  # Common dimension for all-MiniLM-L6-v2
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        np.random.seed(42)  # For reproducible tests
        return np.random.rand(3, 384).astype(np.float32)
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample document metadata."""
        return [
            {"title": "Doc 1", "content": "First document content", "source": "doc1.md"},
            {"title": "Doc 2", "content": "Second document content", "source": "doc2.md"},
            {"title": "Doc 3", "content": "Third document content", "source": "doc3.md"},
        ]
    
    def test_init(self):
        """Test vector storage initialization."""
        storage = VectorStorage(dimension=256, index_type="flat")
        assert storage.dimension == 256
        assert storage.index_type == "flat"
        assert storage._index is None
        assert storage._documents == []
        assert storage._next_id == 0
    
    def test_add_documents(self, vector_storage, sample_embeddings, sample_documents):
        """Test adding documents to storage."""
        doc_ids = vector_storage.add_documents(sample_embeddings, sample_documents)
        
        assert len(doc_ids) == len(sample_documents)
        assert doc_ids == [0, 1, 2]
        assert vector_storage.get_document_count() == 3
    
    def test_add_empty_documents(self, vector_storage):
        """Test adding empty list of documents."""
        doc_ids = vector_storage.add_documents(np.array([]), [])
        assert doc_ids == []
        assert vector_storage.get_document_count() == 0
    
    def test_add_documents_mismatch_length(self, vector_storage, sample_embeddings):
        """Test error when embeddings and documents length mismatch."""
        with pytest.raises(ValueError, match="Number of embeddings must match"):
            vector_storage.add_documents(sample_embeddings, [{"title": "Only one doc"}])
    
    def test_search_empty_storage(self, vector_storage):
        """Test searching in empty storage."""
        query = np.random.rand(384).astype(np.float32)
        similarities, documents = vector_storage.search(query, k=5)
        
        assert similarities == []
        assert documents == []
    
    def test_search_with_documents(self, vector_storage, sample_embeddings, sample_documents):
        """Test searching with documents in storage."""
        # Add documents
        vector_storage.add_documents(sample_embeddings, sample_documents)
        
        # Search with first embedding as query
        query = sample_embeddings[0]
        similarities, documents = vector_storage.search(query, k=2)
        
        assert len(similarities) == 2
        assert len(documents) == 2
        assert all(isinstance(score, float) for score in similarities)
        
        # First result should be most similar (likely the same document)
        assert similarities[0] >= similarities[1]
    
    def test_search_k_larger_than_storage(self, vector_storage, sample_embeddings, sample_documents):
        """Test searching with k larger than number of documents."""
        vector_storage.add_documents(sample_embeddings, sample_documents)
        
        query = np.random.rand(384).astype(np.float32)
        similarities, documents = vector_storage.search(query, k=10)
        
        # Should return all available documents
        assert len(similarities) == 3
        assert len(documents) == 3
    
    def test_document_metadata_preserved(self, vector_storage, sample_embeddings, sample_documents):
        """Test that document metadata is preserved with IDs."""
        doc_ids = vector_storage.add_documents(sample_embeddings, sample_documents)
        
        query = sample_embeddings[0]
        similarities, documents = vector_storage.search(query, k=1)
        
        # Check that returned document has ID and original metadata
        doc = documents[0]
        assert "id" in doc
        assert doc["id"] in doc_ids
        assert "title" in doc
        assert "content" in doc
        assert "source" in doc
    
    def test_save_and_load_index(self, vector_storage, sample_embeddings, sample_documents):
        """Test saving and loading index."""
        # Add documents
        vector_storage.add_documents(sample_embeddings, sample_documents)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_index"
            
            # Save index
            vector_storage.save_index(filepath)
            
            # Verify files were created
            assert filepath.with_suffix('.faiss').exists()
            assert filepath.with_suffix('.json').exists()
            
            # Create new storage and load
            new_storage = VectorStorage(dimension=384)
            new_storage.load_index(filepath)
            
            # Verify loaded data
            assert new_storage.get_document_count() == 3
            
            # Test search works the same
            query = sample_embeddings[0]
            orig_similarities, orig_documents = vector_storage.search(query, k=2)
            loaded_similarities, loaded_documents = new_storage.search(query, k=2)
            
            np.testing.assert_array_almost_equal(orig_similarities, loaded_similarities)
            assert len(loaded_documents) == len(orig_documents)
    
    def test_load_nonexistent_index(self, vector_storage):
        """Test loading non-existent index raises error."""
        with pytest.raises(FileNotFoundError):
            vector_storage.load_index(Path("nonexistent/path"))
    
    def test_zero_vector_normalization(self, vector_storage):
        """Test handling of zero vectors during normalization."""
        zero_embedding = np.zeros((1, 384))
        documents = [{"title": "Zero doc"}]
        
        # Should not raise error
        doc_ids = vector_storage.add_documents(zero_embedding, documents)
        assert len(doc_ids) == 1
        
        # Search with zero vector should work
        query = np.zeros(384)
        similarities, docs = vector_storage.search(query, k=1)
        assert len(similarities) == 1
        assert len(docs) == 1