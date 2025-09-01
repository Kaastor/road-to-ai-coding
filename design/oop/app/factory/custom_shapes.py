"""Example custom shapes demonstrating extensibility."""

import math
from typing import Any

from .shapes import Shape
from .factory import ShapeFactory


class Rectangle(Shape):
    """Rectangle shape implementation."""
    
    def __init__(self, width: float, height: float) -> None:
        """Initialize rectangle with width and height."""
        super().__init__(width=width, height=height)
        self.width = width
        self.height = height
    
    def area(self) -> float:
        """Calculate rectangle area using width * height."""
        return self.width * self.height
    
    def get_name(self) -> str:
        """Get shape name."""
        return "Rectangle"


class Hexagon(Shape):
    """Regular hexagon shape implementation."""
    
    def __init__(self, side: float) -> None:
        """Initialize hexagon with side length."""
        super().__init__(side=side)
        self.side = side
    
    def area(self) -> float:
        """Calculate hexagon area using (3√3/2) * side²."""
        return (3 * math.sqrt(3) / 2) * self.side ** 2
    
    def get_name(self) -> str:
        """Get shape name."""
        return "Hexagon"


class RectangleFactory(ShapeFactory):
    """Factory for creating rectangles."""
    
    def create_shape(self, **kwargs: Any) -> Rectangle:
        """Create a rectangle with width and height parameters."""
        width = kwargs.get('width')
        height = kwargs.get('height')
        if width is None or height is None:
            raise ValueError("Rectangle requires 'width' and 'height' parameters")
        return Rectangle(width, height)


class HexagonFactory(ShapeFactory):
    """Factory for creating hexagons."""
    
    def create_shape(self, **kwargs: Any) -> Hexagon:
        """Create a hexagon with side parameter."""
        side = kwargs.get('side')
        if side is None:
            raise ValueError("Hexagon requires 'side' parameter")
        return Hexagon(side)