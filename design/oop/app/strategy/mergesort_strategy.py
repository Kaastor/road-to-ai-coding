"""
MergeSort implementation using the Strategy pattern.

MergeSort is a stable, divide-and-conquer algorithm that divides the array
into smaller subarrays, sorts them, and then merges them back together.
"""

from typing import List, TypeVar
from .sorting_strategy import SortingStrategy

T = TypeVar('T')


class MergeSortStrategy(SortingStrategy[T]):
    """
    MergeSort implementation with guaranteed O(n log n) performance.
    
    Time Complexity:
    - Best Case: O(n log n) - always divides array in half
    - Average Case: O(n log n) - consistent performance regardless of input
    - Worst Case: O(n log n) - guaranteed logarithmic depth
    
    Space Complexity: O(n) - requires additional space for temporary arrays
    
    Characteristics:
    - Stable sorting (preserves relative order of equal elements)
    - Consistent performance regardless of input distribution
    - Good for large datasets due to predictable O(n log n) guarantee
    - External sorting friendly (can work with data larger than memory)
    - Not in-place (requires additional memory)
    """
    
    def sort(self, data: List[T]) -> List[T]:
        """
        Sort data using MergeSort algorithm.
        
        Args:
            data: List of comparable elements
            
        Returns:
            New sorted list in ascending order
        """
        if not data:
            return []
        
        # Create a copy to avoid modifying the original list
        result = data.copy()
        self._mergesort(result)
        return result
    
    def _mergesort(self, arr: List[T]) -> None:
        """
        Recursive MergeSort implementation.
        
        Divides the array into two halves, recursively sorts them,
        and then merges the sorted halves.
        
        Args:
            arr: Array to sort (modified in-place)
        """
        if len(arr) <= 1:
            return
        
        # Divide: find the middle point
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]
        
        # Conquer: recursively sort both halves
        self._mergesort(left_half)
        self._mergesort(right_half)
        
        # Combine: merge the sorted halves
        self._merge(arr, left_half, right_half)
    
    def _merge(self, arr: List[T], left: List[T], right: List[T]) -> None:
        """
        Merge two sorted arrays into one sorted array.
        
        Args:
            arr: Target array to store merged result
            left: Left sorted subarray
            right: Right sorted subarray
        """
        i = j = k = 0
        
        # Merge elements from left and right while both have elements
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        
        # Copy remaining elements from left subarray
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        
        # Copy remaining elements from right subarray
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
    
    @property
    def name(self) -> str:
        return "MergeSort"
    
    @property
    def time_complexity_best(self) -> str:
        return "O(n log n)"
    
    @property
    def time_complexity_average(self) -> str:
        return "O(n log n)"
    
    @property
    def time_complexity_worst(self) -> str:
        return "O(n log n)"
    
    @property
    def space_complexity(self) -> str:
        return "O(n)"