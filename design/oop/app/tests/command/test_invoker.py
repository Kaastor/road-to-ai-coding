"""Tests for TextEditorInvoker class."""

import pytest
from unittest.mock import Mock
from app.command.invoker import TextEditorInvoker
from app.command.command_interface import Command
from app.command.commands import InsertTextCommand, DeleteTextCommand
from app.command.text_editor import TextEditor


class MockCommand(Command):
    """Mock command for testing purposes."""
    
    def __init__(self, description: str = "Mock command", should_fail: bool = False) -> None:
        self.description = description
        self.should_fail = should_fail
        self.executed = False
        self.undone = False
    
    def execute(self) -> None:
        if self.should_fail:
            raise RuntimeError("Mock command execution failed")
        self.executed = True
        self.undone = False
    
    def undo(self) -> None:
        if self.should_fail:
            raise RuntimeError("Mock command undo failed")
        self.executed = False
        self.undone = True
    
    def get_description(self) -> str:
        return self.description


class TestTextEditorInvoker:
    """Test cases for TextEditorInvoker."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.invoker = TextEditorInvoker()
    
    def test_initial_state(self) -> None:
        """Test invoker initial state."""
        assert not self.invoker.can_undo()
        assert not self.invoker.can_redo()
        assert self.invoker.get_undo_stack_size() == 0
        assert self.invoker.get_redo_stack_size() == 0
        assert self.invoker.get_last_command_description() is None
        assert self.invoker.get_next_redo_description() is None
    
    def test_execute_command(self) -> None:
        """Test executing a command."""
        cmd = MockCommand("Test command")
        self.invoker.execute_command(cmd)
        
        assert cmd.executed
        assert self.invoker.can_undo()
        assert not self.invoker.can_redo()
        assert self.invoker.get_undo_stack_size() == 1
        assert self.invoker.get_last_command_description() == "Test command"
    
    def test_execute_multiple_commands(self) -> None:
        """Test executing multiple commands."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        
        self.invoker.execute_command(cmd1)
        self.invoker.execute_command(cmd2)
        
        assert self.invoker.get_undo_stack_size() == 2
        assert self.invoker.get_last_command_description() == "Command 2"
    
    def test_execute_command_failure(self) -> None:
        """Test executing a failing command."""
        cmd = MockCommand("Failing command", should_fail=True)
        
        with pytest.raises(RuntimeError, match="Mock command execution failed"):
            self.invoker.execute_command(cmd)
        
        assert not cmd.executed
        assert self.invoker.get_undo_stack_size() == 0
    
    def test_undo_command(self) -> None:
        """Test undoing a command."""
        cmd = MockCommand("Test command")
        self.invoker.execute_command(cmd)
        
        success = self.invoker.undo()
        
        assert success
        assert cmd.undone
        assert not self.invoker.can_undo()
        assert self.invoker.can_redo()
        assert self.invoker.get_undo_stack_size() == 0
        assert self.invoker.get_redo_stack_size() == 1
        assert self.invoker.get_next_redo_description() == "Test command"
    
    def test_undo_no_commands(self) -> None:
        """Test undoing when no commands available."""
        success = self.invoker.undo()
        assert not success
    
    def test_undo_failure(self) -> None:
        """Test undoing a command that fails to undo."""
        cmd = MockCommand("Test command")
        self.invoker.execute_command(cmd)
        
        # Make undo fail
        cmd.should_fail = True
        
        with pytest.raises(RuntimeError, match="Mock command undo failed"):
            self.invoker.undo()
        
        # Command should still be in undo stack
        assert self.invoker.get_undo_stack_size() == 1
        assert not self.invoker.can_redo()
    
    def test_redo_command(self) -> None:
        """Test redoing a command."""
        cmd = MockCommand("Test command")
        self.invoker.execute_command(cmd)
        self.invoker.undo()
        
        success = self.invoker.redo()
        
        assert success
        assert cmd.executed
        assert self.invoker.can_undo()
        assert not self.invoker.can_redo()
        assert self.invoker.get_undo_stack_size() == 1
        assert self.invoker.get_redo_stack_size() == 0
    
    def test_redo_no_commands(self) -> None:
        """Test redoing when no commands available."""
        success = self.invoker.redo()
        assert not success
    
    def test_redo_failure(self) -> None:
        """Test redoing a command that fails to execute."""
        cmd = MockCommand("Test command")
        self.invoker.execute_command(cmd)
        self.invoker.undo()
        
        # Make redo fail
        cmd.should_fail = True
        
        with pytest.raises(RuntimeError, match="Mock command execution failed"):
            self.invoker.redo()
        
        # Command should still be in redo stack
        assert self.invoker.get_redo_stack_size() == 1
        assert not self.invoker.can_undo()
    
    def test_new_command_clears_redo_stack(self) -> None:
        """Test that executing new command clears redo stack."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        
        self.invoker.execute_command(cmd1)
        self.invoker.undo()
        
        assert self.invoker.can_redo()
        
        self.invoker.execute_command(cmd2)
        
        assert not self.invoker.can_redo()
        assert self.invoker.get_redo_stack_size() == 0
    
    def test_clear_history(self) -> None:
        """Test clearing command history."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        
        self.invoker.execute_command(cmd1)
        self.invoker.execute_command(cmd2)
        self.invoker.undo()
        
        assert self.invoker.can_undo()
        assert self.invoker.can_redo()
        
        self.invoker.clear_history()
        
        assert not self.invoker.can_undo()
        assert not self.invoker.can_redo()
        assert self.invoker.get_undo_stack_size() == 0
        assert self.invoker.get_redo_stack_size() == 0
    
    def test_history_summary(self) -> None:
        """Test getting history summary."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        cmd3 = MockCommand("Command 3")
        
        self.invoker.execute_command(cmd1)
        self.invoker.execute_command(cmd2)
        self.invoker.execute_command(cmd3)
        self.invoker.undo()  # Move cmd3 to redo stack
        
        history = self.invoker.get_history_summary()
        
        assert history['undo'] == ["Command 2", "Command 1"]  # Most recent first
        assert history['redo'] == ["Command 3"]
    
    def test_max_history_limit(self) -> None:
        """Test that history respects max limit."""
        invoker = TextEditorInvoker(max_history=2)
        
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        cmd3 = MockCommand("Command 3")
        
        invoker.execute_command(cmd1)
        invoker.execute_command(cmd2)
        invoker.execute_command(cmd3)
        
        # Should only have the last 2 commands
        assert invoker.get_undo_stack_size() == 2
        assert invoker.get_last_command_description() == "Command 3"
        
        # Undo twice should not give us Command 1
        invoker.undo()  # Command 3
        invoker.undo()  # Command 2
        success = invoker.undo()  # Should fail
        
        assert not success
    
    def test_execute_multiple_commands_batch(self) -> None:
        """Test executing multiple commands in a batch."""
        editor = TextEditor()
        commands = [
            InsertTextCommand(editor, 0, "Hello"),
            InsertTextCommand(editor, 5, " World"),
        ]
        
        self.invoker.execute_multiple_commands(commands)
        
        assert editor.content == "Hello World"
        assert self.invoker.get_undo_stack_size() == 2
    
    def test_execute_multiple_commands_batch_failure(self) -> None:
        """Test executing multiple commands batch with failure."""
        editor = TextEditor()
        commands = [
            InsertTextCommand(editor, 0, "Hello"),
            InsertTextCommand(editor, 10, "World"),  # This will fail
        ]
        
        with pytest.raises(ValueError):
            self.invoker.execute_multiple_commands(commands)
        
        # Should have rolled back the first command
        assert editor.content == ""
        assert self.invoker.get_undo_stack_size() == 0
    
    def test_execute_multiple_commands_rollback_failure(self) -> None:
        """Test batch execution with rollback failure."""
        # Create a mock command that fails during undo
        failing_undo_cmd = Mock(spec=Command)
        failing_undo_cmd.execute.return_value = None
        failing_undo_cmd.undo.side_effect = RuntimeError("Undo failed")
        failing_undo_cmd.get_description.return_value = "Failing undo command"
        
        # Create a command that fails execution
        failing_exec_cmd = Mock(spec=Command)
        failing_exec_cmd.execute.side_effect = RuntimeError("Execution failed")
        failing_exec_cmd.get_description.return_value = "Failing exec command"
        
        commands = [failing_undo_cmd, failing_exec_cmd]
        
        # Should still raise the original execution error
        with pytest.raises(RuntimeError, match="Execution failed"):
            self.invoker.execute_multiple_commands(commands)
        
        # The failing undo command should have been executed once
        failing_undo_cmd.execute.assert_called_once()
        failing_undo_cmd.undo.assert_called_once()