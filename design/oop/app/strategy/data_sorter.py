"""
DataSorter context class for the Strategy pattern.

This class provides a unified interface for sorting data using different
algorithms that can be switched at runtime.
"""

import time
import logging
from typing import List, TypeVar, Optional, Dict, Any
from .sorting_strategy import SortingStrategy
from .quicksort_strategy import QuickSortStrategy

T = TypeVar('T')

logger = logging.getLogger(__name__)


class DataSorter:
    """
    Context class for the Strategy pattern that manages sorting operations.
    
    This class allows clients to sort data using different algorithms
    without being coupled to specific implementations. The sorting strategy
    can be changed at runtime to adapt to different performance requirements.
    
    Example:
        sorter = DataSorter(QuickSortStrategy())
        result = sorter.sort([3, 1, 4, 1, 5, 9, 2, 6])
        
        # Switch strategy at runtime
        sorter.set_strategy(MergeSortStrategy())
        result = sorter.sort([3, 1, 4, 1, 5, 9, 2, 6])
    """
    
    def __init__(self, strategy: Optional[SortingStrategy[T]] = None):
        """
        Initialize DataSorter with an optional sorting strategy.
        
        Args:
            strategy: Initial sorting strategy to use. Defaults to QuickSort.
        """
        self._strategy = strategy or QuickSortStrategy()
        self._sort_history: List[Dict[str, Any]] = []
    
    def set_strategy(self, strategy: SortingStrategy[T]) -> None:
        """
        Change the sorting strategy at runtime.
        
        Args:
            strategy: New sorting strategy to use
        """
        logger.info(f"Switching sorting strategy from {self._strategy.name} to {strategy.name}")
        self._strategy = strategy
    
    def get_strategy(self) -> SortingStrategy[T]:
        """
        Get the current sorting strategy.
        
        Returns:
            Current sorting strategy instance
        """
        return self._strategy
    
    def sort(self, data: List[T]) -> List[T]:
        """
        Sort the given data using the current strategy.
        
        Args:
            data: List of comparable elements to sort
            
        Returns:
            New list with elements sorted in ascending order
            
        Raises:
            ValueError: If data list is None
        """
        if data is None:
            raise ValueError("Data cannot be None")
        
        if not data:
            return []
        
        logger.info(f"Sorting {len(data)} elements using {self._strategy.name}")
        
        start_time = time.perf_counter()
        result = self._strategy.sort(data)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        # Record sorting operation for analysis
        sort_record = {
            'algorithm': self._strategy.name,
            'input_size': len(data),
            'execution_time_seconds': execution_time,
            'execution_time_ms': execution_time * 1000,
            'timestamp': time.time()
        }
        self._sort_history.append(sort_record)
        
        logger.info(f"Sorting completed in {execution_time * 1000:.2f}ms using {self._strategy.name}")
        
        return result
    
    def get_algorithm_info(self) -> Dict[str, str]:
        """
        Get detailed information about the current sorting algorithm.
        
        Returns:
            Dictionary containing algorithm complexity information
        """
        return {
            'name': self._strategy.name,
            'time_complexity_best': self._strategy.time_complexity_best,
            'time_complexity_average': self._strategy.time_complexity_average,
            'time_complexity_worst': self._strategy.time_complexity_worst,
            'space_complexity': self._strategy.space_complexity
        }
    
    def get_sort_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all sorting operations performed.
        
        Returns:
            List of dictionaries containing sorting operation details
        """
        return self._sort_history.copy()
    
    def clear_history(self) -> None:
        """Clear the sorting operation history."""
        self._sort_history.clear()
        logger.info("Sort history cleared")
    
    def benchmark_current_strategy(self, data: List[T], runs: int = 5) -> Dict[str, Any]:
        """
        Benchmark the current sorting strategy with multiple runs.
        
        Args:
            data: Data to sort for benchmarking
            runs: Number of runs to average over
            
        Returns:
            Dictionary containing benchmark statistics
        """
        if not data:
            return {'error': 'Empty data provided for benchmarking'}
        
        execution_times = []
        
        for run in range(runs):
            start_time = time.perf_counter()
            self._strategy.sort(data)
            end_time = time.perf_counter()
            execution_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        benchmark_result = {
            'algorithm': self._strategy.name,
            'input_size': len(data),
            'runs': runs,
            'average_time_ms': avg_time,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'all_times_ms': execution_times,
            'complexity_info': self.get_algorithm_info()
        }
        
        logger.info(f"Benchmark completed: {self._strategy.name} averaged {avg_time:.2f}ms over {runs} runs")
        
        return benchmark_result
    
    def __str__(self) -> str:
        """String representation of the DataSorter."""
        return f"DataSorter(strategy={self._strategy.name})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the DataSorter."""
        return (f"DataSorter(strategy={self._strategy.__class__.__name__}, "
                f"history_entries={len(self._sort_history)})")