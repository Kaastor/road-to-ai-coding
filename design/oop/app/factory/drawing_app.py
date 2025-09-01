"""Drawing application demonstrating polymorphic area computation."""

from typing import List
import logging

from .shapes import Shape
from .factory import default_registry, ShapeFactory


class DrawingApp:
    """A drawing application that manages shapes and computes areas polymorphically."""
    
    def __init__(self) -> None:
        """Initialize the drawing application."""
        self.shapes: List[Shape] = []
        self.registry = default_registry
        self.logger = logging.getLogger(__name__)
    
    def add_shape(self, shape_type: str, **kwargs) -> None:
        """Add a shape to the drawing using the factory pattern."""
        try:
            shape = self.registry.create_shape(shape_type, **kwargs)
            self.shapes.append(shape)
            self.logger.info(f"Added {shape}")
        except ValueError as e:
            self.logger.error(f"Failed to create shape: {e}")
            raise
    
    def add_custom_shape_factory(self, shape_type: str, factory: ShapeFactory) -> None:
        """Register a custom shape factory for extensibility."""
        self.registry.register_factory(shape_type, factory)
        self.logger.info(f"Registered custom factory for '{shape_type}'")
    
    def compute_total_area(self) -> float:
        """Compute total area of all shapes polymorphically."""
        total = sum(shape.area() for shape in self.shapes)
        self.logger.info(f"Total area computed: {total:.2f}")
        return total
    
    def get_shape_areas(self) -> List[float]:
        """Get areas of all shapes using polymorphism."""
        return [shape.area() for shape in self.shapes]
    
    def list_shapes(self) -> List[str]:
        """List all shapes with their areas."""
        return [str(shape) for shape in self.shapes]
    
    def clear_shapes(self) -> None:
        """Clear all shapes from the drawing."""
        count = len(self.shapes)
        self.shapes.clear()
        self.logger.info(f"Cleared {count} shapes from drawing")
    
    def get_available_shape_types(self) -> List[str]:
        """Get list of available shape types."""
        return self.registry.get_available_types()
    
    def render_summary(self) -> str:
        """Render a summary of the drawing."""
        if not self.shapes:
            return "Drawing is empty"
        
        summary_lines = [
            f"Drawing contains {len(self.shapes)} shapes:",
            *[f"  - {shape}" for shape in self.shapes],
            f"Total area: {self.compute_total_area():.2f}"
        ]
        return "\n".join(summary_lines)