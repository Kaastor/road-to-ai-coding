"""
Abstract base class for text components in the Decorator pattern.
"""

from abc import ABC, abstractmethod


class TextComponent(ABC):
    """
    Abstract base class for text components.
    
    This class defines the interface that both concrete text objects
    and decorators must implement.
    """
    
    @abstractmethod
    def render(self) -> str:
        """
        Render the text with any applied formatting.
        
        Returns:
            str: The formatted text string.
        """
        pass
    
    @abstractmethod
    def get_content(self) -> str:
        """
        Get the raw text content without formatting.
        
        Returns:
            str: The plain text content.
        """
        pass