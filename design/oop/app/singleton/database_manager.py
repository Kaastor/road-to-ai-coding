"""
Thread-safe Singleton implementation for database connection management.

This module implements a thread-safe Singleton pattern to ensure only one
database connection manager instance exists across multiple threads.
"""

import threading
import logging
import time
from typing import Optional
from datetime import datetime


class DatabaseConnectionManager:
    """
    Thread-safe Singleton database connection manager.
    
    Ensures only one instance is created across multiple threads and manages
    database connections with proper logging.
    """
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False
    
    def __new__(cls) -> 'DatabaseConnectionManager':
        """
        Create or return the singleton instance with thread safety.
        
        Returns:
            DatabaseConnectionManager: The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """
        Initialize the database connection manager.
        
        Only initializes once due to singleton pattern.
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._connection_count = 0
                    self._active_connections: dict[int, str] = {}
                    self._creation_time = datetime.now()
                    self._thread_id = threading.get_ident()
                    self._logger = self._setup_logger()
                    
                    self._logger.info(
                        f"DatabaseConnectionManager singleton created at {self._creation_time} "
                        f"by thread {self._thread_id}"
                    )
                    
                    DatabaseConnectionManager._initialized = True
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up logging for the database connection manager.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger('DatabaseConnectionManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [Thread-%(thread)d] - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_connection(self) -> str:
        """
        Get a database connection.
        
        Returns:
            str: Connection identifier
        """
        thread_id = threading.get_ident()
        
        with self._lock:
            self._connection_count += 1
            connection_id = f"conn_{self._connection_count}"
            self._active_connections[thread_id] = connection_id
            
            self._logger.info(
                f"Connection {connection_id} created for thread {thread_id}. "
                f"Total active connections: {len(self._active_connections)}"
            )
            
            return connection_id
    
    def close_connection(self) -> None:
        """
        Close the database connection for the current thread.
        """
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id in self._active_connections:
                connection_id = self._active_connections.pop(thread_id)
                
                self._logger.info(
                    f"Connection {connection_id} closed for thread {thread_id}. "
                    f"Remaining active connections: {len(self._active_connections)}"
                )
            else:
                self._logger.warning(f"No active connection found for thread {thread_id}")
    
    def get_instance_info(self) -> dict[str, any]:
        """
        Get information about the singleton instance.
        
        Returns:
            dict: Instance information including creation time, thread ID, and connection stats
        """
        return {
            'creation_time': self._creation_time,
            'creator_thread_id': self._thread_id,
            'current_thread_id': threading.get_ident(),
            'total_connections_created': self._connection_count,
            'active_connections': len(self._active_connections),
            'active_connection_details': dict(self._active_connections),
            'instance_id': id(self)
        }
    
    def simulate_database_operation(self, operation_name: str, duration: float = 0.1) -> None:
        """
        Simulate a database operation with logging.
        
        Args:
            operation_name: Name of the operation being performed
            duration: Time to simulate the operation (in seconds)
        """
        thread_id = threading.get_ident()
        connection_id = self._active_connections.get(thread_id, "No connection")
        
        self._logger.info(
            f"Thread {thread_id} starting '{operation_name}' using {connection_id}"
        )
        
        time.sleep(duration)
        
        self._logger.info(
            f"Thread {thread_id} completed '{operation_name}' using {connection_id}"
        )