"""Tests for text chunker service."""

import pytest
from app.services.text_chunker import TextChunker, TextChunk


class TestTextChunk:
    """Test cases for TextChunk class."""
    
    def test_chunk_creation(self):
        """Test basic chunk creation."""
        chunk = TextChunk(
            text="This is a test chunk.",
            doc_id="test_doc",
            chunk_index=0,
            start_char=0,
            end_char=21
        )
        
        assert chunk.text == "This is a test chunk."
        assert chunk.doc_id == "test_doc"
        assert chunk.chunk_index == 0
        assert chunk.chunk_id == "test_doc_chunk_0"
    
    def test_chunk_id_generation(self):
        """Test chunk ID generation."""
        chunk = TextChunk("text", "doc123", 5, 0, 4)
        assert chunk.chunk_id == "doc123_chunk_5"


class TestTextChunker:
    """Test cases for TextChunker class."""
    
    def test_chunker_initialization(self):
        """Test chunker initialization with default values."""
        chunker = TextChunker()
        
        assert chunker.chunk_size == 500
        assert chunker.overlap_size == 50
        assert chunker.separator == "\n\n"
    
    def test_chunker_custom_parameters(self):
        """Test chunker initialization with custom parameters."""
        chunker = TextChunker(chunk_size=100, overlap_size=20, separator="\n")
        
        assert chunker.chunk_size == 100
        assert chunker.overlap_size == 20
        assert chunker.separator == "\n"
    
    def test_invalid_overlap_size(self):
        """Test that overlap size cannot be >= chunk size."""
        with pytest.raises(ValueError, match="Overlap size must be less than chunk size"):
            TextChunker(chunk_size=100, overlap_size=100)
    
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("", "test_doc")
        
        assert chunks == []
    
    def test_chunk_whitespace_only(self):
        """Test chunking whitespace-only text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("   \n\n  ", "test_doc")
        
        assert chunks == []
    
    def test_chunk_small_text(self):
        """Test chunking text smaller than chunk size."""
        chunker = TextChunker(chunk_size=100)
        text = "This is a small piece of text."
        
        chunks = chunker.chunk_text(text, "test_doc")
        
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].doc_id == "test_doc"
        assert chunks[0].chunk_index == 0
        assert chunks[0].chunk_id == "test_doc_chunk_0"
    
    def test_chunk_with_paragraphs(self):
        """Test chunking text with paragraph separators."""
        chunker = TextChunker(chunk_size=50, overlap_size=10)
        text = "First paragraph with some content.\n\nSecond paragraph with more content.\n\nThird paragraph."
        
        chunks = chunker.chunk_text(text, "test_doc")
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, TextChunk) for chunk in chunks)
        assert all(chunk.doc_id == "test_doc" for chunk in chunks)
        
        # Check that chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
    
    def test_chunk_without_separators(self):
        """Test chunking text without paragraph separators."""
        chunker = TextChunker(chunk_size=30, overlap_size=5)
        text = "This is a long sentence without paragraph breaks that should be split into multiple chunks."
        
        chunks = chunker.chunk_text(text, "test_doc")
        
        assert len(chunks) > 1
        # Should still create meaningful chunks even without paragraph separators
        assert all(len(chunk.text) > 0 for chunk in chunks)
    
    def test_overlap_functionality(self):
        """Test that overlapping chunks share content."""
        chunker = TextChunker(chunk_size=40, overlap_size=10)
        text = "First part of text.\n\nSecond part of text.\n\nThird part of text."
        
        chunks = chunker.chunk_text(text, "test_doc")
        
        if len(chunks) > 1:
            # Check that chunks have some overlapping content (simplified check)
            assert chunks[0].end_char > chunks[1].start_char
    
    def test_chunk_properties(self):
        """Test chunk start and end character positions."""
        chunker = TextChunker(chunk_size=30, overlap_size=5)
        text = "Short text for testing character positions."
        
        chunks = chunker.chunk_text(text, "test_doc")
        
        for chunk in chunks:
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
            assert len(chunk.text) == chunk.end_char - chunk.start_char