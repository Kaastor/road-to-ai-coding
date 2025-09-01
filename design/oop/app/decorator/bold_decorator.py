"""
Bold text decorator implementation.
"""

from .text_decorator import TextDecorator
from .text_component import TextComponent


class BoldDecorator(TextDecorator):
    """
    Decorator that adds bold formatting to text.
    
    This decorator wraps text with HTML-like bold tags to indicate
    bold formatting.
    """
    
    def __init__(self, component: TextComponent) -> None:
        """
        Initialize the bold decorator.
        
        Args:
            component: The TextComponent to decorate with bold formatting.
        """
        super().__init__(component)
    
    def render(self) -> str:
        """
        Render the text with bold formatting.
        
        Returns:
            str: The text wrapped with bold tags.
        """
        return f"<b>{self._component.render()}</b>"