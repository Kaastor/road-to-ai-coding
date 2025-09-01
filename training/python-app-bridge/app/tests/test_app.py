"""Tests for the in-memory bridge system."""

import pytest
import time
import threading
from app.app import BridgeSystem, Server, Client, Task, TaskStatus, ConsoleUI


class TestTask:
    """Test cases for Task class."""
    
    def test_task_creation(self):
        """Test task creation with default values."""
        task = Task(1, "test task", 5.0)
        assert task.id == 1
        assert task.description == "test task"
        assert task.timeout == 5.0
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.assigned_client_id is None
        assert task.created_at is not None
    
    def test_task_with_custom_timestamp(self):
        """Test task creation with custom timestamp."""
        timestamp = time.time()
        task = Task(1, "test", 5.0, created_at=timestamp)
        assert task.created_at == timestamp


class TestServer:
    """Test cases for Server class."""
    
    def test_server_initialization(self):
        """Test server initialization."""
        server = Server()
        assert server.task_counter == 0
        assert server.get_pending_task_count() == 0
        assert len(server.active_tasks) == 0
    
    def test_add_task(self):
        """Test adding a task to the server."""
        server = Server()
        task = server.add_task("test task", 5.0)
        
        assert task.id == 1
        assert task.description == "test task"
        assert task.timeout == 5.0
        assert server.get_pending_task_count() == 1
        assert task.id in server.active_tasks
        assert task.id in server.result_events
    
    def test_multiple_tasks(self):
        """Test adding multiple tasks."""
        server = Server()
        task1 = server.add_task("task 1", 3.0)
        task2 = server.add_task("task 2", 4.0)
        
        assert task1.id == 1
        assert task2.id == 2
        assert server.get_pending_task_count() == 2
    
    def test_get_task_for_client(self):
        """Test client getting a task."""
        server = Server()
        task = server.add_task("test task", 5.0)
        
        retrieved_task = server.get_task_for_client(1)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.assigned_client_id == 1
        assert retrieved_task.status == TaskStatus.PROCESSING
        assert server.get_pending_task_count() == 0
    
    def test_get_task_from_empty_queue(self):
        """Test getting task when queue is empty."""
        server = Server()
        task = server.get_task_for_client(1)
        assert task is None
    
    def test_submit_result(self):
        """Test submitting task result."""
        server = Server()
        task = server.add_task("test task", 5.0)
        retrieved_task = server.get_task_for_client(1)
        
        server.submit_result(task.id, 1, "Success")
        
        assert task.result == "Success"
        assert task.status == TaskStatus.COMPLETED
    
    def test_submit_result_wrong_client(self):
        """Test submitting result from wrong client."""
        server = Server()
        task = server.add_task("test task", 5.0)
        server.get_task_for_client(1)
        
        # Try to submit result from different client
        server.submit_result(task.id, 2, "Success")
        
        # Result should not be accepted
        assert task.result is None
        assert task.status == TaskStatus.PROCESSING
    
    def test_wait_for_task_result_success(self):
        """Test waiting for task result successfully."""
        server = Server()
        task = server.add_task("test task", 2.0)
        
        def submit_result():
            time.sleep(0.5)
            server.get_task_for_client(1)
            server.submit_result(task.id, 1, "Success")
        
        thread = threading.Thread(target=submit_result)
        thread.start()
        
        result = server.wait_for_task_result(task)
        thread.join()
        
        assert result is True
        assert task.status == TaskStatus.COMPLETED
    
    def test_wait_for_task_result_timeout(self):
        """Test waiting for task result with timeout."""
        server = Server()
        task = server.add_task("test task", 0.5)
        
        result = server.wait_for_task_result(task)
        
        assert result is False
        assert task.status == TaskStatus.TIMEOUT
    
    def test_cleanup_completed_task(self):
        """Test cleaning up completed task."""
        server = Server()
        task = server.add_task("test task", 5.0)
        task_id = task.id
        
        server.cleanup_completed_task(task_id)
        
        assert task_id not in server.active_tasks
        assert task_id not in server.result_events
        assert task_id not in server.client_assignments


class TestClient:
    """Test cases for Client class."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        server = Server()
        client = Client(1, server)
        
        assert client.client_id == 1
        assert client.server is server
        assert client.is_running is False
        assert client.thread is None
    
    def test_start_stop_client(self):
        """Test starting and stopping client."""
        server = Server()
        client = Client(1, server)
        
        # Start client
        client.start()
        assert client.is_running is True
        assert client.thread is not None
        time.sleep(0.1)  # Allow thread to start
        
        # Stop client
        client.stop()
        assert client.is_running is False
    
    def test_client_processes_task(self):
        """Test client processing a task."""
        server = Server()
        client = Client(1, server)
        
        # Add task and start client
        task = server.add_task("test task", 10.0)
        client.start()
        
        # Wait for client to process task
        time.sleep(6.0)  # Max processing time is 5 seconds
        
        client.stop()
        
        # Task should be completed
        assert task.status == TaskStatus.COMPLETED
        assert task.result is not None
        assert task.assigned_client_id == 1


class TestBridgeSystem:
    """Test cases for BridgeSystem class."""
    
    def test_bridge_initialization(self):
        """Test bridge system initialization."""
        bridge = BridgeSystem()
        
        assert len(bridge.clients) == 3
        assert 1 in bridge.clients
        assert 2 in bridge.clients
        assert 3 in bridge.clients
        assert bridge.server is not None
    
    def test_start_stop_client(self):
        """Test starting and stopping clients."""
        bridge = BridgeSystem()
        
        # Start client 1
        result = bridge.start_client(1)
        assert result is True
        
        status = bridge.get_client_status()
        assert status[1] == "UP"
        assert status[2] == "DOWN"
        assert status[3] == "DOWN"
        
        # Stop client 1
        result = bridge.stop_client(1)
        assert result is True
        
        status = bridge.get_client_status()
        assert status[1] == "DOWN"
    
    def test_start_stop_invalid_client(self):
        """Test starting/stopping invalid client."""
        bridge = BridgeSystem()
        
        result = bridge.start_client(99)
        assert result is False
        
        result = bridge.stop_client(99)
        assert result is False
    
    def test_get_client_status(self):
        """Test getting client status."""
        bridge = BridgeSystem()
        
        status = bridge.get_client_status()
        assert len(status) == 3
        for client_id in [1, 2, 3]:
            assert status[client_id] == "DOWN"
    
    def test_task_processing_integration(self):
        """Test end-to-end task processing."""
        bridge = BridgeSystem()
        
        # Start a client
        bridge.start_client(1)
        time.sleep(0.1)
        
        # Add task (this will block until completion or timeout)
        def add_task():
            bridge.add_task("integration test", 10.0)
        
        # Run task addition in separate thread to avoid blocking test
        task_thread = threading.Thread(target=add_task)
        task_thread.start()
        task_thread.join(timeout=7.0)  # Max wait time
        
        # Clean up
        bridge.shutdown()
        
        # Task should have been processed
        assert task_thread.is_alive() is False
    
    def test_shutdown(self):
        """Test system shutdown."""
        bridge = BridgeSystem()
        
        # Start all clients
        for client_id in [1, 2, 3]:
            bridge.start_client(client_id)
        
        # Verify all are running
        status = bridge.get_client_status()
        for client_id in [1, 2, 3]:
            assert status[client_id] == "UP"
        
        # Shutdown
        bridge.shutdown()
        
        # Verify all are stopped
        status = bridge.get_client_status()
        for client_id in [1, 2, 3]:
            assert status[client_id] == "DOWN"


class TestConsoleUI:
    """Test cases for ConsoleUI class."""
    
    def test_console_ui_initialization(self):
        """Test console UI initialization."""
        ui = ConsoleUI()
        
        assert ui.bridge is not None
        assert ui.running is True
        assert len(ui.bridge.clients) == 3


class TestConcurrency:
    """Test cases for concurrent operations."""
    
    def test_multiple_clients_processing(self):
        """Test multiple clients processing tasks concurrently."""
        bridge = BridgeSystem()
        
        # Start all clients
        for client_id in [1, 2, 3]:
            bridge.start_client(client_id)
        
        time.sleep(0.1)  # Allow clients to start
        
        # Add multiple tasks concurrently
        def add_tasks():
            for i in range(3):
                bridge.server.add_task(f"concurrent task {i}", 10.0)
        
        task_thread = threading.Thread(target=add_tasks)
        task_thread.start()
        task_thread.join()
        
        # Wait for all tasks to be picked up
        time.sleep(1.0)
        
        # All tasks should be picked up by clients
        assert bridge.server.get_pending_task_count() == 0
        
        # Clean up
        bridge.shutdown()
    
    def test_task_timeout_with_no_clients(self):
        """Test task timeout when no clients are available."""
        bridge = BridgeSystem()
        
        # Don't start any clients
        task = bridge.server.add_task("timeout test", 1.0)
        
        result = bridge.server.wait_for_task_result(task)
        
        assert result is False
        assert task.status == TaskStatus.TIMEOUT


@pytest.fixture
def bridge_system():
    """Fixture providing a clean bridge system for each test."""
    bridge = BridgeSystem()
    yield bridge
    bridge.shutdown()


@pytest.fixture
def server():
    """Fixture providing a clean server for each test."""
    return Server()


def test_task_assignment_fairness(bridge_system):
    """Test that tasks are assigned fairly among clients."""
    # Start all clients
    for client_id in [1, 2, 3]:
        bridge_system.start_client(client_id)
    
    time.sleep(0.1)  # Allow clients to start
    
    # Add several tasks
    tasks = []
    for i in range(6):
        task = bridge_system.server.add_task(f"fairness test {i}", 15.0)
        tasks.append(task)
    
    # Wait for tasks to be assigned
    time.sleep(0.5)
    
    # Check that tasks are distributed among clients
    assigned_clients = set()
    for task in tasks:
        if task.assigned_client_id:
            assigned_clients.add(task.assigned_client_id)
    
    # At least 2 different clients should have received tasks
    assert len(assigned_clients) >= 2


def test_system_robustness_under_load(bridge_system):
    """Test system behavior under high load."""
    # Start all clients
    for client_id in [1, 2, 3]:
        bridge_system.start_client(client_id)
    
    time.sleep(0.1)
    
    # Add many tasks
    num_tasks = 10
    for i in range(num_tasks):
        bridge_system.server.add_task(f"load test {i}", 20.0)
    
    # Wait for some processing
    time.sleep(2.0)
    
    # System should still be responsive
    status = bridge_system.get_client_status()
    assert status[1] == "UP"
    assert status[2] == "UP"
    assert status[3] == "UP"


def test_concurrent_client_start_stop():
    """Test thread safety of concurrent client start/stop operations."""
    bridge = BridgeSystem()
    
    def start_stop_client(client_id):
        """Rapidly start and stop a client."""
        for _ in range(20):
            bridge.start_client(client_id)
            time.sleep(0.001)  # Brief pause
            bridge.stop_client(client_id)
            time.sleep(0.001)
    
    # Start multiple threads performing start/stop on different clients
    threads = []
    for client_id in [1, 2, 3]:
        thread = threading.Thread(target=start_stop_client, args=(client_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All clients should be in a consistent state
    status = bridge.get_client_status()
    for client_id in [1, 2, 3]:
        assert status[client_id] in ["UP", "DOWN"]
    
    bridge.shutdown()


def test_concurrent_task_submission():
    """Test thread safety of concurrent task submission and result handling."""
    bridge = BridgeSystem()
    
    # Start all clients
    for client_id in [1, 2, 3]:
        bridge.start_client(client_id)
    
    time.sleep(0.1)
    
    completed_tasks = []
    task_lock = threading.Lock()
    
    def add_tasks(thread_id):
        """Add multiple tasks from different threads."""
        for i in range(5):
            task = bridge.server.add_task(f"thread_{thread_id}_task_{i}", 10.0)
            # Wait for result
            if bridge.server.wait_for_task_result(task):
                with task_lock:
                    completed_tasks.append(task.id)
            bridge.server.cleanup_completed_task(task.id)
    
    # Create multiple threads adding tasks concurrently
    threads = []
    for thread_id in range(4):
        thread = threading.Thread(target=add_tasks, args=(thread_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Some tasks should have completed successfully
    assert len(completed_tasks) > 0
    
    # All task IDs should be unique
    assert len(completed_tasks) == len(set(completed_tasks))
    
    bridge.shutdown()


def test_race_condition_prevention():
    """Test that race conditions are prevented in critical sections."""
    server = Server()
    
    # Test concurrent task addition
    task_ids = []
    task_ids_lock = threading.Lock()
    
    def add_multiple_tasks():
        for i in range(10):
            task = server.add_task(f"race_test_{i}", 5.0)
            with task_ids_lock:
                task_ids.append(task.id)
    
    # Start multiple threads adding tasks
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=add_multiple_tasks)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # All task IDs should be unique (no race in counter)
    assert len(task_ids) == len(set(task_ids))
    
    # Task IDs should be sequential starting from 1
    sorted_ids = sorted(task_ids)
    expected_ids = list(range(1, len(task_ids) + 1))
    assert sorted_ids == expected_ids


def test_task_list_functionality():
    """Test task list display functionality."""
    server = Server()
    
    # Initially no tasks
    tasks = server.get_all_tasks()
    assert len(tasks['active']) == 0
    assert len(tasks['completed']) == 0
    
    # Add some tasks
    task1 = server.add_task("Task 1", 5.0)
    task2 = server.add_task("Task 2", 3.0)
    
    tasks = server.get_all_tasks()
    assert len(tasks['active']) == 2
    assert len(tasks['completed']) == 0
    
    # Simulate task completion
    task1.status = TaskStatus.COMPLETED
    task1.result = "Success"
    
    # Clean up one task
    server.cleanup_completed_task(task1.id)
    
    tasks = server.get_all_tasks()
    assert len(tasks['active']) == 1  # task2 still active
    assert len(tasks['completed']) == 1  # task1 moved to completed
    
    # Verify completed task details
    completed_task = tasks['completed'][0]
    assert completed_task.id == task1.id
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.result == "Success"


def test_bridge_system_show_task_list(bridge_system):
    """Test BridgeSystem task list display method."""
    # Start a client
    bridge_system.start_client(1)
    time.sleep(0.1)
    
    # Add a task directly to server (without blocking)
    task = bridge_system.server.add_task("Test task", 10.0)
    
    # This should not raise an exception
    bridge_system.show_task_list()
    
    # Clean up
    bridge_system.server.cleanup_completed_task(task.id)