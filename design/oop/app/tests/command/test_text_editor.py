"""Tests for TextEditor receiver class."""

import pytest
from app.command.text_editor import TextEditor, TextFormat, TextSegment


class TestTextEditor:
    """Test cases for TextEditor class."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.editor = TextEditor()
    
    def test_initial_state(self) -> None:
        """Test editor initial state."""
        assert self.editor.content == ""
        assert self.editor.length == 0
        assert len(self.editor.get_formatted_segments()) == 0
    
    def test_insert_text_at_beginning(self) -> None:
        """Test inserting text at the beginning."""
        self.editor.insert_text(0, "Hello")
        assert self.editor.content == "Hello"
        assert self.editor.length == 5
    
    def test_insert_text_at_end(self) -> None:
        """Test inserting text at the end."""
        self.editor.insert_text(0, "Hello")
        self.editor.insert_text(5, " World")
        assert self.editor.content == "Hello World"
        assert self.editor.length == 11
    
    def test_insert_text_in_middle(self) -> None:
        """Test inserting text in the middle."""
        self.editor.insert_text(0, "Hello World")
        self.editor.insert_text(6, "Beautiful ")
        assert self.editor.content == "Hello Beautiful World"
    
    def test_insert_text_invalid_position(self) -> None:
        """Test inserting text at invalid positions."""
        with pytest.raises(ValueError, match="Position -1 is out of bounds"):
            self.editor.insert_text(-1, "text")
        
        with pytest.raises(ValueError, match="Position 1 is out of bounds"):
            self.editor.insert_text(1, "text")
    
    def test_delete_text_basic(self) -> None:
        """Test basic text deletion."""
        self.editor.insert_text(0, "Hello World")
        deleted = self.editor.delete_text(6, 5)
        assert deleted == "World"
        assert self.editor.content == "Hello "
    
    def test_delete_text_from_beginning(self) -> None:
        """Test deleting text from beginning."""
        self.editor.insert_text(0, "Hello World")
        deleted = self.editor.delete_text(0, 6)
        assert deleted == "Hello "
        assert self.editor.content == "World"
    
    def test_delete_text_invalid_position(self) -> None:
        """Test deleting text from invalid positions."""
        self.editor.insert_text(0, "Hello")
        
        with pytest.raises(ValueError, match="Start position -1 is out of bounds"):
            self.editor.delete_text(-1, 1)
        
        with pytest.raises(ValueError, match="Start position 5 is out of bounds"):
            self.editor.delete_text(5, 1)
        
        with pytest.raises(ValueError, match="Delete length 6 exceeds content bounds"):
            self.editor.delete_text(0, 6)
    
    def test_format_text_basic(self) -> None:
        """Test basic text formatting."""
        self.editor.insert_text(0, "Hello World")
        old_segments = self.editor.format_text(0, 5, TextFormat.BOLD)
        
        assert len(old_segments) == 0  # No previous formatting
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].start_pos == 0
        assert segments[0].end_pos == 5
        assert segments[0].format_type == TextFormat.BOLD
        assert segments[0].text == "Hello"
    
    def test_format_text_overlapping(self) -> None:
        """Test overlapping text formatting."""
        self.editor.insert_text(0, "Hello World")
        
        # Apply bold to "Hello"
        self.editor.format_text(0, 5, TextFormat.BOLD)
        
        # Apply italic to "lo Wo" (overlapping)
        old_segments = self.editor.format_text(3, 5, TextFormat.ITALIC)
        
        # Should have removed the overlapping bold formatting
        assert len(old_segments) == 1
        assert old_segments[0].format_type == TextFormat.BOLD
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.ITALIC
        assert segments[0].start_pos == 3
        assert segments[0].end_pos == 8
    
    def test_format_text_invalid_position(self) -> None:
        """Test formatting text at invalid positions."""
        self.editor.insert_text(0, "Hello")
        
        with pytest.raises(ValueError, match="Start position -1 is out of bounds"):
            self.editor.format_text(-1, 1, TextFormat.BOLD)
        
        with pytest.raises(ValueError, match="Start position 5 is out of bounds"):
            self.editor.format_text(5, 1, TextFormat.BOLD)
        
        with pytest.raises(ValueError, match="Format length 6 exceeds content bounds"):
            self.editor.format_text(0, 6, TextFormat.BOLD)
    
    def test_restore_formatting(self) -> None:
        """Test restoring previous formatting."""
        self.editor.insert_text(0, "Hello World")
        
        # Apply initial formatting
        self.editor.format_text(0, 5, TextFormat.BOLD)
        
        # Apply overlapping formatting and get old segments
        old_segments = self.editor.format_text(0, 5, TextFormat.ITALIC)
        
        # Restore old formatting
        self.editor.restore_formatting(old_segments)
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.BOLD
    
    def test_segment_position_update_after_insert(self) -> None:
        """Test that formatting segments are updated after text insertion."""
        self.editor.insert_text(0, "Hello World")
        self.editor.format_text(6, 5, TextFormat.BOLD)  # Format "World"
        
        # Insert text before the formatted segment
        self.editor.insert_text(0, "Hi ")
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].start_pos == 9  # 6 + 3 = 9
        assert segments[0].end_pos == 14   # 11 + 3 = 14
        assert segments[0].format_type == TextFormat.BOLD
    
    def test_segment_position_update_after_delete(self) -> None:
        """Test that formatting segments are updated after text deletion."""
        self.editor.insert_text(0, "Hello Beautiful World")
        self.editor.format_text(16, 5, TextFormat.BOLD)  # Format "World"
        
        # Delete "Beautiful " (10 characters at position 6)
        self.editor.delete_text(6, 10)
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].start_pos == 6   # 16 - 10 = 6
        assert segments[0].end_pos == 11    # 21 - 10 = 11
        assert segments[0].format_type == TextFormat.BOLD
    
    def test_segment_removal_after_delete(self) -> None:
        """Test that formatting segments are removed when text is deleted."""
        self.editor.insert_text(0, "Hello World")
        self.editor.format_text(6, 5, TextFormat.BOLD)  # Format "World"
        
        # Delete the formatted text
        self.editor.delete_text(6, 5)
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 0
    
    def test_str_representation_empty(self) -> None:
        """Test string representation of empty editor."""
        assert str(self.editor) == "[Empty]"
    
    def test_str_representation_with_content(self) -> None:
        """Test string representation with content."""
        self.editor.insert_text(0, "Hello World")
        result = str(self.editor)
        assert "Content: 'Hello World'" in result
    
    def test_str_representation_with_formatting(self) -> None:
        """Test string representation with formatting."""
        self.editor.insert_text(0, "Hello World")
        self.editor.format_text(0, 5, TextFormat.BOLD)
        result = str(self.editor)
        assert "Content: 'Hello World'" in result
        assert "Formatting: 1 segments" in result
        assert "bold: pos 0-5" in result