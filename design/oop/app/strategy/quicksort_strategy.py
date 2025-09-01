"""
QuickSort implementation using the Strategy pattern.

QuickSort is a divide-and-conquer algorithm that works by selecting a 'pivot'
element and partitioning the array around the pivot.
"""

import random
from typing import List, TypeVar
from .sorting_strategy import SortingStrategy

T = TypeVar('T')


class QuickSortStrategy(SortingStrategy[T]):
    """
    QuickSort implementation with randomized pivot selection.
    
    Time Complexity:
    - Best Case: O(n log n) - when pivot divides array into equal halves
    - Average Case: O(n log n) - randomized pivot helps achieve this
    - Worst Case: O(n²) - when pivot is always smallest/largest element
    
    Space Complexity: O(log n) - due to recursion stack depth
    
    Characteristics:
    - In-place sorting (modifies original array copy)
    - Not stable (relative order of equal elements may change)
    - Cache-efficient due to good locality of reference
    - Performs well on average with randomized pivot
    """
    
    def sort(self, data: List[T]) -> List[T]:
        """
        Sort data using QuickSort algorithm.
        
        Args:
            data: List of comparable elements
            
        Returns:
            New sorted list in ascending order
        """
        if not data:
            return []
        
        # Create a copy to avoid modifying the original list
        result = data.copy()
        self._quicksort(result, 0, len(result) - 1)
        return result
    
    def _quicksort(self, arr: List[T], low: int, high: int) -> None:
        """
        Recursive QuickSort implementation.
        
        Args:
            arr: Array to sort (modified in-place)
            low: Starting index of subarray
            high: Ending index of subarray
        """
        if low < high:
            # Partition the array and get pivot index
            pivot_index = self._partition(arr, low, high)
            
            # Recursively sort elements before and after partition
            self._quicksort(arr, low, pivot_index - 1)
            self._quicksort(arr, pivot_index + 1, high)
    
    def _partition(self, arr: List[T], low: int, high: int) -> int:
        """
        Lomuto partition scheme with randomized pivot.
        
        Rearranges array so that all elements smaller than pivot
        come before it, and all greater elements come after it.
        
        Args:
            arr: Array to partition
            low: Starting index
            high: Ending index
            
        Returns:
            Final position of pivot element
        """
        # Randomize pivot to improve average performance
        random_index = random.randint(low, high)
        arr[random_index], arr[high] = arr[high], arr[random_index]
        
        pivot = arr[high]  # Choose rightmost element as pivot
        i = low - 1  # Index of smaller element
        
        for j in range(low, high):
            # If current element is smaller than or equal to pivot
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        # Place pivot in correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    @property
    def name(self) -> str:
        return "QuickSort"
    
    @property
    def time_complexity_best(self) -> str:
        return "O(n log n)"
    
    @property
    def time_complexity_average(self) -> str:
        return "O(n log n)"
    
    @property
    def time_complexity_worst(self) -> str:
        return "O(n²)"
    
    @property
    def space_complexity(self) -> str:
        return "O(log n)"