"""Subject class for the Observer pattern with thread safety."""

import logging
import threading
from typing import Any, Set
from .observer import Observer


class Subject:
    """Subject class that maintains a list of observers and notifies them of state changes.
    
    This implementation is thread-safe using locks to handle concurrent access
    to the observer list and notifications.
    """

    def __init__(self, name: str = "Subject") -> None:
        """Initialize the subject with an empty observer list.
        
        Args:
            name: Name identifier for the subject
        """
        self._observers: Set[Observer] = set()
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._name = name
        self._logger = logging.getLogger(f"{__name__}.{self._name}")

    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject.
        
        Args:
            observer: Observer to attach
            
        Raises:
            TypeError: If observer doesn't implement Observer interface
        """
        if not isinstance(observer, Observer):
            raise TypeError(f"Observer must implement Observer interface, got {type(observer)}")
        
        with self._lock:
            if observer not in self._observers:
                self._observers.add(observer)
                self._logger.info(f"Observer '{observer.name}' attached to subject '{self._name}'")
            else:
                self._logger.debug(f"Observer '{observer.name}' already attached to subject '{self._name}'")

    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject.
        
        Args:
            observer: Observer to detach
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                self._logger.info(f"Observer '{observer.name}' detached from subject '{self._name}'")
            else:
                self._logger.debug(f"Observer '{observer.name}' not found in subject '{self._name}'")

    def notify(self, *args, **kwargs) -> None:
        """Notify all attached observers of a state change.
        
        Args:
            *args: Variable positional arguments to pass to observers
            **kwargs: Variable keyword arguments to pass to observers
        """
        with self._lock:
            # Create a copy of observers to avoid modification during iteration
            observers_copy = self._observers.copy()
            observer_count = len(observers_copy)
        
        if observer_count == 0:
            self._logger.debug(f"No observers to notify for subject '{self._name}'")
            return
        
        self._logger.info(f"Notifying {observer_count} observers for subject '{self._name}'")
        
        # Notify observers outside the lock to avoid deadlocks
        failed_notifications = []
        for observer in observers_copy:
            try:
                observer.update(self, *args, **kwargs)
            except Exception as e:
                failed_notifications.append((observer.name, str(e)))
                self._logger.error(f"Failed to notify observer '{observer.name}': {e}")
        
        if failed_notifications:
            self._logger.warning(f"Failed to notify {len(failed_notifications)} observers")

    def get_observer_count(self) -> int:
        """Get the current number of attached observers.
        
        Returns:
            Number of attached observers
        """
        with self._lock:
            return len(self._observers)

    def get_observer_names(self) -> list[str]:
        """Get names of all attached observers.
        
        Returns:
            List of observer names
        """
        with self._lock:
            return [observer.name for observer in self._observers]

    @property
    def name(self) -> str:
        """Get the subject's name."""
        return self._name