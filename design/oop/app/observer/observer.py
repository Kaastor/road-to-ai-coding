"""Observer abstract base class for the Observer pattern."""

from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    """Abstract base class for observers in the Observer pattern.
    
    Observers implement the update method to receive notifications
    when the subject's state changes.
    """

    @abstractmethod
    def update(self, subject: Any, *args, **kwargs) -> None:
        """Update method called when the subject notifies observers.
        
        Args:
            subject: The subject that triggered the notification
            *args: Variable positional arguments with update data
            **kwargs: Variable keyword arguments with update data
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name/identifier of this observer."""
        pass