"""Tests for document loader service."""

import pytest
from pathlib import Path
from app.services.document_loader import DocumentLoader, Document


class TestDocument:
    """Test cases for Document class."""
    
    def test_document_creation(self):
        """Test basic document creation."""
        content = "# Test Document\nThis is test content."
        source = "test.md"
        
        doc = Document(content=content, source=source)
        
        assert doc.content == content
        assert doc.source == source
        assert doc.doc_id == "test"
        assert doc.metadata["source"] == source
        assert doc.metadata["content_length"] == len(content)
    
    def test_document_with_custom_id(self):
        """Test document creation with custom ID."""
        doc = Document(content="test", source="test.md", doc_id="custom_id")
        
        assert doc.doc_id == "custom_id"
    
    def test_document_repr(self):
        """Test document string representation."""
        doc = Document(content="test", source="test.md")
        repr_str = repr(doc)
        
        assert "Document(doc_id='test'" in repr_str
        assert "source='test.md'" in repr_str


class TestDocumentLoader:
    """Test cases for DocumentLoader class."""
    
    def test_loader_initialization(self):
        """Test loader initialization."""
        loader = DocumentLoader("test_docs")
        
        assert loader.docs_directory == Path("test_docs")
        assert loader.documents == {}
        assert loader.get_document_count() == 0
    
    def test_load_documents_from_existing_docs(self):
        """Test loading documents from existing docs directory."""
        loader = DocumentLoader("docs")
        documents = loader.load_documents()
        
        # Should find our sample markdown files
        assert len(documents) > 0
        assert loader.get_document_count() > 0
        
        # Check that documents have expected attributes
        for doc in documents:
            assert isinstance(doc, Document)
            assert doc.content
            assert doc.source
            assert doc.doc_id
    
    def test_load_documents_nonexistent_directory(self):
        """Test loading from non-existent directory."""
        loader = DocumentLoader("nonexistent_dir")
        documents = loader.load_documents()
        
        assert len(documents) == 0
        assert loader.get_document_count() == 0
    
    def test_get_document_by_id(self):
        """Test retrieving document by ID."""
        loader = DocumentLoader("docs")
        documents = loader.load_documents()
        
        if documents:
            doc_id = documents[0].doc_id
            retrieved_doc = loader.get_document(doc_id)
            
            assert retrieved_doc is not None
            assert retrieved_doc.doc_id == doc_id
    
    def test_get_nonexistent_document(self):
        """Test retrieving non-existent document."""
        loader = DocumentLoader("docs")
        doc = loader.get_document("nonexistent_id")
        
        assert doc is None
    
    def test_get_all_documents(self):
        """Test getting all loaded documents."""
        loader = DocumentLoader("docs")
        loader.load_documents()
        
        all_docs = loader.get_all_documents()
        assert len(all_docs) == loader.get_document_count()
        
        for doc in all_docs:
            assert isinstance(doc, Document)