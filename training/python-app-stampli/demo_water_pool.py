#!/usr/bin/env python3
"""Demo script to showcase the water in pool implementation."""

from app.app import water_in_pool


def visualize_pool(heights):
    """Create a simple ASCII visualization of the pool and trapped water."""
    if not heights:
        return "Empty pool"
    
    max_height = max(heights)
    lines = []
    
    # Build visualization from top to bottom
    for level in range(max_height, 0, -1):
        line = ""
        for i, height in enumerate(heights):
            if height >= level:
                line += "█"  # Bar
            else:
                # Check if water can be trapped at this level
                left_max = max(heights[:i+1]) if i >= 0 else 0
                right_max = max(heights[i:]) if i < len(heights) else 0
                water_level = min(left_max, right_max)
                
                if water_level >= level:
                    line += "~"  # Water
                else:
                    line += " "  # Air
        lines.append(line)
    
    return "\n".join(lines)


def main():
    """Run demo of water in pool calculations."""
    print("🌊 WATER IN POOL DEMO 🌊")
    print("=" * 50)
    
    test_cases = [
        ([3, 0, 2, 0, 4], "Example from problem"),
        ([1, 1, 1, 1], "Flat surface"),
        ([1, 2, 3, 4, 3, 2, 1, 1], "Mountain shape"),
        ([5, 1, 2, 3, 4, 5, 1, 1], "Valley with walls"),
        ([2, 0, 2], "Simple valley"),
        ([4, 2, 0, 3, 2, 5], "Complex pattern"),
    ]
    
    for heights, description in test_cases:
        water = water_in_pool(heights)
        print(f"\n📊 {description}")
        print(f"Heights: {heights}")
        print(f"Water trapped: {water} units")
        print("Visualization:")
        print(visualize_pool(heights))
        print("-" * 30)
    
    print(f"\n✅ All examples completed successfully!")
    print("Run 'poetry run python -m pytest app/tests/test_app.py::TestWaterInPool -v' for full tests")


if __name__ == "__main__":
    main()