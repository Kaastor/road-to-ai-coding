"""Tests for concrete command implementations."""

import pytest
from app.command.commands import DeleteTextCommand, FormatTextCommand, InsertTextCommand, MacroCommand
from app.command.text_editor import TextEditor, TextFormat


class TestInsertTextCommand:
    """Test cases for InsertTextCommand."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.editor = TextEditor()
    
    def test_execute_insert_command(self) -> None:
        """Test executing insert command."""
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        cmd.execute()
        
        assert self.editor.content == "Hello"
        assert cmd.get_description() == "Insert 'Hello' at position 0"
    
    def test_undo_insert_command(self) -> None:
        """Test undoing insert command."""
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        cmd.execute()
        cmd.undo()
        
        assert self.editor.content == ""
    
    def test_execute_already_executed_command(self) -> None:
        """Test executing already executed command."""
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        cmd.execute()
        
        with pytest.raises(RuntimeError, match="Command has already been executed"):
            cmd.execute()
    
    def test_undo_unexecuted_command(self) -> None:
        """Test undoing unexecuted command."""
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        
        with pytest.raises(RuntimeError, match="Cannot undo command that hasn't been executed"):
            cmd.undo()
    
    def test_execute_undo_execute_cycle(self) -> None:
        """Test execute-undo-execute cycle."""
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        
        # Execute
        cmd.execute()
        assert self.editor.content == "Hello"
        
        # Undo
        cmd.undo()
        assert self.editor.content == ""
        
        # Execute again
        cmd.execute()
        assert self.editor.content == "Hello"


class TestDeleteTextCommand:
    """Test cases for DeleteTextCommand."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.editor = TextEditor()
        self.editor.insert_text(0, "Hello World")
    
    def test_execute_delete_command(self) -> None:
        """Test executing delete command."""
        cmd = DeleteTextCommand(self.editor, 6, 5)
        cmd.execute()
        
        assert self.editor.content == "Hello "
        assert "Delete 'World' from position 6" in cmd.get_description()
    
    def test_undo_delete_command(self) -> None:
        """Test undoing delete command."""
        cmd = DeleteTextCommand(self.editor, 6, 5)
        cmd.execute()
        cmd.undo()
        
        assert self.editor.content == "Hello World"
    
    def test_description_before_execution(self) -> None:
        """Test command description before execution."""
        cmd = DeleteTextCommand(self.editor, 6, 5)
        assert cmd.get_description() == "Delete 5 characters from position 6"
    
    def test_execute_already_executed_command(self) -> None:
        """Test executing already executed command."""
        cmd = DeleteTextCommand(self.editor, 6, 5)
        cmd.execute()
        
        with pytest.raises(RuntimeError, match="Command has already been executed"):
            cmd.execute()
    
    def test_undo_unexecuted_command(self) -> None:
        """Test undoing unexecuted command."""
        cmd = DeleteTextCommand(self.editor, 6, 5)
        
        with pytest.raises(RuntimeError, match="Cannot undo command that hasn't been executed"):
            cmd.undo()


class TestFormatTextCommand:
    """Test cases for FormatTextCommand."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.editor = TextEditor()
        self.editor.insert_text(0, "Hello World")
    
    def test_execute_format_command(self) -> None:
        """Test executing format command."""
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        cmd.execute()
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.BOLD
        assert segments[0].start_pos == 0
        assert segments[0].end_pos == 5
    
    def test_undo_format_command(self) -> None:
        """Test undoing format command."""
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        cmd.execute()
        cmd.undo()
        
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 0
    
    def test_undo_format_with_previous_formatting(self) -> None:
        """Test undoing format command that overwrote previous formatting."""
        # Apply initial formatting
        self.editor.format_text(0, 5, TextFormat.ITALIC)
        
        # Apply overlapping formatting via command
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        cmd.execute()
        
        # Should have bold formatting now
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.BOLD
        
        # Undo should restore italic formatting
        cmd.undo()
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.ITALIC
    
    def test_description(self) -> None:
        """Test command description."""
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        assert cmd.get_description() == "Apply bold formatting to position 0-5"
    
    def test_execute_already_executed_command(self) -> None:
        """Test executing already executed command."""
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        cmd.execute()
        
        with pytest.raises(RuntimeError, match="Command has already been executed"):
            cmd.execute()
    
    def test_undo_unexecuted_command(self) -> None:
        """Test undoing unexecuted command."""
        cmd = FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        
        with pytest.raises(RuntimeError, match="Cannot undo command that hasn't been executed"):
            cmd.undo()


class TestMacroCommand:
    """Test cases for MacroCommand."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.editor = TextEditor()
    
    def test_execute_macro_command(self) -> None:
        """Test executing macro command."""
        commands = [
            InsertTextCommand(self.editor, 0, "Hello"),
            InsertTextCommand(self.editor, 5, " World"),
            FormatTextCommand(self.editor, 0, 5, TextFormat.BOLD)
        ]
        
        macro = MacroCommand(commands, "Add greeting with formatting")
        macro.execute()
        
        assert self.editor.content == "Hello World"
        segments = self.editor.get_formatted_segments()
        assert len(segments) == 1
        assert segments[0].format_type == TextFormat.BOLD
    
    def test_undo_macro_command(self) -> None:
        """Test undoing macro command."""
        commands = [
            InsertTextCommand(self.editor, 0, "Hello"),
            InsertTextCommand(self.editor, 5, " World"),
        ]
        
        macro = MacroCommand(commands, "Add greeting")
        macro.execute()
        macro.undo()
        
        assert self.editor.content == ""
    
    def test_macro_partial_failure(self) -> None:
        """Test macro command with partial failure."""
        # Create commands where the second one will fail
        commands = [
            InsertTextCommand(self.editor, 0, "Hello"),
            InsertTextCommand(self.editor, 10, "World"),  # Invalid position
        ]
        
        macro = MacroCommand(commands, "Add greeting with error")
        
        with pytest.raises(ValueError):
            macro.execute()
        
        # Should have undone the first command
        assert self.editor.content == ""
    
    def test_add_command_to_unexecuted_macro(self) -> None:
        """Test adding command to unexecuted macro."""
        macro = MacroCommand([], "Empty macro")
        cmd = InsertTextCommand(self.editor, 0, "Hello")
        
        macro.add_command(cmd)
        macro.execute()
        
        assert self.editor.content == "Hello"
    
    def test_add_command_to_executed_macro(self) -> None:
        """Test adding command to executed macro."""
        cmd1 = InsertTextCommand(self.editor, 0, "Hello")
        macro = MacroCommand([cmd1], "Simple macro")
        macro.execute()
        
        cmd2 = InsertTextCommand(self.editor, 5, " World")
        with pytest.raises(RuntimeError, match="Cannot add commands to a macro that has been executed"):
            macro.add_command(cmd2)
    
    def test_macro_description(self) -> None:
        """Test macro command description."""
        commands = [InsertTextCommand(self.editor, 0, "Hello")]
        macro = MacroCommand(commands, "Test macro")
        
        assert macro.get_description() == "Test macro"