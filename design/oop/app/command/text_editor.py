"""TextEditor receiver class that performs the actual text operations."""

import logging
from dataclasses import dataclass
from enum import Enum


class TextFormat(Enum):
    """Enumeration of supported text formatting options."""
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    NORMAL = "normal"


@dataclass
class TextSegment:
    """Represents a segment of text with its formatting."""
    text: str
    start_pos: int
    end_pos: int
    format_type: TextFormat = TextFormat.NORMAL


class TextEditor:
    """The receiver class that performs actual text editing operations.
    
    This class maintains the text content and formatting state,
    and provides methods for text manipulation operations.
    """
    
    def __init__(self) -> None:
        """Initialize an empty text editor."""
        self._content: str = ""
        self._formatted_segments: list[TextSegment] = []
        self._logger = logging.getLogger(__name__)
    
    @property
    def content(self) -> str:
        """Get the current text content."""
        return self._content
    
    @property
    def length(self) -> int:
        """Get the current length of text content."""
        return len(self._content)
    
    def insert_text(self, position: int, text: str) -> None:
        """Insert text at the specified position.
        
        Args:
            position: The position where to insert text (0-based index)
            text: The text to insert
            
        Raises:
            ValueError: If position is out of bounds
        """
        if position < 0 or position > len(self._content):
            raise ValueError(f"Position {position} is out of bounds for content length {len(self._content)}")
        
        self._content = self._content[:position] + text + self._content[position:]
        self._update_segment_positions_after_insert(position, len(text))
        self._logger.info(f"Inserted '{text}' at position {position}")
    
    def delete_text(self, start_position: int, length: int) -> str:
        """Delete text from the specified position.
        
        Args:
            start_position: The starting position for deletion (0-based index)
            length: The number of characters to delete
            
        Returns:
            The deleted text
            
        Raises:
            ValueError: If position or length is out of bounds
        """
        if start_position < 0 or start_position >= len(self._content):
            raise ValueError(f"Start position {start_position} is out of bounds")
        
        end_position = start_position + length
        if end_position > len(self._content):
            raise ValueError(f"Delete length {length} exceeds content bounds")
        
        deleted_text = self._content[start_position:end_position]
        self._content = self._content[:start_position] + self._content[end_position:]
        self._update_segment_positions_after_delete(start_position, length)
        self._logger.info(f"Deleted '{deleted_text}' from position {start_position}")
        
        return deleted_text
    
    def format_text(self, start_position: int, length: int, format_type: TextFormat) -> list[TextSegment]:
        """Apply formatting to a text range.
        
        Args:
            start_position: The starting position for formatting
            length: The length of text to format
            format_type: The formatting to apply
            
        Returns:
            List of previously applied formatting segments in the range
            
        Raises:
            ValueError: If position or length is out of bounds
        """
        if start_position < 0 or start_position >= len(self._content):
            raise ValueError(f"Start position {start_position} is out of bounds")
        
        end_position = start_position + length
        if end_position > len(self._content):
            raise ValueError(f"Format length {length} exceeds content bounds")
        
        # Remove existing formatting in this range and store for undo
        old_segments = self._remove_formatting_in_range(start_position, end_position)
        
        # Add new formatting
        new_segment = TextSegment(
            text=self._content[start_position:end_position],
            start_pos=start_position,
            end_pos=end_position,
            format_type=format_type
        )
        self._formatted_segments.append(new_segment)
        self._logger.info(f"Applied {format_type.value} formatting to position {start_position}-{end_position}")
        
        return old_segments
    
    def get_formatted_segments(self) -> list[TextSegment]:
        """Get all current formatting segments."""
        return self._formatted_segments.copy()
    
    def restore_formatting(self, segments: list[TextSegment]) -> None:
        """Restore previous formatting segments.
        
        Args:
            segments: List of formatting segments to restore
        """
        for segment in segments:
            # Remove any conflicting formatting first
            self._remove_formatting_in_range(segment.start_pos, segment.end_pos)
            # Add the restored segment
            self._formatted_segments.append(segment)
        
        self._logger.info(f"Restored {len(segments)} formatting segments")
    
    def _update_segment_positions_after_insert(self, insert_position: int, insert_length: int) -> None:
        """Update formatting segment positions after text insertion."""
        for segment in self._formatted_segments:
            if segment.start_pos >= insert_position:
                segment.start_pos += insert_length
                segment.end_pos += insert_length
            elif segment.end_pos > insert_position:
                segment.end_pos += insert_length
    
    def _update_segment_positions_after_delete(self, delete_position: int, delete_length: int) -> None:
        """Update formatting segment positions after text deletion."""
        segments_to_remove = []
        
        for segment in self._formatted_segments:
            delete_end = delete_position + delete_length
            
            if segment.end_pos <= delete_position:
                # Segment is before deletion, no change needed
                continue
            elif segment.start_pos >= delete_end:
                # Segment is after deletion, shift positions
                segment.start_pos -= delete_length
                segment.end_pos -= delete_length
            elif segment.start_pos >= delete_position and segment.end_pos <= delete_end:
                # Segment is completely within deletion, remove it
                segments_to_remove.append(segment)
            else:
                # Segment partially overlaps with deletion, adjust accordingly
                if segment.start_pos < delete_position:
                    segment.end_pos = max(segment.start_pos, segment.end_pos - delete_length)
                else:
                    segment.start_pos = delete_position
                    segment.end_pos -= delete_length
        
        for segment in segments_to_remove:
            self._formatted_segments.remove(segment)
    
    def _remove_formatting_in_range(self, start_pos: int, end_pos: int) -> list[TextSegment]:
        """Remove formatting segments in the specified range and return them."""
        old_segments = []
        segments_to_remove = []
        
        for segment in self._formatted_segments:
            if (segment.start_pos < end_pos and segment.end_pos > start_pos):
                old_segments.append(TextSegment(
                    text=segment.text,
                    start_pos=segment.start_pos,
                    end_pos=segment.end_pos,
                    format_type=segment.format_type
                ))
                segments_to_remove.append(segment)
        
        for segment in segments_to_remove:
            self._formatted_segments.remove(segment)
        
        return old_segments
    
    def __str__(self) -> str:
        """Return a string representation of the editor content."""
        if not self._content:
            return "[Empty]"
        
        result = f"Content: '{self._content}'"
        if self._formatted_segments:
            result += f"\nFormatting: {len(self._formatted_segments)} segments"
            for segment in self._formatted_segments:
                result += f"\n  - {segment.format_type.value}: pos {segment.start_pos}-{segment.end_pos}"
        
        return result