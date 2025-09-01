"""Demonstration of the Factory Method Pattern for Shape Creation."""

import logging

from .drawing_app import DrawingApp
from .custom_shapes import RectangleFactory, HexagonFactory


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


def main() -> None:
    """Demonstrate the Factory Method Pattern."""
    setup_logging()
    
    print("=== Factory Method Pattern Demo ===\n")
    
    # Create drawing application
    app = DrawingApp()
    
    print("1. Adding built-in shapes:")
    app.add_shape('circle', radius=5.0)
    app.add_shape('square', side=4.0)
    app.add_shape('triangle', base=6.0, height=8.0)
    
    print(f"\nShapes in drawing:")
    for shape_desc in app.list_shapes():
        print(f"  - {shape_desc}")
    
    print(f"\nTotal area (polymorphic computation): {app.compute_total_area():.2f}")
    
    # Demonstrate extensibility with custom shapes
    print("\n2. Extending with custom shapes:")
    app.add_custom_shape_factory('rectangle', RectangleFactory())
    app.add_custom_shape_factory('hexagon', HexagonFactory())
    
    app.add_shape('rectangle', width=3.0, height=7.0)
    app.add_shape('hexagon', side=2.5)
    
    print(f"\nAvailable shape types: {app.get_available_shape_types()}")
    
    print(f"\nUpdated drawing summary:")
    print(app.render_summary())
    
    # Demonstrate error handling
    print("\n3. Error handling:")
    try:
        app.add_shape('nonexistent_shape', param=1.0)
    except ValueError as e:
        print(f"Expected error: {e}")
    
    try:
        app.add_shape('circle')  # Missing required parameter
    except ValueError as e:
        print(f"Expected error: {e}")
    
    print(f"\nFinal total area: {app.compute_total_area():.2f}")


if __name__ == "__main__":
    main()