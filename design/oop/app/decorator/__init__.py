"""
Decorator Pattern implementation for text processing.

This module implements the Decorator pattern to add functionalities like bold, italic,
and underline to text objects. The decorators can be composed dynamically to create
various text formatting combinations.
"""

from .text_component import TextComponent
from .plain_text import PlainText
from .text_decorator import TextDecorator
from .bold_decorator import BoldDecorator
from .italic_decorator import ItalicDecorator
from .underline_decorator import UnderlineDecorator

__all__ = [
    'TextComponent',
    'PlainText',
    'TextDecorator',
    'BoldDecorator',
    'ItalicDecorator',
    'UnderlineDecorator'
]