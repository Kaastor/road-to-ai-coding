"""Base Command interface for the Command pattern."""

from abc import ABC, abstractmethod


class Command(ABC):
    """Abstract base class defining the command interface.
    
    All concrete commands must implement execute() and undo() methods
    to support reversible operations.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command operation."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command operation, reversing its effects."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of the command."""
        pass