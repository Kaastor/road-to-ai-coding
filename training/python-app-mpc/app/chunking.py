"""Text chunking utilities for document processing."""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_index: int
    page_start: int
    page_end: int
    char_start: int
    char_end: int


class SimpleChunker:
    """Simple text chunker for PoC."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        """Initialize chunker with size and overlap parameters."""
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, pages: List[Dict[str, Any]]) -> List[TextChunk]:
        """Chunk a document from extracted pages."""
        chunks: List[TextChunk] = []
        full_text = ""
        page_boundaries = []
        
        # Combine all pages into full text and track page boundaries
        current_pos = 0
        for page in pages:
            page_text = page["text"]
            if page_text.strip():  # Only add non-empty pages
                page_boundaries.append({
                    "page_number": page["page_number"],
                    "start": current_pos,
                    "end": current_pos + len(page_text)
                })
                full_text += page_text + "\n\n"
                current_pos = len(full_text)
        
        if not full_text.strip():
            return chunks
        
        # Create chunks with overlap
        chunks = self._create_overlapping_chunks(full_text, page_boundaries)
        
        return chunks
    
    def _create_overlapping_chunks(self, text: str, page_boundaries: List[Dict]) -> List[TextChunk]:
        """Create overlapping chunks from text."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(end - 100, start)
                sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', text[search_start:end])]
                if sentence_ends:
                    end = search_start + sentence_ends[-1]
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                # Find which pages this chunk spans
                page_start, page_end = self._find_page_range(start, end, page_boundaries)
                
                chunks.append(TextChunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    page_start=page_start,
                    page_end=page_end,
                    char_start=start,
                    char_end=end
                ))
                chunk_index += 1
            
            # Move start position (with overlap)
            start = max(start + self.chunk_size - self.overlap, end)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def _find_page_range(self, start: int, end: int, page_boundaries: List[Dict]) -> tuple[int, int]:
        """Find which pages a chunk spans."""
        page_start = 1
        page_end = 1
        
        for boundary in page_boundaries:
            if boundary["start"] <= start < boundary["end"]:
                page_start = boundary["page_number"]
            if boundary["start"] < end <= boundary["end"]:
                page_end = boundary["page_number"]
        
        return page_start, page_end


def create_chunker(chunk_size: int = 800, overlap: int = 100) -> SimpleChunker:
    """Factory function to create a chunker."""
    return SimpleChunker(chunk_size, overlap)