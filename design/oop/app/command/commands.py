"""Concrete command implementations for text editor operations."""

from .command_interface import Command
from .text_editor import TextEditor, TextFormat, TextSegment


class InsertTextCommand(Command):
    """Command to insert text at a specific position."""
    
    def __init__(self, editor: TextEditor, position: int, text: str) -> None:
        """Initialize the insert command.
        
        Args:
            editor: The text editor instance to operate on
            position: Position where to insert the text
            text: Text to insert
        """
        self._editor = editor
        self._position = position
        self._text = text
        self._executed = False
    
    def execute(self) -> None:
        """Execute the insert operation."""
        if self._executed:
            raise RuntimeError("Command has already been executed")
        
        self._editor.insert_text(self._position, self._text)
        self._executed = True
    
    def undo(self) -> None:
        """Undo the insert operation by deleting the inserted text."""
        if not self._executed:
            raise RuntimeError("Cannot undo command that hasn't been executed")
        
        self._editor.delete_text(self._position, len(self._text))
        self._executed = False
    
    def get_description(self) -> str:
        """Return description of the command."""
        return f"Insert '{self._text}' at position {self._position}"


class DeleteTextCommand(Command):
    """Command to delete text from a specific position."""
    
    def __init__(self, editor: TextEditor, position: int, length: int) -> None:
        """Initialize the delete command.
        
        Args:
            editor: The text editor instance to operate on
            position: Starting position for deletion
            length: Number of characters to delete
        """
        self._editor = editor
        self._position = position
        self._length = length
        self._deleted_text: str = ""
        self._executed = False
    
    def execute(self) -> None:
        """Execute the delete operation."""
        if self._executed:
            raise RuntimeError("Command has already been executed")
        
        self._deleted_text = self._editor.delete_text(self._position, self._length)
        self._executed = True
    
    def undo(self) -> None:
        """Undo the delete operation by inserting the deleted text back."""
        if not self._executed:
            raise RuntimeError("Cannot undo command that hasn't been executed")
        
        self._editor.insert_text(self._position, self._deleted_text)
        self._executed = False
    
    def get_description(self) -> str:
        """Return description of the command."""
        if self._executed:
            return f"Delete '{self._deleted_text}' from position {self._position}"
        return f"Delete {self._length} characters from position {self._position}"


class FormatTextCommand(Command):
    """Command to apply formatting to a text range."""
    
    def __init__(self, editor: TextEditor, position: int, length: int, format_type: TextFormat) -> None:
        """Initialize the format command.
        
        Args:
            editor: The text editor instance to operate on
            position: Starting position for formatting
            length: Length of text to format
            format_type: Type of formatting to apply
        """
        self._editor = editor
        self._position = position
        self._length = length
        self._format_type = format_type
        self._previous_segments: list[TextSegment] = []
        self._executed = False
    
    def execute(self) -> None:
        """Execute the format operation."""
        if self._executed:
            raise RuntimeError("Command has already been executed")
        
        self._previous_segments = self._editor.format_text(
            self._position, self._length, self._format_type
        )
        self._executed = True
    
    def undo(self) -> None:
        """Undo the format operation by restoring previous formatting."""
        if not self._executed:
            raise RuntimeError("Cannot undo command that hasn't been executed")
        
        # Remove current formatting in the range
        end_position = self._position + self._length
        self._editor._remove_formatting_in_range(self._position, end_position)
        
        # Restore previous formatting
        if self._previous_segments:
            self._editor.restore_formatting(self._previous_segments)
        
        self._executed = False
    
    def get_description(self) -> str:
        """Return description of the command."""
        return f"Apply {self._format_type.value} formatting to position {self._position}-{self._position + self._length}"


class MacroCommand(Command):
    """Command that executes multiple commands as a single unit."""
    
    def __init__(self, commands: list[Command], description: str) -> None:
        """Initialize the macro command.
        
        Args:
            commands: List of commands to execute as a group
            description: Description of the macro operation
        """
        self._commands = commands.copy()
        self._description = description
        self._executed_count = 0
    
    def execute(self) -> None:
        """Execute all commands in sequence."""
        for i, command in enumerate(self._commands[self._executed_count:], self._executed_count):
            try:
                command.execute()
                self._executed_count = i + 1
            except Exception as e:
                # If any command fails, we need to undo the ones that succeeded
                self._undo_partial_execution()
                raise e
    
    def undo(self) -> None:
        """Undo all executed commands in reverse order."""
        self._undo_partial_execution()
    
    def _undo_partial_execution(self) -> None:
        """Undo commands that were successfully executed."""
        for command in reversed(self._commands[:self._executed_count]):
            try:
                command.undo()
            except Exception:
                # Log the error but continue undoing other commands
                pass
        self._executed_count = 0
    
    def get_description(self) -> str:
        """Return description of the macro command."""
        return self._description
    
    def add_command(self, command: Command) -> None:
        """Add a command to the macro.
        
        Args:
            command: Command to add
            
        Raises:
            RuntimeError: If macro has already been executed
        """
        if self._executed_count > 0:
            raise RuntimeError("Cannot add commands to a macro that has been executed")
        self._commands.append(command)