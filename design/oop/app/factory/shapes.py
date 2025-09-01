"""Shape abstract class and concrete implementations."""

import math
from abc import ABC, abstractmethod
from typing import Any


class Shape(ABC):
    """Abstract base class for all shapes."""
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize shape with parameters."""
        self._params = kwargs
    
    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the shape."""
        pass
    
    def __str__(self) -> str:
        """String representation of the shape."""
        return f"{self.get_name()} (area: {self.area():.2f})"


class Circle(Shape):
    """Circle shape implementation."""
    
    def __init__(self, radius: float) -> None:
        """Initialize circle with radius."""
        super().__init__(radius=radius)
        self.radius = radius
    
    def area(self) -> float:
        """Calculate circle area using π * r²."""
        return math.pi * self.radius ** 2
    
    def get_name(self) -> str:
        """Get shape name."""
        return "Circle"


class Square(Shape):
    """Square shape implementation."""
    
    def __init__(self, side: float) -> None:
        """Initialize square with side length."""
        super().__init__(side=side)
        self.side = side
    
    def area(self) -> float:
        """Calculate square area using side²."""
        return self.side ** 2
    
    def get_name(self) -> str:
        """Get shape name."""
        return "Square"


class Triangle(Shape):
    """Triangle shape implementation."""
    
    def __init__(self, base: float, height: float) -> None:
        """Initialize triangle with base and height."""
        super().__init__(base=base, height=height)
        self.base = base
        self.height = height
    
    def area(self) -> float:
        """Calculate triangle area using ½ * base * height."""
        return 0.5 * self.base * self.height
    
    def get_name(self) -> str:
        """Get shape name."""
        return "Triangle"