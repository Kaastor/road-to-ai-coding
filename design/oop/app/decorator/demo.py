"""
Demonstration of the Decorator pattern for text processing.

This script shows how to use the text decorators to compose
multiple formatting options dynamically.
"""

import logging
from .plain_text import PlainText
from .bold_decorator import BoldDecorator
from .italic_decorator import ItalicDecorator
from .underline_decorator import UnderlineDecorator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_decorator_pattern() -> None:
    """
    Demonstrate various combinations of text decorators.
    
    Shows how decorators can be composed dynamically to create
    different text formatting combinations.
    """
    logger.info("=== Text Decorator Pattern Demonstration ===")
    
    # Create base text
    plain_text = PlainText("Hello, World!")
    logger.info(f"Plain text: {plain_text.render()}")
    logger.info(f"Content: {plain_text.get_content()}")
    
    print("\n" + "="*50)
    
    # Single decorators
    logger.info("\n--- Single Decorators ---")
    
    bold_text = BoldDecorator(plain_text)
    logger.info(f"Bold text: {bold_text.render()}")
    
    italic_text = ItalicDecorator(plain_text)
    logger.info(f"Italic text: {italic_text.render()}")
    
    underline_text = UnderlineDecorator(plain_text)
    logger.info(f"Underline text: {underline_text.render()}")
    
    print("\n" + "="*50)
    
    # Double decorators
    logger.info("\n--- Double Decorators ---")
    
    bold_italic = ItalicDecorator(BoldDecorator(plain_text))
    logger.info(f"Bold + Italic: {bold_italic.render()}")
    
    bold_underline = UnderlineDecorator(BoldDecorator(plain_text))
    logger.info(f"Bold + Underline: {bold_underline.render()}")
    
    italic_underline = UnderlineDecorator(ItalicDecorator(plain_text))
    logger.info(f"Italic + Underline: {italic_underline.render()}")
    
    print("\n" + "="*50)
    
    # Triple decorator (all formatting)
    logger.info("\n--- Triple Decorator ---")
    
    all_formatting = UnderlineDecorator(
        ItalicDecorator(
            BoldDecorator(plain_text)
        )
    )
    logger.info(f"Bold + Italic + Underline: {all_formatting.render()}")
    logger.info(f"Original content preserved: {all_formatting.get_content()}")
    
    print("\n" + "="*50)
    
    # Different order of decoration
    logger.info("\n--- Different Decoration Order ---")
    
    different_order = BoldDecorator(
        UnderlineDecorator(
            ItalicDecorator(plain_text)
        )
    )
    logger.info(f"Italic + Underline + Bold: {different_order.render()}")
    
    print("\n" + "="*50)
    
    # Multiple texts with different decorations
    logger.info("\n--- Multiple Texts ---")
    
    texts = [
        ("Welcome", BoldDecorator(PlainText("Welcome"))),
        ("to the", ItalicDecorator(PlainText("to the"))),
        ("Decorator", UnderlineDecorator(PlainText("Decorator"))),
        ("Pattern", UnderlineDecorator(ItalicDecorator(BoldDecorator(PlainText("Pattern")))))
    ]
    
    sentence_parts = []
    for description, decorated_text in texts:
        logger.info(f"{description}: {decorated_text.render()}")
        sentence_parts.append(decorated_text.render())
    
    full_sentence = " ".join(sentence_parts)
    logger.info(f"\nComplete sentence: {full_sentence}")
    
    print("\n" + "="*50)
    logger.info("Demonstration completed successfully!")


def demonstrate_dynamic_composition() -> None:
    """
    Demonstrate dynamic composition of decorators based on user preferences.
    """
    logger.info("\n=== Dynamic Decorator Composition ===")
    
    # Simulate user preferences
    formatting_options = [
        {"bold": True, "italic": False, "underline": True},
        {"bold": False, "italic": True, "underline": False},
        {"bold": True, "italic": True, "underline": True},
        {"bold": False, "italic": False, "underline": False}
    ]
    
    base_text = "Dynamic Text"
    
    for i, options in enumerate(formatting_options, 1):
        text_component = PlainText(base_text)
        
        # Apply decorators based on options
        if options["bold"]:
            text_component = BoldDecorator(text_component)
        
        if options["italic"]:
            text_component = ItalicDecorator(text_component)
        
        if options["underline"]:
            text_component = UnderlineDecorator(text_component)
        
        logger.info(f"Configuration {i}: {options}")
        logger.info(f"Result: {text_component.render()}")
        print()


if __name__ == "__main__":
    demonstrate_decorator_pattern()
    demonstrate_dynamic_composition()