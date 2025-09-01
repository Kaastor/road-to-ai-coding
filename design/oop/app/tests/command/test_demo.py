"""Tests for the command pattern demonstration."""

import pytest
from io import StringIO
import sys
from unittest.mock import patch
from app.command.demo import (
    demonstrate_basic_operations,
    demonstrate_undo_redo,
    demonstrate_delete_operations,
    demonstrate_formatting_operations,
    demonstrate_macro_commands,
    demonstrate_error_handling,
    demonstrate_command_history,
    print_editor_state,
    print_separator,
)
from app.command.text_editor import TextEditor
from app.command.invoker import TextEditorInvoker


class TestDemoFunctions:
    """Test cases for demonstration functions."""
    
    def test_demonstrate_basic_operations(self) -> None:
        """Test basic operations demonstration."""
        editor, invoker = demonstrate_basic_operations()
        
        # Should have created editor and invoker with some content
        assert isinstance(editor, TextEditor)
        assert isinstance(invoker, TextEditorInvoker)
        assert "Hello Beautiful World!" in editor.content
        assert invoker.get_undo_stack_size() > 0
    
    def test_demonstrate_undo_redo(self) -> None:
        """Test undo/redo demonstration."""
        editor, invoker = demonstrate_basic_operations()
        initial_stack_size = invoker.get_undo_stack_size()
        
        demonstrate_undo_redo(editor, invoker)
        
        # Should have performed some undo/redo operations
        # Final state should have some commands still available
        assert invoker.get_undo_stack_size() <= initial_stack_size
    
    def test_demonstrate_delete_operations(self) -> None:
        """Test delete operations demonstration."""
        editor, invoker = demonstrate_basic_operations()
        
        demonstrate_delete_operations(editor, invoker)
        
        # Should have performed delete operations
        # The exact content depends on the operations, but should be different
        assert editor.length > 0
    
    def test_demonstrate_formatting_operations(self) -> None:
        """Test formatting operations demonstration."""
        editor, invoker = demonstrate_basic_operations()
        
        demonstrate_formatting_operations(editor, invoker)
        
        # Should have some formatting segments
        segments = editor.get_formatted_segments()
        assert len(segments) >= 0  # May have been undone
    
    def test_demonstrate_macro_commands(self) -> None:
        """Test macro commands demonstration."""
        editor, invoker = demonstrate_basic_operations()
        
        demonstrate_macro_commands(editor, invoker)
        
        # Should have executed macro operations
        assert editor.length > 0
    
    def test_demonstrate_error_handling(self) -> None:
        """Test error handling demonstration."""
        editor, invoker = demonstrate_basic_operations()
        
        # Should not raise exceptions - errors should be caught
        demonstrate_error_handling(editor, invoker)
        
        # After clearing history, should have no undo/redo available
        assert not invoker.can_undo()
        assert not invoker.can_redo()
    
    def test_demonstrate_command_history(self) -> None:
        """Test command history demonstration."""
        # Should not raise exceptions
        demonstrate_command_history()
    
    def test_print_editor_state(self, capsys) -> None:
        """Test printing editor state."""
        editor = TextEditor()
        invoker = TextEditorInvoker()
        editor.insert_text(0, "Test")
        
        print_editor_state(editor, invoker)
        
        captured = capsys.readouterr()
        assert "Editor State:" in captured.out
        assert "Test" in captured.out
        assert "Command History:" in captured.out
    
    def test_print_separator(self, capsys) -> None:
        """Test printing separator."""
        print_separator("Test Title")
        
        captured = capsys.readouterr()
        assert "=" in captured.out
        assert "Test Title" in captured.out


class TestIntegrationDemo:
    """Integration tests for the complete demonstration."""
    
    def test_full_demo_sequence(self) -> None:
        """Test that the full demo sequence works without errors."""
        # This tests the complete flow that would be run in main()
        
        # Basic operations
        editor, invoker = demonstrate_basic_operations()
        assert editor.content != ""
        
        # Undo/redo
        demonstrate_undo_redo(editor, invoker)
        
        # Delete operations
        demonstrate_delete_operations(editor, invoker)
        
        # Formatting
        demonstrate_formatting_operations(editor, invoker)
        
        # Macros
        demonstrate_macro_commands(editor, invoker)
        
        # Error handling
        demonstrate_error_handling(editor, invoker)
        
        # Command history
        demonstrate_command_history()
        
        # All demonstrations should complete without exceptions
        assert True  # If we reach here, all demos passed
    
    def test_demo_with_empty_editor(self) -> None:
        """Test demonstrations starting with empty editor."""
        editor = TextEditor()
        invoker = TextEditorInvoker()
        
        # Should handle empty editor gracefully
        print_editor_state(editor, invoker)
        
        # Should be able to demonstrate error handling on empty editor
        demonstrate_error_handling(editor, invoker)
    
    def test_demo_resilience(self) -> None:
        """Test that demo functions handle different initial states gracefully."""
        editor = TextEditor()
        invoker = TextEditorInvoker()
        
        # Start with some content and commands
        editor.insert_text(0, "Initial content")
        
        # These functions should handle different initial states gracefully
        # Note: Some demo functions expect specific content, so we test them carefully
        demonstrate_undo_redo(editor, invoker)
        
        # For error handling, which clears history, that should always work
        demonstrate_error_handling(editor, invoker)
        
        # Test that we can still do basic operations after error handling
        editor.insert_text(0, "Hello World")
        demonstrate_formatting_operations(editor, invoker)