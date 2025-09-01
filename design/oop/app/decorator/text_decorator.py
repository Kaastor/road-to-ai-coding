"""
Abstract base class for text decorators.
"""

from abc import abstractmethod
from .text_component import TextComponent


class TextDecorator(TextComponent):
    """
    Abstract base class for text decorators.
    
    This class implements the Decorator pattern by wrapping a TextComponent
    and delegating calls to it while potentially adding additional functionality.
    """
    
    def __init__(self, component: TextComponent) -> None:
        """
        Initialize the decorator with a text component to wrap.
        
        Args:
            component: The TextComponent to decorate.
        """
        self._component = component
    
    @abstractmethod
    def render(self) -> str:
        """
        Render the decorated text.
        
        Returns:
            str: The formatted text string.
        """
        pass
    
    def get_content(self) -> str:
        """
        Get the raw text content from the wrapped component.
        
        Returns:
            str: The plain text content.
        """
        return self._component.get_content()