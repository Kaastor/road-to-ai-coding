"""
Multi-threaded demonstration of the thread-safe Singleton pattern.

This script demonstrates how the DatabaseConnectionManager singleton works
across multiple threads, ensuring only one instance is created while
handling concurrent access safely.
"""

import threading
import time
import random
from typing import List

from .database_manager import DatabaseConnectionManager


def worker_thread(thread_name: str, operations: int = 3) -> None:
    """
    Worker function that simulates database operations in a thread.
    
    Args:
        thread_name: Name identifier for the thread
        operations: Number of operations to perform
    """
    # Get the singleton instance
    db_manager = DatabaseConnectionManager()
    
    print(f"\n[{thread_name}] Worker started")
    print(f"[{thread_name}] Instance info: {db_manager.get_instance_info()}")
    
    # Get a connection
    connection = db_manager.get_connection()
    
    try:
        # Perform some database operations
        for i in range(operations):
            operation_name = f"Operation_{i+1}"
            operation_duration = random.uniform(0.1, 0.3)
            
            db_manager.simulate_database_operation(operation_name, operation_duration)
            
            # Small delay between operations
            time.sleep(random.uniform(0.05, 0.1))
    
    finally:
        # Always close the connection
        db_manager.close_connection()
        print(f"[{thread_name}] Worker finished")


def demonstrate_singleton_behavior() -> None:
    """
    Demonstrate that all threads get the same singleton instance.
    """
    print("=== Singleton Instance Verification ===")
    
    instances = []
    threads = []
    
    def collect_instance():
        instance = DatabaseConnectionManager()
        instances.append(instance)
    
    # Create multiple threads that get the singleton instance
    for i in range(5):
        thread = threading.Thread(target=collect_instance)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all instances are the same
    print(f"Number of threads: {len(instances)}")
    print(f"All instances are the same: {all(instance is instances[0] for instance in instances)}")
    print(f"Instance IDs: {[id(instance) for instance in instances]}")


def run_multithreaded_demo() -> None:
    """
    Run the complete multi-threaded demonstration.
    """
    print("=== Thread-Safe Singleton Database Connection Manager Demo ===\n")
    
    # First demonstrate singleton behavior
    demonstrate_singleton_behavior()
    
    print("\n=== Multi-threaded Database Operations Demo ===")
    
    # Create multiple threads that will use the database manager
    threads: List[threading.Thread] = []
    
    # Create worker threads
    for i in range(4):
        thread_name = f"Worker-{i+1}"
        thread = threading.Thread(
            target=worker_thread,
            args=(thread_name, random.randint(2, 4))
        )
        threads.append(thread)
    
    # Start all threads
    print(f"\nStarting {len(threads)} worker threads...")
    start_time = time.time()
    
    for thread in threads:
        thread.start()
        time.sleep(0.1)  # Stagger thread starts slightly
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # Show final statistics
    db_manager = DatabaseConnectionManager()
    final_info = db_manager.get_instance_info()
    
    print(f"\n=== Final Statistics ===")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    print(f"Singleton instance ID: {final_info['instance_id']}")
    print(f"Total connections created: {final_info['total_connections_created']}")
    print(f"Active connections remaining: {final_info['active_connections']}")
    print(f"Instance created by thread: {final_info['creator_thread_id']}")
    print(f"Instance creation time: {final_info['creation_time']}")


if __name__ == "__main__":
    run_multithreaded_demo()