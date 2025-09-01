"""Tests for the Factory Method Pattern implementation."""

import math
import pytest
from unittest.mock import patch

from app.factory.shapes import Circle, Square, Triangle
from app.factory.factory import (
    CircleFactory, SquareFactory, TriangleFactory,
    ShapeFactoryRegistry, default_registry
)
from app.factory.drawing_app import DrawingApp
from app.factory.custom_shapes import Rectangle, Hexagon, RectangleFactory, HexagonFactory


class TestShapes:
    """Test shape implementations."""
    
    def test_circle_area(self):
        """Test circle area calculation."""
        circle = Circle(radius=5.0)
        expected_area = math.pi * 25
        assert abs(circle.area() - expected_area) < 1e-10
        assert circle.get_name() == "Circle"
    
    def test_square_area(self):
        """Test square area calculation."""
        square = Square(side=4.0)
        assert square.area() == 16.0
        assert square.get_name() == "Square"
    
    def test_triangle_area(self):
        """Test triangle area calculation."""
        triangle = Triangle(base=6.0, height=8.0)
        assert triangle.area() == 24.0
        assert triangle.get_name() == "Triangle"
    
    def test_shape_string_representation(self):
        """Test shape string representation."""
        circle = Circle(radius=2.0)
        expected = f"Circle (area: {math.pi * 4:.2f})"
        assert str(circle) == expected


class TestFactories:
    """Test factory implementations."""
    
    def test_circle_factory(self):
        """Test circle factory."""
        factory = CircleFactory()
        circle = factory.create_shape(radius=3.0)
        assert isinstance(circle, Circle)
        assert circle.radius == 3.0
        
        with pytest.raises(ValueError, match="Circle requires 'radius' parameter"):
            factory.create_shape()
    
    def test_square_factory(self):
        """Test square factory."""
        factory = SquareFactory()
        square = factory.create_shape(side=5.0)
        assert isinstance(square, Square)
        assert square.side == 5.0
        
        with pytest.raises(ValueError, match="Square requires 'side' parameter"):
            factory.create_shape()
    
    def test_triangle_factory(self):
        """Test triangle factory."""
        factory = TriangleFactory()
        triangle = factory.create_shape(base=4.0, height=6.0)
        assert isinstance(triangle, Triangle)
        assert triangle.base == 4.0
        assert triangle.height == 6.0
        
        with pytest.raises(ValueError, match="Triangle requires 'base' and 'height' parameters"):
            factory.create_shape(base=4.0)


class TestShapeFactoryRegistry:
    """Test shape factory registry."""
    
    def test_registry_create_shapes(self):
        """Test registry can create all built-in shapes."""
        registry = ShapeFactoryRegistry()
        
        circle = registry.create_shape('circle', radius=2.0)
        assert isinstance(circle, Circle)
        
        square = registry.create_shape('square', side=3.0)
        assert isinstance(square, Square)
        
        triangle = registry.create_shape('triangle', base=4.0, height=5.0)
        assert isinstance(triangle, Triangle)
    
    def test_registry_case_insensitive(self):
        """Test registry is case insensitive."""
        registry = ShapeFactoryRegistry()
        
        circle = registry.create_shape('CIRCLE', radius=2.0)
        assert isinstance(circle, Circle)
        
        square = registry.create_shape('Square', side=3.0)
        assert isinstance(square, Square)
    
    def test_registry_unknown_shape(self):
        """Test registry raises error for unknown shapes."""
        registry = ShapeFactoryRegistry()
        
        with pytest.raises(ValueError, match="Unknown shape type 'pentagon'"):
            registry.create_shape('pentagon', side=5.0)
    
    def test_registry_extensibility(self):
        """Test registry can be extended with custom shapes."""
        registry = ShapeFactoryRegistry()
        registry.register_factory('rectangle', RectangleFactory())
        
        rectangle = registry.create_shape('rectangle', width=4.0, height=6.0)
        assert isinstance(rectangle, Rectangle)
        assert 'rectangle' in registry.get_available_types()


class TestDrawingApp:
    """Test drawing application."""
    
    def test_add_shapes(self):
        """Test adding shapes to drawing."""
        app = DrawingApp()
        
        app.add_shape('circle', radius=3.0)
        app.add_shape('square', side=4.0)
        app.add_shape('triangle', base=5.0, height=6.0)
        
        assert len(app.shapes) == 3
        assert isinstance(app.shapes[0], Circle)
        assert isinstance(app.shapes[1], Square)
        assert isinstance(app.shapes[2], Triangle)
    
    def test_compute_total_area(self):
        """Test polymorphic area computation."""
        app = DrawingApp()
        
        app.add_shape('circle', radius=2.0)  # π * 4
        app.add_shape('square', side=3.0)    # 9
        app.add_shape('triangle', base=4.0, height=5.0)  # 10
        
        expected_total = math.pi * 4 + 9 + 10
        assert abs(app.compute_total_area() - expected_total) < 1e-10
    
    def test_get_shape_areas(self):
        """Test getting individual shape areas."""
        app = DrawingApp()
        
        app.add_shape('square', side=4.0)
        app.add_shape('triangle', base=6.0, height=8.0)
        
        areas = app.get_shape_areas()
        assert areas == [16.0, 24.0]
    
    def test_clear_shapes(self):
        """Test clearing shapes from drawing."""
        app = DrawingApp()
        
        app.add_shape('circle', radius=1.0)
        app.add_shape('square', side=2.0)
        assert len(app.shapes) == 2
        
        app.clear_shapes()
        assert len(app.shapes) == 0
    
    def test_custom_shape_integration(self):
        """Test integrating custom shapes."""
        app = DrawingApp()
        
        app.add_custom_shape_factory('rectangle', RectangleFactory())
        app.add_custom_shape_factory('hexagon', HexagonFactory())
        
        app.add_shape('rectangle', width=5.0, height=3.0)
        app.add_shape('hexagon', side=2.0)
        
        assert len(app.shapes) == 2
        assert isinstance(app.shapes[0], Rectangle)
        assert isinstance(app.shapes[1], Hexagon)
    
    def test_render_summary_empty(self):
        """Test summary rendering for empty drawing."""
        app = DrawingApp()
        assert app.render_summary() == "Drawing is empty"
    
    def test_render_summary_with_shapes(self):
        """Test summary rendering with shapes."""
        app = DrawingApp()
        app.add_shape('square', side=2.0)
        
        summary = app.render_summary()
        assert "Drawing contains 1 shapes:" in summary
        assert "Square (area: 4.00)" in summary
        assert "Total area: 4.00" in summary
    
    @patch('app.factory.drawing_app.logging.getLogger')
    def test_logging_integration(self, mock_get_logger):
        """Test logging integration."""
        mock_logger = mock_get_logger.return_value
        
        app = DrawingApp()
        app.add_shape('circle', radius=1.0)
        
        mock_logger.info.assert_called()


class TestCustomShapes:
    """Test custom shape implementations."""
    
    def test_rectangle_area(self):
        """Test rectangle area calculation."""
        rectangle = Rectangle(width=4.0, height=6.0)
        assert rectangle.area() == 24.0
        assert rectangle.get_name() == "Rectangle"
    
    def test_hexagon_area(self):
        """Test hexagon area calculation."""
        hexagon = Hexagon(side=2.0)
        expected_area = (3 * math.sqrt(3) / 2) * 4
        assert abs(hexagon.area() - expected_area) < 1e-10
        assert hexagon.get_name() == "Hexagon"
    
    def test_rectangle_factory(self):
        """Test rectangle factory."""
        factory = RectangleFactory()
        rectangle = factory.create_shape(width=3.0, height=5.0)
        assert isinstance(rectangle, Rectangle)
        
        with pytest.raises(ValueError):
            factory.create_shape(width=3.0)  # Missing height
    
    def test_hexagon_factory(self):
        """Test hexagon factory."""
        factory = HexagonFactory()
        hexagon = factory.create_shape(side=4.0)
        assert isinstance(hexagon, Hexagon)
        
        with pytest.raises(ValueError):
            factory.create_shape()  # Missing side