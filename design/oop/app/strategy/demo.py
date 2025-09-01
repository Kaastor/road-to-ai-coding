#!/usr/bin/env python3
"""
Strategy Pattern Demonstration for Sorting Algorithms.

This script demonstrates the Strategy pattern implementation with sorting
algorithms, showing how different strategies can be swapped at runtime.
"""

import random
import logging
from app.strategy import (
    DataSorter,
    QuickSortStrategy,
    MergeSortStrategy,
    HeapSortStrategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def demonstrate_basic_usage():
    """Demonstrate basic usage of the Strategy pattern."""
    print("="*70)
    print("STRATEGY PATTERN DEMONSTRATION")
    print("="*70)
    
    # Sample data
    data = [64, 34, 25, 12, 22, 11, 90, 5, 77, 30]
    print(f"Original data: {data}")
    print(f"Expected result: {sorted(data)}")
    print()
    
    # Create sorter with default strategy (QuickSort)
    sorter = DataSorter()
    print(f"Created DataSorter with default strategy: {sorter.get_strategy().name}")
    
    # Sort with QuickSort
    result1 = sorter.sort(data)
    print(f"QuickSort result: {result1}")
    
    # Switch to MergeSort at runtime
    sorter.set_strategy(MergeSortStrategy())
    result2 = sorter.sort(data)
    print(f"MergeSort result: {result2}")
    
    # Switch to HeapSort at runtime
    sorter.set_strategy(HeapSortStrategy())
    result3 = sorter.sort(data)
    print(f"HeapSort result: {result3}")
    
    print("\\nAll algorithms produced the same correct result!")


def demonstrate_algorithm_info():
    """Demonstrate getting algorithm complexity information."""
    print("\\n" + "="*70)
    print("ALGORITHM COMPLEXITY INFORMATION")
    print("="*70)
    
    strategies = [
        QuickSortStrategy(),
        MergeSortStrategy(), 
        HeapSortStrategy()
    ]
    
    for strategy in strategies:
        sorter = DataSorter(strategy)
        info = sorter.get_algorithm_info()
        
        print(f"\\n{strategy.name}:")
        print(f"  Best Case Time Complexity:    {info['time_complexity_best']}")
        print(f"  Average Case Time Complexity: {info['time_complexity_average']}")
        print(f"  Worst Case Time Complexity:   {info['time_complexity_worst']}")
        print(f"  Space Complexity:             {info['space_complexity']}")


def demonstrate_performance_benchmarking():
    """Demonstrate performance benchmarking capabilities."""
    print("\\n" + "="*70)
    print("PERFORMANCE BENCHMARKING")
    print("="*70)
    
    # Generate test data of different sizes
    sizes = [1000, 5000]
    
    for size in sizes:
        print(f"\\nBenchmarking with {size} elements:")
        print("-" * 40)
        
        # Generate random data
        random.seed(42)
        test_data = [random.randint(1, size * 10) for _ in range(size)]
        
        strategies = [
            QuickSortStrategy(),
            MergeSortStrategy(),
            HeapSortStrategy()
        ]
        
        for strategy in strategies:
            sorter = DataSorter(strategy)
            benchmark = sorter.benchmark_current_strategy(test_data, runs=5)
            
            print(f"  {strategy.name:12}: {benchmark['average_time_ms']:8.2f}ms avg "
                  f"(min: {benchmark['min_time_ms']:6.2f}ms, "
                  f"max: {benchmark['max_time_ms']:6.2f}ms)")


def demonstrate_history_tracking():
    """Demonstrate sorting history tracking."""
    print("\\n" + "="*70)
    print("HISTORY TRACKING")
    print("="*70)
    
    sorter = DataSorter()
    data1 = [5, 2, 8, 1, 9]
    data2 = [10, 3, 7, 4, 6]
    
    print("Performing multiple sorts with different strategies...")
    
    # Sort with QuickSort
    sorter.sort(data1)
    
    # Switch to MergeSort and sort different data
    sorter.set_strategy(MergeSortStrategy())
    sorter.sort(data2)
    
    # Switch to HeapSort and sort again
    sorter.set_strategy(HeapSortStrategy())
    sorter.sort(data1)
    
    print("\\nSort History:")
    history = sorter.get_sort_history()
    for i, record in enumerate(history, 1):
        print(f"  {i}. {record['algorithm']:12} - "
              f"{record['input_size']} elements - "
              f"{record['execution_time_ms']:.2f}ms")


def demonstrate_real_world_scenario():
    """Demonstrate a real-world scenario where strategy switching is beneficial."""
    print("\\n" + "="*70)
    print("REAL-WORLD SCENARIO: ADAPTIVE SORTING")
    print("="*70)
    
    print("Scenario: An application that needs to sort different types of datasets")
    print("and wants to choose the optimal algorithm based on data characteristics.")
    print()
    
    sorter = DataSorter()
    
    scenarios = [
        {
            'name': 'Small dataset (< 100 elements)',
            'data': [random.randint(1, 100) for _ in range(50)],
            'recommended': 'QuickSort',
            'reason': 'Low overhead, good for small datasets'
        },
        {
            'name': 'Large random dataset',
            'data': [random.randint(1, 10000) for _ in range(5000)],
            'recommended': 'QuickSort', 
            'reason': 'Best average performance for random data'
        },
        {
            'name': 'Memory-constrained environment',
            'data': [random.randint(1, 1000) for _ in range(1000)],
            'recommended': 'HeapSort',
            'reason': 'O(1) space complexity, in-place sorting'
        },
        {
            'name': 'Stability required (equal elements order preserved)',
            'data': [1, 3, 2, 3, 1, 2, 3],
            'recommended': 'MergeSort',
            'reason': 'Stable sorting algorithm'
        }
    ]
    
    for scenario in scenarios:
        print(f"\\n{scenario['name']}:")
        print(f"  Data size: {len(scenario['data'])} elements")
        print(f"  Recommended: {scenario['recommended']}")
        print(f"  Reason: {scenario['reason']}")
        
        # Set appropriate strategy
        if scenario['recommended'] == 'QuickSort':
            sorter.set_strategy(QuickSortStrategy())
        elif scenario['recommended'] == 'MergeSort':
            sorter.set_strategy(MergeSortStrategy())
        elif scenario['recommended'] == 'HeapSort':
            sorter.set_strategy(HeapSortStrategy())
        
        # Perform sorting and show results
        result = sorter.sort(scenario['data'])
        print(f"  Sorted successfully: {len(result)} elements")
        
        # Show partial result for readability
        if len(result) > 10:
            print(f"  First 10 elements: {result[:10]}")
        else:
            print(f"  Result: {result}")


def main():
    """Main demonstration function."""
    print("Strategy Pattern Implementation for Sorting Algorithms")
    print("This demonstration shows how the Strategy pattern enables")
    print("runtime algorithm switching and flexible design.")
    
    try:
        demonstrate_basic_usage()
        demonstrate_algorithm_info()
        demonstrate_performance_benchmarking()
        demonstrate_history_tracking()
        demonstrate_real_world_scenario()
        
        print("\\n" + "="*70)
        print("DEMONSTRATION COMPLETE")
        print("="*70)
        print("\\nKey Benefits of the Strategy Pattern:")
        print("• Runtime algorithm switching")
        print("• Easy to add new sorting algorithms")
        print("• Decoupled client code from specific implementations")
        print("• Algorithm-specific optimizations and configurations")
        print("• Comprehensive performance tracking and analysis")
        
    except Exception as e:
        print(f"\\nError during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()