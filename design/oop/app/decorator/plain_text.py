"""
Concrete implementation of a plain text component.
"""

from .text_component import TextComponent


class PlainText(TextComponent):
    """
    Concrete implementation of TextComponent for plain text.
    
    This class represents the base text object that can be decorated
    with various formatting options.
    """
    
    def __init__(self, content: str) -> None:
        """
        Initialize the plain text with content.
        
        Args:
            content: The text content to store.
        """
        self._content = content
    
    def render(self) -> str:
        """
        Render the plain text without any formatting.
        
        Returns:
            str: The plain text content.
        """
        return self._content
    
    def get_content(self) -> str:
        """
        Get the raw text content.
        
        Returns:
            str: The plain text content.
        """
        return self._content