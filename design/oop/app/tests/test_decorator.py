"""
Comprehensive tests for the Decorator pattern implementation.
"""

import pytest
from app.decorator import (
    TextComponent,
    PlainText,
    TextDecorator,
    BoldDecorator,
    ItalicDecorator,
    UnderlineDecorator
)


class TestPlainText:
    """Test cases for the PlainText class."""
    
    def test_plain_text_creation(self):
        """Test creating a plain text object."""
        content = "Hello, World!"
        text = PlainText(content)
        
        assert text.render() == content
        assert text.get_content() == content
    
    def test_plain_text_empty_content(self):
        """Test plain text with empty content."""
        text = PlainText("")
        
        assert text.render() == ""
        assert text.get_content() == ""
    
    def test_plain_text_special_characters(self):
        """Test plain text with special characters."""
        content = "Hello! @#$%^&*() 123"
        text = PlainText(content)
        
        assert text.render() == content
        assert text.get_content() == content


class TestBoldDecorator:
    """Test cases for the BoldDecorator class."""
    
    def test_bold_decorator_single(self):
        """Test bold decorator on plain text."""
        plain_text = PlainText("Bold text")
        bold_text = BoldDecorator(plain_text)
        
        assert bold_text.render() == "<b>Bold text</b>"
        assert bold_text.get_content() == "Bold text"
    
    def test_bold_decorator_empty_text(self):
        """Test bold decorator with empty text."""
        plain_text = PlainText("")
        bold_text = BoldDecorator(plain_text)
        
        assert bold_text.render() == "<b></b>"
        assert bold_text.get_content() == ""
    
    def test_bold_decorator_preserves_content(self):
        """Test that bold decorator preserves original content."""
        original_content = "Test content"
        plain_text = PlainText(original_content)
        bold_text = BoldDecorator(plain_text)
        
        assert bold_text.get_content() == original_content


class TestItalicDecorator:
    """Test cases for the ItalicDecorator class."""
    
    def test_italic_decorator_single(self):
        """Test italic decorator on plain text."""
        plain_text = PlainText("Italic text")
        italic_text = ItalicDecorator(plain_text)
        
        assert italic_text.render() == "<i>Italic text</i>"
        assert italic_text.get_content() == "Italic text"
    
    def test_italic_decorator_empty_text(self):
        """Test italic decorator with empty text."""
        plain_text = PlainText("")
        italic_text = ItalicDecorator(plain_text)
        
        assert italic_text.render() == "<i></i>"
        assert italic_text.get_content() == ""


class TestUnderlineDecorator:
    """Test cases for the UnderlineDecorator class."""
    
    def test_underline_decorator_single(self):
        """Test underline decorator on plain text."""
        plain_text = PlainText("Underlined text")
        underline_text = UnderlineDecorator(plain_text)
        
        assert underline_text.render() == "<u>Underlined text</u>"
        assert underline_text.get_content() == "Underlined text"
    
    def test_underline_decorator_empty_text(self):
        """Test underline decorator with empty text."""
        plain_text = PlainText("")
        underline_text = UnderlineDecorator(plain_text)
        
        assert underline_text.render() == "<u></u>"
        assert underline_text.get_content() == ""


class TestDecoratorComposition:
    """Test cases for decorator composition."""
    
    def test_double_decoration_bold_italic(self):
        """Test combining bold and italic decorators."""
        plain_text = PlainText("Bold Italic")
        decorated_text = ItalicDecorator(BoldDecorator(plain_text))
        
        assert decorated_text.render() == "<i><b>Bold Italic</b></i>"
        assert decorated_text.get_content() == "Bold Italic"
    
    def test_double_decoration_italic_bold(self):
        """Test combining italic and bold decorators in different order."""
        plain_text = PlainText("Italic Bold")
        decorated_text = BoldDecorator(ItalicDecorator(plain_text))
        
        assert decorated_text.render() == "<b><i>Italic Bold</i></b>"
        assert decorated_text.get_content() == "Italic Bold"
    
    def test_triple_decoration_all_formats(self):
        """Test combining all three decorators."""
        plain_text = PlainText("All Formats")
        decorated_text = UnderlineDecorator(
            ItalicDecorator(
                BoldDecorator(plain_text)
            )
        )
        
        expected = "<u><i><b>All Formats</b></i></u>"
        assert decorated_text.render() == expected
        assert decorated_text.get_content() == "All Formats"
    
    def test_triple_decoration_different_order(self):
        """Test all decorators in a different order."""
        plain_text = PlainText("Different Order")
        decorated_text = BoldDecorator(
            UnderlineDecorator(
                ItalicDecorator(plain_text)
            )
        )
        
        expected = "<b><u><i>Different Order</i></u></b>"
        assert decorated_text.render() == expected
        assert decorated_text.get_content() == "Different Order"
    
    @pytest.mark.parametrize("decorators,expected_tags", [
        ([BoldDecorator], ["<b>", "</b>"]),
        ([ItalicDecorator], ["<i>", "</i>"]),
        ([UnderlineDecorator], ["<u>", "</u>"]),
        ([BoldDecorator, ItalicDecorator], ["<i>", "<b>", "</b>", "</i>"]),
        ([ItalicDecorator, BoldDecorator], ["<b>", "<i>", "</i>", "</b>"]),
        ([BoldDecorator, ItalicDecorator, UnderlineDecorator], 
         ["<u>", "<i>", "<b>", "</b>", "</i>", "</u>"])
    ])
    def test_decorator_combinations(self, decorators, expected_tags):
        """Test various decorator combinations produce expected tags."""
        content = "Test"
        text_component = PlainText(content)
        
        # Apply decorators in sequence
        for decorator_class in decorators:
            text_component = decorator_class(text_component)
        
        rendered = text_component.render()
        
        # Check that all expected tags are present
        for tag in expected_tags:
            assert tag in rendered
        
        # Check that content is preserved
        assert text_component.get_content() == content


class TestDecoratorInterface:
    """Test cases for the decorator interface and polymorphism."""
    
    def test_decorator_is_text_component(self):
        """Test that decorators implement TextComponent interface."""
        plain_text = PlainText("Test")
        bold_text = BoldDecorator(plain_text)
        
        assert isinstance(bold_text, TextComponent)
        assert hasattr(bold_text, 'render')
        assert hasattr(bold_text, 'get_content')
    
    def test_decorator_chain_is_text_component(self):
        """Test that decorator chains maintain TextComponent interface."""
        plain_text = PlainText("Test")
        decorated_text = UnderlineDecorator(
            ItalicDecorator(
                BoldDecorator(plain_text)
            )
        )
        
        assert isinstance(decorated_text, TextComponent)
        assert hasattr(decorated_text, 'render')
        assert hasattr(decorated_text, 'get_content')
    
    def test_decorators_can_decorate_other_decorators(self):
        """Test that decorators can wrap other decorators seamlessly."""
        base = PlainText("Base")
        first_decorator = BoldDecorator(base)
        second_decorator = ItalicDecorator(first_decorator)
        third_decorator = UnderlineDecorator(second_decorator)
        
        # Each level should be a valid TextComponent
        assert isinstance(first_decorator, TextComponent)
        assert isinstance(second_decorator, TextComponent)
        assert isinstance(third_decorator, TextComponent)
        
        # Content should be preserved at all levels
        assert first_decorator.get_content() == "Base"
        assert second_decorator.get_content() == "Base"
        assert third_decorator.get_content() == "Base"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_multiple_same_decorators(self):
        """Test applying the same decorator multiple times."""
        plain_text = PlainText("Double Bold")
        double_bold = BoldDecorator(BoldDecorator(plain_text))
        
        assert double_bold.render() == "<b><b>Double Bold</b></b>"
        assert double_bold.get_content() == "Double Bold"
    
    def test_long_text_content(self):
        """Test decorators with long text content."""
        long_content = "This is a very long piece of text " * 10
        plain_text = PlainText(long_content)
        decorated = BoldDecorator(ItalicDecorator(plain_text))
        
        expected = f"<b><i>{long_content}</i></b>"
        assert decorated.render() == expected
        assert decorated.get_content() == long_content
    
    def test_special_characters_in_content(self):
        """Test decorators with special characters."""
        special_content = "<>&\"'"
        plain_text = PlainText(special_content)
        decorated = BoldDecorator(plain_text)
        
        # Note: This test shows that our decorators don't escape HTML
        # In a real implementation, you might want to escape HTML entities
        assert decorated.render() == f"<b>{special_content}</b>"
        assert decorated.get_content() == special_content


class TestDynamicComposition:
    """Test dynamic composition scenarios."""
    
    def test_conditional_decoration(self):
        """Test applying decorators based on conditions."""
        content = "Conditional"
        text = PlainText(content)
        
        # Simulate conditional decoration
        make_bold = True
        make_italic = False
        make_underline = True
        
        if make_bold:
            text = BoldDecorator(text)
        if make_italic:
            text = ItalicDecorator(text)
        if make_underline:
            text = UnderlineDecorator(text)
        
        expected = "<u><b>Conditional</b></u>"
        assert text.render() == expected
        assert text.get_content() == content
    
    def test_decorator_removal_by_composition(self):
        """Test that we can selectively apply decorators."""
        content = "Selective"
        
        # Create different combinations
        combinations = [
            [],
            [BoldDecorator],
            [ItalicDecorator],
            [BoldDecorator, ItalicDecorator],
            [UnderlineDecorator, BoldDecorator, ItalicDecorator]
        ]
        
        for decorators in combinations:
            text = PlainText(content)
            
            for decorator_class in decorators:
                text = decorator_class(text)
            
            # Content should always be preserved
            assert text.get_content() == content
            
            # Rendering should contain the content
            assert content in text.render()