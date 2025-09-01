"""
Comprehensive tests for the Strategy pattern implementation of sorting algorithms.

Tests include functionality, performance with large datasets, and strategy switching.
"""

import pytest
import random
import time
from typing import List
from app.strategy import (
    DataSorter,
    QuickSortStrategy,
    MergeSortStrategy,
    HeapSortStrategy,
    SortingStrategy
)


class TestSortingStrategies:
    """Test individual sorting strategy implementations."""
    
    @pytest.fixture
    def sample_data(self) -> List[int]:
        """Small dataset for basic functionality tests."""
        return [64, 34, 25, 12, 22, 11, 90]
    
    @pytest.fixture
    def empty_data(self) -> List[int]:
        """Empty dataset."""
        return []
    
    @pytest.fixture
    def single_element(self) -> List[int]:
        """Single element dataset."""
        return [42]
    
    @pytest.fixture
    def already_sorted(self) -> List[int]:
        """Already sorted dataset."""
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    @pytest.fixture
    def reverse_sorted(self) -> List[int]:
        """Reverse sorted dataset."""
        return [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    
    @pytest.fixture
    def duplicates(self) -> List[int]:
        """Dataset with duplicate values."""
        return [5, 2, 8, 2, 9, 1, 5, 5, 1, 8]
    
    @pytest.fixture
    def large_dataset(self) -> List[int]:
        """Large dataset for performance testing."""
        random.seed(42)  # Reproducible results
        return [random.randint(1, 10000) for _ in range(10000)]
    
    @pytest.fixture
    def very_large_dataset(self) -> List[int]:
        """Very large dataset for stress testing."""
        random.seed(42)
        return [random.randint(1, 100000) for _ in range(100000)]
    
    @pytest.fixture
    def strategies(self) -> List[SortingStrategy]:
        """All sorting strategies to test."""
        return [
            QuickSortStrategy(),
            MergeSortStrategy(),
            HeapSortStrategy()
        ]
    
    def test_basic_sorting_functionality(self, sample_data: List[int], strategies: List[SortingStrategy]):
        """Test that all strategies correctly sort basic datasets."""
        expected = sorted(sample_data)
        
        for strategy in strategies:
            result = strategy.sort(sample_data)
            assert result == expected, f"{strategy.name} failed to sort correctly"
            # Ensure original data is not modified
            assert sample_data == [64, 34, 25, 12, 22, 11, 90]
    
    def test_empty_list_handling(self, empty_data: List[int], strategies: List[SortingStrategy]):
        """Test that all strategies handle empty lists correctly."""
        for strategy in strategies:
            result = strategy.sort(empty_data)
            assert result == [], f"{strategy.name} failed to handle empty list"
    
    def test_single_element_handling(self, single_element: List[int], strategies: List[SortingStrategy]):
        """Test that all strategies handle single element lists correctly."""
        for strategy in strategies:
            result = strategy.sort(single_element)
            assert result == [42], f"{strategy.name} failed to handle single element"
    
    def test_already_sorted_data(self, already_sorted: List[int], strategies: List[SortingStrategy]):
        """Test performance on already sorted data."""
        for strategy in strategies:
            result = strategy.sort(already_sorted)
            assert result == already_sorted, f"{strategy.name} failed on sorted data"
    
    def test_reverse_sorted_data(self, reverse_sorted: List[int], strategies: List[SortingStrategy]):
        """Test performance on reverse sorted data."""
        expected = sorted(reverse_sorted)
        
        for strategy in strategies:
            result = strategy.sort(reverse_sorted)
            assert result == expected, f"{strategy.name} failed on reverse sorted data"
    
    def test_duplicate_values(self, duplicates: List[int], strategies: List[SortingStrategy]):
        """Test that all strategies handle duplicate values correctly."""
        expected = sorted(duplicates)
        
        for strategy in strategies:
            result = strategy.sort(duplicates)
            assert result == expected, f"{strategy.name} failed with duplicates"
    
    def test_large_dataset_sorting(self, large_dataset: List[int], strategies: List[SortingStrategy]):
        """Test sorting performance on large datasets (10,000 elements)."""
        expected = sorted(large_dataset)
        
        for strategy in strategies:
            start_time = time.perf_counter()
            result = strategy.sort(large_dataset)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            assert result == expected, f"{strategy.name} failed on large dataset"
            print(f"{strategy.name}: {execution_time * 1000:.2f}ms for 10K elements")
    
    @pytest.mark.slow
    def test_very_large_dataset_sorting(self, very_large_dataset: List[int], strategies: List[SortingStrategy]):
        """Test sorting performance on very large datasets (100,000 elements)."""
        expected = sorted(very_large_dataset)
        
        for strategy in strategies:
            start_time = time.perf_counter()
            result = strategy.sort(very_large_dataset)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            assert result == expected, f"{strategy.name} failed on very large dataset"
            print(f"{strategy.name}: {execution_time * 1000:.2f}ms for 100K elements")
    
    def test_strategy_properties(self, strategies: List[SortingStrategy]):
        """Test that all strategies have required properties."""
        for strategy in strategies:
            assert strategy.name
            assert strategy.time_complexity_best
            assert strategy.time_complexity_average
            assert strategy.time_complexity_worst
            assert strategy.space_complexity
            
            # Verify complexity notation format
            assert "O(" in strategy.time_complexity_best
            assert "O(" in strategy.time_complexity_average
            assert "O(" in strategy.time_complexity_worst
            assert "O(" in strategy.space_complexity


class TestDataSorter:
    """Test the DataSorter context class."""
    
    @pytest.fixture
    def sorter(self) -> DataSorter:
        """DataSorter instance with default strategy."""
        return DataSorter()
    
    @pytest.fixture
    def sample_data(self) -> List[int]:
        """Sample data for testing."""
        return [64, 34, 25, 12, 22, 11, 90]
    
    def test_default_strategy(self, sorter: DataSorter):
        """Test that DataSorter has a default strategy."""
        assert sorter.get_strategy() is not None
        assert sorter.get_strategy().name == "QuickSort"
    
    def test_strategy_switching(self, sorter: DataSorter, sample_data: List[int]):
        """Test that strategies can be switched at runtime."""
        expected = sorted(sample_data)
        
        # Test with QuickSort (default)
        result1 = sorter.sort(sample_data)
        assert result1 == expected
        assert sorter.get_strategy().name == "QuickSort"
        
        # Switch to MergeSort
        sorter.set_strategy(MergeSortStrategy())
        result2 = sorter.sort(sample_data)
        assert result2 == expected
        assert sorter.get_strategy().name == "MergeSort"
        
        # Switch to HeapSort
        sorter.set_strategy(HeapSortStrategy())
        result3 = sorter.sort(sample_data)
        assert result3 == expected
        assert sorter.get_strategy().name == "HeapSort"
    
    def test_sort_with_none_data(self, sorter: DataSorter):
        """Test that sorting None data raises ValueError."""
        with pytest.raises(ValueError, match="Data cannot be None"):
            sorter.sort(None)
    
    def test_algorithm_info(self, sorter: DataSorter):
        """Test that algorithm info is returned correctly."""
        info = sorter.get_algorithm_info()
        
        required_keys = [
            'name', 'time_complexity_best', 'time_complexity_average',
            'time_complexity_worst', 'space_complexity'
        ]
        
        for key in required_keys:
            assert key in info
            assert info[key] is not None
    
    def test_sort_history_tracking(self, sorter: DataSorter, sample_data: List[int]):
        """Test that sort history is tracked correctly."""
        assert len(sorter.get_sort_history()) == 0
        
        # Perform some sorts
        sorter.sort(sample_data)
        sorter.set_strategy(MergeSortStrategy())
        sorter.sort(sample_data)
        
        history = sorter.get_sort_history()
        assert len(history) == 2
        
        # Check first entry
        assert history[0]['algorithm'] == 'QuickSort'
        assert history[0]['input_size'] == len(sample_data)
        assert 'execution_time_seconds' in history[0]
        assert 'execution_time_ms' in history[0]
        
        # Check second entry
        assert history[1]['algorithm'] == 'MergeSort'
        assert history[1]['input_size'] == len(sample_data)
    
    def test_clear_history(self, sorter: DataSorter, sample_data: List[int]):
        """Test that sort history can be cleared."""
        sorter.sort(sample_data)
        assert len(sorter.get_sort_history()) == 1
        
        sorter.clear_history()
        assert len(sorter.get_sort_history()) == 0
    
    def test_benchmark_functionality(self, sorter: DataSorter, sample_data: List[int]):
        """Test the benchmark functionality."""
        benchmark = sorter.benchmark_current_strategy(sample_data, runs=3)
        
        assert benchmark['algorithm'] == 'QuickSort'
        assert benchmark['input_size'] == len(sample_data)
        assert benchmark['runs'] == 3
        assert 'average_time_ms' in benchmark
        assert 'min_time_ms' in benchmark
        assert 'max_time_ms' in benchmark
        assert len(benchmark['all_times_ms']) == 3
        assert 'complexity_info' in benchmark
    
    def test_benchmark_empty_data(self, sorter: DataSorter):
        """Test benchmark with empty data."""
        result = sorter.benchmark_current_strategy([], runs=3)
        assert 'error' in result
    
    def test_string_representations(self, sorter: DataSorter):
        """Test string representations of DataSorter."""
        str_repr = str(sorter)
        assert "QuickSort" in str_repr
        
        detailed_repr = repr(sorter)
        assert "DataSorter" in detailed_repr
        assert "QuickSortStrategy" in detailed_repr


class TestPerformanceComparison:
    """Performance comparison tests between sorting algorithms."""
    
    def test_algorithm_performance_comparison(self):
        """
        Compare performance of all algorithms on different dataset types.
        
        This test provides insights into algorithm performance characteristics
        but doesn't fail based on performance (as it's system-dependent).
        """
        dataset_sizes = [1000, 5000, 10000]
        strategies = [QuickSortStrategy(), MergeSortStrategy(), HeapSortStrategy()]
        
        print("\\n" + "="*80)
        print("SORTING ALGORITHM PERFORMANCE COMPARISON")
        print("="*80)
        
        for size in dataset_sizes:
            print(f"\\nDataset size: {size} elements")
            print("-" * 40)
            
            # Generate test datasets
            random.seed(42)
            random_data = [random.randint(1, size * 10) for _ in range(size)]
            sorted_data = list(range(size))
            reverse_data = list(range(size, 0, -1))
            
            datasets = {
                "Random": random_data,
                "Sorted": sorted_data,
                "Reverse": reverse_data
            }
            
            for data_type, data in datasets.items():
                print(f"\\n  {data_type} data:")
                
                for strategy in strategies:
                    sorter = DataSorter(strategy)
                    benchmark = sorter.benchmark_current_strategy(data, runs=3)
                    
                    avg_time = benchmark['average_time_ms']
                    min_time = benchmark['min_time_ms']
                    max_time = benchmark['max_time_ms']
                    
                    print(f"    {strategy.name:12}: {avg_time:8.2f}ms avg "
                          f"(min: {min_time:6.2f}ms, max: {max_time:6.2f}ms)")
        
        print("\\n" + "="*80)
        print("ALGORITHM COMPLEXITY SUMMARY")
        print("="*80)
        
        for strategy in strategies:
            info = DataSorter(strategy).get_algorithm_info()
            print(f"\\n{strategy.name}:")
            print(f"  Time Complexity - Best: {info['time_complexity_best']}, "
                  f"Average: {info['time_complexity_average']}, "
                  f"Worst: {info['time_complexity_worst']}")
            print(f"  Space Complexity: {info['space_complexity']}")
    
    @pytest.mark.parametrize("strategy_class", [QuickSortStrategy, MergeSortStrategy, HeapSortStrategy])
    def test_sorting_correctness_with_various_inputs(self, strategy_class):
        """Test sorting correctness with various edge cases for each strategy."""
        strategy = strategy_class()
        
        # Test cases with expected results
        test_cases = [
            ([], []),
            ([1], [1]),
            ([2, 1], [1, 2]),
            ([1, 1, 1], [1, 1, 1]),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]),
            (list(range(100, 0, -1)), list(range(1, 101))),  # Reverse sorted
        ]
        
        for input_data, expected in test_cases:
            result = strategy.sort(input_data)
            assert result == expected, f"{strategy.name} failed on input {input_data}"


if __name__ == "__main__":
    # Run performance comparison when script is executed directly
    test_instance = TestPerformanceComparison()
    test_instance.test_algorithm_performance_comparison()