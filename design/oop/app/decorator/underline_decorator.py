"""
Underline text decorator implementation.
"""

from .text_decorator import TextDecorator
from .text_component import TextComponent


class UnderlineDecorator(TextDecorator):
    """
    Decorator that adds underline formatting to text.
    
    This decorator wraps text with HTML-like underline tags to indicate
    underlined formatting.
    """
    
    def __init__(self, component: TextComponent) -> None:
        """
        Initialize the underline decorator.
        
        Args:
            component: The TextComponent to decorate with underline formatting.
        """
        super().__init__(component)
    
    def render(self) -> str:
        """
        Render the text with underline formatting.
        
        Returns:
            str: The text wrapped with underline tags.
        """
        return f"<u>{self._component.render()}</u>"