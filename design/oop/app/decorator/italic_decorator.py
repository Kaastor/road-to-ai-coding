"""
Italic text decorator implementation.
"""

from .text_decorator import TextDecorator
from .text_component import TextComponent


class ItalicDecorator(TextDecorator):
    """
    Decorator that adds italic formatting to text.
    
    This decorator wraps text with HTML-like italic tags to indicate
    italic formatting.
    """
    
    def __init__(self, component: TextComponent) -> None:
        """
        Initialize the italic decorator.
        
        Args:
            component: The TextComponent to decorate with italic formatting.
        """
        super().__init__(component)
    
    def render(self) -> str:
        """
        Render the text with italic formatting.
        
        Returns:
            str: The text wrapped with italic tags.
        """
        return f"<i>{self._component.render()}</i>"