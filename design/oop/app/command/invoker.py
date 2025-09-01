"""Text editor invoker with undo/redo functionality."""

import logging
from collections import deque
from typing import Optional

from .command_interface import Command


class TextEditorInvoker:
    """Invoker class that manages command execution and maintains undo/redo stacks.
    
    This class acts as the invoker in the Command pattern, providing
    an interface for executing commands and managing their history
    for undo/redo operations.
    """
    
    def __init__(self, max_history: int = 100) -> None:
        """Initialize the invoker with empty command history.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self._undo_stack: deque[Command] = deque(maxlen=max_history)
        self._redo_stack: deque[Command] = deque(maxlen=max_history)
        self._max_history = max_history
        self._logger = logging.getLogger(__name__)
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to the undo stack.
        
        Args:
            command: The command to execute
            
        Raises:
            Exception: If command execution fails
        """
        try:
            command.execute()
            self._undo_stack.append(command)
            # Clear redo stack since we executed a new command
            self._redo_stack.clear()
            self._logger.info(f"Executed command: {command.get_description()}")
        except Exception as e:
            self._logger.error(f"Failed to execute command: {command.get_description()}: {e}")
            raise
    
    def undo(self) -> bool:
        """Undo the last executed command.
        
        Returns:
            True if undo was successful, False if no commands to undo
        """
        if not self._undo_stack:
            self._logger.warning("No commands to undo")
            return False
        
        command = self._undo_stack.pop()
        try:
            command.undo()
            self._redo_stack.append(command)
            self._logger.info(f"Undid command: {command.get_description()}")
            return True
        except Exception as e:
            # If undo fails, put the command back on the undo stack
            self._undo_stack.append(command)
            self._logger.error(f"Failed to undo command: {command.get_description()}: {e}")
            raise
    
    def redo(self) -> bool:
        """Redo the last undone command.
        
        Returns:
            True if redo was successful, False if no commands to redo
        """
        if not self._redo_stack:
            self._logger.warning("No commands to redo")
            return False
        
        command = self._redo_stack.pop()
        try:
            command.execute()
            self._undo_stack.append(command)
            self._logger.info(f"Redid command: {command.get_description()}")
            return True
        except Exception as e:
            # If redo fails, put the command back on the redo stack
            self._redo_stack.append(command)
            self._logger.error(f"Failed to redo command: {command.get_description()}: {e}")
            raise
    
    def can_undo(self) -> bool:
        """Check if there are commands available to undo.
        
        Returns:
            True if undo is possible, False otherwise
        """
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if there are commands available to redo.
        
        Returns:
            True if redo is possible, False otherwise
        """
        return len(self._redo_stack) > 0
    
    def get_undo_stack_size(self) -> int:
        """Get the number of commands in the undo stack."""
        return len(self._undo_stack)
    
    def get_redo_stack_size(self) -> int:
        """Get the number of commands in the redo stack."""
        return len(self._redo_stack)
    
    def get_last_command_description(self) -> Optional[str]:
        """Get the description of the last executed command.
        
        Returns:
            Description of the last command, or None if no commands executed
        """
        if self._undo_stack:
            return self._undo_stack[-1].get_description()
        return None
    
    def get_next_redo_description(self) -> Optional[str]:
        """Get the description of the next command that would be redone.
        
        Returns:
            Description of the next redo command, or None if no commands to redo
        """
        if self._redo_stack:
            return self._redo_stack[-1].get_description()
        return None
    
    def clear_history(self) -> None:
        """Clear both undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._logger.info("Cleared command history")
    
    def get_history_summary(self) -> dict[str, list[str]]:
        """Get a summary of the command history.
        
        Returns:
            Dictionary with 'undo' and 'redo' keys containing command descriptions
        """
        return {
            'undo': [cmd.get_description() for cmd in reversed(self._undo_stack)],
            'redo': [cmd.get_description() for cmd in reversed(self._redo_stack)]
        }
    
    def execute_multiple_commands(self, commands: list[Command]) -> None:
        """Execute multiple commands in sequence.
        
        If any command fails, all previously executed commands in this batch
        will be undone to maintain consistency.
        
        Args:
            commands: List of commands to execute
            
        Raises:
            Exception: If any command execution fails
        """
        executed_commands = []
        
        try:
            for command in commands:
                command.execute()
                executed_commands.append(command)
                self._undo_stack.append(command)
            
            # Clear redo stack since we executed new commands
            self._redo_stack.clear()
            self._logger.info(f"Executed {len(commands)} commands successfully")
            
        except Exception as e:
            # Undo all commands that were executed in this batch
            self._logger.error(f"Failed to execute command batch, rolling back {len(executed_commands)} commands")
            
            for command in reversed(executed_commands):
                try:
                    command.undo()
                    # Remove from undo stack
                    if self._undo_stack and self._undo_stack[-1] is command:
                        self._undo_stack.pop()
                except Exception as undo_error:
                    self._logger.error(f"Failed to rollback command during batch failure: {undo_error}")
            
            raise e