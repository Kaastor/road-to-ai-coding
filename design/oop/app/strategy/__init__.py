"""
Strategy Pattern implementation for sorting algorithms.

This module provides a flexible sorting system where different sorting algorithms
can be swapped at runtime using the Strategy pattern.
"""

from .sorting_strategy import SortingStrategy
from .quicksort_strategy import QuickSortStrategy
from .mergesort_strategy import MergeSortStrategy
from .heapsort_strategy import HeapSortStrategy
from .data_sorter import DataSorter

__all__ = [
    'SortingStrategy',
    'QuickSortStrategy', 
    'MergeSortStrategy',
    'HeapSortStrategy',
    'DataSorter'
]