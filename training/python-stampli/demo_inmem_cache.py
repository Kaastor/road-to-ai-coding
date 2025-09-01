#!/usr/bin/env python3
"""Demo script showcasing InMemCache functionality with all test cases."""

from app.inmem_cache import InMemCache


def print_separator(title: str) -> None:
    """Print a formatted section separator."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)


def demo_basic_operations() -> None:
    """Demo basic set and get operations."""
    print_separator("Basic Set and Get Operations")
    
    cache = InMemCache[int, str]()
    
    print("Creating cache and setting values:")
    cache.set(1, "one")
    print("Set(1, 'one')")
    
    cache.set(2, "two")
    print("Set(2, 'two')")
    
    print("\nRetrieving values:")
    result1 = cache.get(1)
    print(f"Get(1) => {result1}")
    
    result2 = cache.get(2)
    print(f"Get(2) => {result2}")
    
    result3 = cache.get(3)
    print(f"Get(3) => {result3}")


def demo_set_all_functionality() -> None:
    """Demo SetAll functionality."""
    print_separator("SetAll Functionality")
    
    cache = InMemCache[int, str]()
    
    print("Setting up initial cache:")
    cache.set(1, "one")
    print("Set(1, 'one')")
    
    cache.set(2, "two")
    print("Set(2, 'two')")
    
    print("\nBefore SetAll:")
    print(f"Get(1) => {cache.get(1)}")
    print(f"Get(2) => {cache.get(2)}")
    
    print("\nCalling SetAll('all'):")
    cache.set_all("all")
    
    print("\nAfter SetAll:")
    print(f"Get(1) => {cache.get(1)}")
    print(f"Get(2) => {cache.get(2)}")
    print(f"Get(3) => {cache.get(3)} (key 3 was never set)")


def demo_requirements_example() -> None:
    """Demo the exact sequence from requirements."""
    print_separator("Requirements Example Sequence")
    
    cache = InMemCache[int, str]()
    
    print("Following the exact sequence from requirements:")
    
    cache.set(1, "one")
    print("1. Set(1, 'one')")
    
    cache.set(2, "two")
    print("2. Set(2, 'two')")
    
    result = cache.get(1)
    print(f"3. Get(1) => {result}")
    
    result = cache.get(3)
    print(f"4. Get(3) => {result}")
    
    cache.set_all("all")
    print("5. SetAll('all')")
    
    result = cache.get(1)
    print(f"6. Get(1) => {result}")
    
    cache.set(1, "one")
    print("7. Set(1, 'one')")
    
    result = cache.get(2)
    print(f"8. Get(2) => {result}")
    
    result = cache.get(1)
    print(f"9. Get(1) => {result}")
    
    result = cache.get(3)
    print(f"10. Get(3) => {result} (Note: key 3 was never set)")
    
    result = cache.get(4)
    print(f"11. Get(4) => {result} (Note: key 4 was never set)")


def demo_empty_cache_operations() -> None:
    """Demo operations on empty cache."""
    print_separator("Empty Cache Operations")
    
    cache = InMemCache[str, int]()
    
    print("Operating on empty cache:")
    result = cache.get("nonexistent")
    print(f"Get('nonexistent') => {result}")
    
    print("\nCalling SetAll(42) on empty cache:")
    cache.set_all(42)
    
    result = cache.get("still_nonexistent")
    print(f"Get('still_nonexistent') => {result}")


def demo_overwrite_operations() -> None:
    """Demo overwriting existing keys."""
    print_separator("Overwrite Operations")
    
    cache = InMemCache[str, int]()
    
    print("Testing key overwriting:")
    cache.set("key", 1)
    print("Set('key', 1)")
    
    result = cache.get("key")
    print(f"Get('key') => {result}")
    
    cache.set("key", 2)
    print("Set('key', 2)")
    
    result = cache.get("key")
    print(f"Get('key') => {result}")


def demo_different_types() -> None:
    """Demo cache with different types."""
    print_separator("Different Type Combinations")
    
    print("String keys, Integer values:")
    cache_str_int = InMemCache[str, int]()
    cache_str_int.set("count", 42)
    cache_str_int.set("age", 25)
    print(f"Set('count', 42), Set('age', 25)")
    print(f"Get('count') => {cache_str_int.get('count')}")
    print(f"Get('age') => {cache_str_int.get('age')}")
    
    print("\nInteger keys, List values:")
    cache_int_list = InMemCache[int, list[str]]()
    cache_int_list.set(1, ["apple", "banana"])
    cache_int_list.set(2, ["cat", "dog"])
    print(f"Set(1, ['apple', 'banana']), Set(2, ['cat', 'dog'])")
    print(f"Get(1) => {cache_int_list.get(1)}")
    print(f"Get(2) => {cache_int_list.get(2)}")
    
    cache_int_list.set_all(["updated"])
    print(f"\nAfter SetAll(['updated']):")
    print(f"Get(1) => {cache_int_list.get(1)}")
    print(f"Get(2) => {cache_int_list.get(2)}")


def main() -> None:
    """Run all demo scenarios."""
    print("InMemCache Demo - Showcasing All Functionality")
    print("=" * 50)
    
    demo_basic_operations()
    demo_set_all_functionality()
    demo_requirements_example()
    demo_empty_cache_operations()
    demo_overwrite_operations()
    demo_different_types()
    
    print_separator("Demo Complete")
    print("All InMemCache functionality demonstrated successfully!")


if __name__ == "__main__":
    main()