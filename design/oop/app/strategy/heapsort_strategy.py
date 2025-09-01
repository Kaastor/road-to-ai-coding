"""
HeapSort implementation using the Strategy pattern.

HeapSort is a comparison-based sorting algorithm that uses a binary heap
data structure. It builds a max heap from the input data, then repeatedly
extracts the maximum element to create a sorted array.
"""

from typing import List, TypeVar
from .sorting_strategy import SortingStrategy

T = TypeVar('T')


class HeapSortStrategy(SortingStrategy[T]):
    """
    HeapSort implementation with guaranteed O(n log n) performance.
    
    Time Complexity:
    - Best Case: O(n log n) - building heap takes O(n), extraction takes O(n log n)
    - Average Case: O(n log n) - consistent performance
    - Worst Case: O(n log n) - guaranteed logarithmic height operations
    
    Space Complexity: O(1) - sorts in-place with only constant extra space
    
    Characteristics:
    - In-place sorting (only requires constant extra space)
    - Not stable (relative order of equal elements may change)
    - Guaranteed O(n log n) performance in all cases
    - Good for systems with memory constraints due to O(1) space complexity
    - Cache performance not as good as QuickSort due to non-sequential access
    """
    
    def sort(self, data: List[T]) -> List[T]:
        """
        Sort data using HeapSort algorithm.
        
        Args:
            data: List of comparable elements
            
        Returns:
            New sorted list in ascending order
        """
        if not data:
            return []
        
        # Create a copy to avoid modifying the original list
        result = data.copy()
        self._heapsort(result)
        return result
    
    def _heapsort(self, arr: List[T]) -> None:
        """
        HeapSort implementation.
        
        1. Build a max heap from the input array
        2. Repeatedly extract the maximum element and place it at the end
        
        Args:
            arr: Array to sort (modified in-place)
        """
        n = len(arr)
        
        # Build max heap (rearrange array)
        # Start from the last non-leaf node and heapify each node
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(arr, n, i)
        
        # Extract elements from heap one by one
        for i in range(n - 1, 0, -1):
            # Move current root (maximum) to end
            arr[0], arr[i] = arr[i], arr[0]
            
            # Call heapify on the reduced heap
            self._heapify(arr, i, 0)
    
    def _heapify(self, arr: List[T], n: int, i: int) -> None:
        """
        Heapify a subtree rooted with node i.
        
        Maintains the max heap property by ensuring that the parent
        node is larger than its children.
        
        Args:
            arr: Array representing the heap
            n: Size of heap
            i: Root index of subtree to heapify
        """
        largest = i  # Initialize largest as root
        left = 2 * i + 1  # Left child index
        right = 2 * i + 2  # Right child index
        
        # Check if left child exists and is greater than root
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        # Check if right child exists and is greater than current largest
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        # If largest is not root, swap and continue heapifying
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            
            # Recursively heapify the affected subtree
            self._heapify(arr, n, largest)
    
    @property
    def name(self) -> str:
        return "HeapSort"
    
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
        return "O(1)"