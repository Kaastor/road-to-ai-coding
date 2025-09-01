"""
Tests for the thread-safe Singleton DatabaseConnectionManager.

This module contains comprehensive tests to verify the singleton behavior,
thread safety, and functionality of the DatabaseConnectionManager.
"""

import pytest
import threading
import time
from typing import List
from unittest.mock import patch

from app.singleton import DatabaseConnectionManager


class TestDatabaseConnectionManager:
    """Test cases for DatabaseConnectionManager singleton."""
    
    def setup_method(self):
        """Reset singleton state before each test."""
        # Reset singleton state
        DatabaseConnectionManager._instance = None
        DatabaseConnectionManager._initialized = False
    
    def test_singleton_instance_creation(self):
        """Test that only one instance is created."""
        manager1 = DatabaseConnectionManager()
        manager2 = DatabaseConnectionManager()
        
        assert manager1 is manager2
        assert id(manager1) == id(manager2)
    
    def test_singleton_thread_safety(self):
        """Test singleton creation is thread-safe."""
        instances = []
        
        def create_instance():
            instance = DatabaseConnectionManager()
            instances.append(instance)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
        
        # Start all threads simultaneously
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all instances are the same
        assert len(instances) == 10
        assert all(instance is instances[0] for instance in instances)
    
    def test_connection_creation(self):
        """Test connection creation functionality."""
        manager = DatabaseConnectionManager()
        
        connection1 = manager.get_connection()
        connection2 = manager.get_connection()
        
        assert connection1 != connection2
        assert connection1.startswith("conn_")
        assert connection2.startswith("conn_")
    
    def test_connection_tracking(self):
        """Test that connections are properly tracked."""
        manager = DatabaseConnectionManager()
        
        # Initially no connections
        info = manager.get_instance_info()
        assert info['total_connections_created'] == 0
        assert info['active_connections'] == 0
        
        # Create a connection
        connection = manager.get_connection()
        
        info = manager.get_instance_info()
        assert info['total_connections_created'] == 1
        assert info['active_connections'] == 1
        assert threading.get_ident() in info['active_connection_details']
        
        # Close the connection
        manager.close_connection()
        
        info = manager.get_instance_info()
        assert info['total_connections_created'] == 1
        assert info['active_connections'] == 0
        assert threading.get_ident() not in info['active_connection_details']
    
    def test_multiple_thread_connections(self):
        """Test connection management across multiple threads."""
        manager = DatabaseConnectionManager()
        results = {}
        
        def thread_worker(thread_id: int):
            connection = manager.get_connection()
            results[thread_id] = connection
            time.sleep(0.1)  # Keep connection alive briefly
            manager.close_connection()
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        assert len(set(results.values())) == 5  # All connections should be unique
        
        # All connections should be closed
        info = manager.get_instance_info()
        assert info['active_connections'] == 0
        assert info['total_connections_created'] == 5
    
    def test_close_nonexistent_connection(self):
        """Test closing a connection that doesn't exist."""
        manager = DatabaseConnectionManager()
        
        # This should not raise an exception
        manager.close_connection()
        
        info = manager.get_instance_info()
        assert info['active_connections'] == 0
    
    def test_simulate_database_operation(self):
        """Test database operation simulation."""
        manager = DatabaseConnectionManager()
        
        # Create a connection first
        connection = manager.get_connection()
        
        # This should not raise an exception
        manager.simulate_database_operation("test_operation", 0.01)
        
        manager.close_connection()
    
    def test_instance_info_structure(self):
        """Test the structure of instance information."""
        manager = DatabaseConnectionManager()
        info = manager.get_instance_info()
        
        required_keys = {
            'creation_time',
            'creator_thread_id',
            'current_thread_id',
            'total_connections_created',
            'active_connections',
            'active_connection_details',
            'instance_id'
        }
        
        assert set(info.keys()) == required_keys
        assert isinstance(info['total_connections_created'], int)
        assert isinstance(info['active_connections'], int)
        assert isinstance(info['active_connection_details'], dict)
        assert isinstance(info['instance_id'], int)
    
    @patch('time.sleep')
    def test_simulate_operation_without_connection(self, mock_sleep):
        """Test simulating operation without an active connection."""
        manager = DatabaseConnectionManager()
        
        # Should work even without an active connection
        manager.simulate_database_operation("test_op", 0.01)
        
        mock_sleep.assert_called_once_with(0.01)
    
    def test_concurrent_instance_creation_stress(self):
        """Stress test for concurrent instance creation."""
        instances = []
        barrier = threading.Barrier(50)  # Synchronize 50 threads
        
        def stress_create_instance():
            barrier.wait()  # All threads start simultaneously
            instance = DatabaseConnectionManager()
            instances.append(instance)
        
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=stress_create_instance)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 50
        assert all(instance is instances[0] for instance in instances)
    
    def test_connection_isolation_between_threads(self):
        """Test that connections are properly isolated between threads."""
        manager = DatabaseConnectionManager()
        thread_connections = {}
        
        def thread_worker(thread_name: str):
            connection = manager.get_connection()
            thread_connections[thread_name] = connection
            time.sleep(0.1)
            
            # Verify this thread's connection is tracked
            info = manager.get_instance_info()
            current_thread_id = threading.get_ident()
            assert current_thread_id in info['active_connection_details']
            assert info['active_connection_details'][current_thread_id] == connection
            
            manager.close_connection()
        
        threads = []
        for i in range(3):
            thread_name = f"thread_{i}"
            thread = threading.Thread(target=thread_worker, args=(thread_name,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all connections were unique
        connections = list(thread_connections.values())
        assert len(connections) == 3
        assert len(set(connections)) == 3  # All unique
        
        # All connections should be closed
        info = manager.get_instance_info()
        assert info['active_connections'] == 0