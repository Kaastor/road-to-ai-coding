"""Text chunking service for splitting documents into smaller segments."""

import re
from typing import Generator
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text from a document."""
    text: str
    doc_id: str
    chunk_index: int
    start_char: int
    end_char: int
    
    @property
    def chunk_id(self) -> str:
        """Generate a unique chunk ID."""
        return f"{self.doc_id}_chunk_{self.chunk_index}"


class TextChunker:
    """Splits text into overlapping chunks for better retrieval."""
    
    def __init__(
        self, 
        chunk_size: int = 500,
        overlap_size: int = 50,
        separator: str = "\n\n"
    ):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            overlap_size: Number of characters to overlap between chunks
            separator: Primary separator for splitting text (paragraphs by default)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.separator = separator
        
        if overlap_size >= chunk_size:
            raise ValueError("Overlap size must be less than chunk size")
    
    def chunk_text(self, text: str, doc_id: str) -> list[TextChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text content to chunk
            doc_id: Document identifier
            
        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []
        
        # If text is smaller than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [self._create_chunk(text.strip(), doc_id, 0, 0)]
        
        # First try to split by separator (e.g., paragraphs)
        segments = self._split_by_separator(text)
        
        # Then create overlapping chunks
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for segment in segments:
            # If adding this segment would exceed chunk size, finalize current chunk
            if current_chunk and len(current_chunk) + len(segment) > self.chunk_size:
                chunk = self._create_chunk(
                    current_chunk, doc_id, chunk_index, current_start
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap from previous chunk
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + segment
                current_start = chunk.end_char - len(overlap_text)
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk = current_chunk + segment
                else:
                    current_chunk = segment
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk, doc_id, chunk_index, current_start
            )
            chunks.append(chunk)
        
        # If we still only have one chunk but it's too long, force split
        if len(chunks) == 1 and len(chunks[0].text) > self.chunk_size:
            return self._force_split_text(text, doc_id)
        
        return chunks
    
    def _split_by_separator(self, text: str) -> list[str]:
        """Split text by separator, preserving the separator."""
        if self.separator not in text:
            # Fallback to sentence splitting if no separator found
            return self._split_by_sentences(text)
        
        parts = text.split(self.separator)
        segments = []
        
        for i, part in enumerate(parts):
            if i < len(parts) - 1:  # Add separator back except for last part
                segments.append(part + self.separator)
            else:
                segments.append(part)
        
        return [seg for seg in segments if seg.strip()]
    
    def _split_by_sentences(self, text: str) -> list[str]:
        """Fallback: split text by sentences."""
        sentences = re.split(r'[.!?]+\s+', text)
        result = []
        for i, s in enumerate(sentences):
            if s.strip():
                # Don't add period if it's the last sentence and already ends with punctuation
                if i == len(sentences) - 1 and text.rstrip()[-1] in '.!?':
                    result.append(s.strip())
                else:
                    result.append(s.strip() + '. ')
        return result
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the overlap text from the end of current chunk."""
        if len(text) <= self.overlap_size:
            return text
        
        # Try to break at word boundaries
        overlap_text = text[-self.overlap_size:]
        
        # Find the first space to avoid breaking words
        first_space = overlap_text.find(' ')
        if first_space > 0:
            overlap_text = overlap_text[first_space:].strip()
        
        return overlap_text + " " if overlap_text else ""
    
    def _force_split_text(self, text: str, doc_id: str) -> list[TextChunk]:
        """Force split text into chunks when normal splitting fails."""
        chunks = []
        text = text.strip()
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at word boundary if possible
            if end < len(text):
                # Look for space within overlap distance
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = TextChunk(
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = max(end - self.overlap_size, start + 1)
        
        return chunks
    
    def _create_chunk(
        self, text: str, doc_id: str, chunk_index: int, start_char: int
    ) -> TextChunk:
        """Create a TextChunk object."""
        clean_text = text.strip()
        return TextChunk(
            text=clean_text,
            doc_id=doc_id,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=start_char + len(clean_text)
        )