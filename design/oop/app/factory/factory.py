"""Factory Method Pattern implementation for shape creation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from .shapes import Shape, Circle, Square, Triangle


class ShapeFactory(ABC):
    """Abstract factory for creating shapes."""
    
    @abstractmethod
    def create_shape(self, **kwargs: Any) -> Shape:
        """Create a shape with given parameters."""
        pass


class CircleFactory(ShapeFactory):
    """Factory for creating circles."""
    
    def create_shape(self, **kwargs: Any) -> Circle:
        """Create a circle with radius parameter."""
        radius = kwargs.get('radius')
        if radius is None:
            raise ValueError("Circle requires 'radius' parameter")
        return Circle(radius)


class SquareFactory(ShapeFactory):
    """Factory for creating squares."""
    
    def create_shape(self, **kwargs: Any) -> Square:
        """Create a square with side parameter."""
        side = kwargs.get('side')
        if side is None:
            raise ValueError("Square requires 'side' parameter")
        return Square(side)


class TriangleFactory(ShapeFactory):
    """Factory for creating triangles."""
    
    def create_shape(self, **kwargs: Any) -> Triangle:
        """Create a triangle with base and height parameters."""
        base = kwargs.get('base')
        height = kwargs.get('height')
        if base is None or height is None:
            raise ValueError("Triangle requires 'base' and 'height' parameters")
        return Triangle(base, height)


class ShapeFactoryRegistry:
    """Registry for shape factories supporting extensibility."""
    
    def __init__(self) -> None:
        """Initialize registry with built-in factories."""
        self._factories: Dict[str, ShapeFactory] = {
            'circle': CircleFactory(),
            'square': SquareFactory(),
            'triangle': TriangleFactory(),
        }
    
    def register_factory(self, shape_type: str, factory: ShapeFactory) -> None:
        """Register a new shape factory."""
        self._factories[shape_type.lower()] = factory
    
    def create_shape(self, shape_type: str, **kwargs: Any) -> Shape:
        """Create a shape using the appropriate factory."""
        factory = self._factories.get(shape_type.lower())
        if factory is None:
            available_types = list(self._factories.keys())
            raise ValueError(f"Unknown shape type '{shape_type}'. Available types: {available_types}")
        
        return factory.create_shape(**kwargs)
    
    def get_available_types(self) -> list[str]:
        """Get list of available shape types."""
        return list(self._factories.keys())


# Default registry instance
default_registry = ShapeFactoryRegistry()