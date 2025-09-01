"""In-memory cache implementation with generic key-value storage."""

from typing import TypeVar, Generic, Dict, Optional

K = TypeVar('K')
V = TypeVar('V')


class InMemCache(Generic[K, V]):
    """A generic in-memory cache implementation.
    
    This cache stores key-value pairs in memory with no persistence.
    It is designed for single-thread use only.
    
    Type Parameters:
        K: The type of keys stored in the cache
        V: The type of values stored in the cache
    """
    
    def __init__(self) -> None:
        """Initialize an empty cache."""
        self._cache: Dict[K, V] = {}
    
    def set(self, key: K, value: V) -> None:
        """Store a key-value pair in the cache.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        self._cache[key] = value
    
    def get(self, key: K) -> Optional[V]:
        """Retrieve a value from the cache by key.
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or None if key not found
        """
        return self._cache.get(key)
    
    def set_all(self, value: V) -> None:
        """Set all existing keys in the cache to the same value.
        
        Args:
            value: The value to set for all existing keys
        """
        for key in self._cache:
            self._cache[key] = value