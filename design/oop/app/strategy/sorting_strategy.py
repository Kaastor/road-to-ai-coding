"""
Abstract base class for sorting strategies.

Defines the interface that all concrete sorting strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')


class SortingStrategy(ABC, Generic[T]):
    """
    Abstract base class for sorting algorithms.
    
    This class defines the interface that all concrete sorting strategies
    must implement. It uses the Strategy pattern to allow different
    sorting algorithms to be used interchangeably.
    """
    
    @abstractmethod
    def sort(self, data: List[T]) -> List[T]:
        """
        Sort the given data using the specific algorithm.
        
        Args:
            data: List of comparable elements to sort
            
        Returns:
            New list with elements sorted in ascending order
            
        Note:
            This method should not modify the original list
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the sorting algorithm.
        
        Returns:
            String name of the algorithm
        """
        pass
    
    @property
    @abstractmethod
    def time_complexity_best(self) -> str:
        """
        Return the best-case time complexity.
        
        Returns:
            String representation of best-case time complexity
        """
        pass
    
    @property
    @abstractmethod
    def time_complexity_average(self) -> str:
        """
        Return the average-case time complexity.
        
        Returns:
            String representation of average-case time complexity
        """
        pass
    
    @property
    @abstractmethod
    def time_complexity_worst(self) -> str:
        """
        Return the worst-case time complexity.
        
        Returns:
            String representation of worst-case time complexity
        """
        pass
    
    @property
    @abstractmethod
    def space_complexity(self) -> str:
        """
        Return the space complexity.
        
        Returns:
            String representation of space complexity
        """
        pass