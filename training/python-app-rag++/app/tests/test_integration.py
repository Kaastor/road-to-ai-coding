"""Integration tests for Phase 3 pipeline."""

import pytest
import tempfile
from pathlib import Path
from app.services.document_loader import DocumentLoader
from app.services.text_chunker import TextChunker
from app.services.mock_embedding_service import MockEmbeddingService
from app.services.vector_storage import VectorStorage


class TestPhase3Integration:
    """Integration tests for the complete Phase 3 pipeline."""
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary directory with test documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir)
            
            # Create test markdown files
            (docs_dir / "doc1.md").write_text(
                "# Document One\n\nThis is the first test document with vector embeddings content."
            )
            (docs_dir / "doc2.md").write_text(
                "# Document Two\n\nThis document discusses API design and search functionality."
            )
            (docs_dir / "doc3.md").write_text(
                "# Document Three\n\nFeedback systems and user interaction patterns are covered here."
            )
            
            yield docs_dir
    
    def test_complete_pipeline(self, temp_docs_dir):
        """Test the complete document processing pipeline."""
        # Initialize services
        doc_loader = DocumentLoader(docs_directory=str(temp_docs_dir))
        text_chunker = TextChunker(chunk_size=100, overlap_size=20)
        embedding_service = MockEmbeddingService(dimension=128)  # Smaller for testing
        vector_storage = VectorStorage(dimension=128)
        
        # Load documents
        documents = doc_loader.load_documents()
        assert len(documents) == 3
        
        # Process documents
        all_chunks = []
        chunk_metadata = []
        
        for doc in documents:
            chunks = text_chunker.chunk_text(doc.content, doc_id=doc.doc_id)
            for chunk in chunks:
                all_chunks.append(chunk.text)
                chunk_metadata.append({
                    "source_file": str(doc.file_path),
                    "title": doc.title,
                    "chunk_index": chunk.chunk_index,
                    "chunk_text": chunk.text,
                    "doc_id": doc.doc_id
                })
        
        assert len(all_chunks) > 0
        assert len(chunk_metadata) == len(all_chunks)
        
        # Generate embeddings
        embeddings = embedding_service.embed_texts(all_chunks)
        assert embeddings.shape[0] == len(all_chunks)
        assert embeddings.shape[1] == 128
        
        # Index vectors
        doc_ids = vector_storage.add_documents(embeddings, chunk_metadata)
        assert len(doc_ids) == len(all_chunks)
        
        # Test search
        query = "vector embeddings API"
        query_embedding = embedding_service.embed_text(query)
        similarities, results = vector_storage.search(query_embedding, k=2)
        
        assert len(similarities) <= 2
        assert len(results) <= 2
        assert len(similarities) == len(results)
        
        # Verify results have expected structure
        if results:
            result = results[0]
            assert "title" in result
            assert "chunk_text" in result
            assert "doc_id" in result
            assert isinstance(similarities[0], float)
    
    def test_save_load_integration(self, temp_docs_dir):
        """Test that the complete pipeline works with save/load."""
        # Create and populate index
        embedding_service = MockEmbeddingService(dimension=64)
        original_storage = VectorStorage(dimension=64)
        
        doc_loader = DocumentLoader(docs_directory=str(temp_docs_dir))
        documents = doc_loader.load_documents()
        
        # Simple processing for testing
        texts = [doc.content for doc in documents]
        metadata = [{"title": doc.title, "doc_id": doc.doc_id} for doc in documents]
        embeddings = embedding_service.embed_texts(texts)
        original_storage.add_documents(embeddings, metadata)
        
        # Save index
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "test_index"
            original_storage.save_index(index_path)
            
            # Load in new storage
            new_storage = VectorStorage(dimension=64)
            new_storage.load_index(index_path)
            
            # Verify loaded storage works
            assert new_storage.get_document_count() == original_storage.get_document_count()
            
            # Test search works
            query_embedding = embedding_service.embed_text("test query")
            similarities, results = new_storage.search(query_embedding, k=1)
            
            assert len(results) > 0
            assert "title" in results[0]
    
    def test_empty_documents(self):
        """Test pipeline handles empty document set gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir)
            
            doc_loader = DocumentLoader(docs_directory=str(empty_dir))
            documents = doc_loader.load_documents()
            
            assert len(documents) == 0
            
            # Pipeline should handle empty case
            embedding_service = MockEmbeddingService()
            vector_storage = VectorStorage(dimension=384)
            
            embeddings = embedding_service.embed_texts([])
            assert embeddings.size == 0
            
            doc_ids = vector_storage.add_documents(embeddings, [])
            assert doc_ids == []
            
            # Search should return empty results
            query_embedding = embedding_service.embed_text("test")
            similarities, results = vector_storage.search(query_embedding, k=5)
            assert similarities == []
            assert results == []