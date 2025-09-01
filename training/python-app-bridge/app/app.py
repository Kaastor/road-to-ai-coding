"""In-Memory Bridge System with Multi-Client, Per-Task Timeout, and Interactive Console UI."""

import threading
import time
import queue
import random
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """Task data structure."""
    id: int
    description: str
    timeout: float
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    assigned_client_id: Optional[int] = None
    created_at: float = None

    def __post_init__(self):
        """Initialize creation timestamp."""
        if self.created_at is None:
            self.created_at = time.time()


class Client:
    """Client worker thread that processes tasks."""
    
    def __init__(self, client_id: int, server: 'Server'):
        """Initialize client.
        
        Args:
            client_id: Unique identifier for the client
            server: Reference to the server instance
        """
        self.client_id = client_id
        self.server = server
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._state_lock = threading.Lock()

    def start(self) -> None:
        """Start the client thread."""
        with self._state_lock:
            if self.is_running:
                return
            
            self.is_running = True
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Stop the client thread."""
        with self._state_lock:
            if not self.is_running:
                return
            
            self.is_running = False
            self._stop_event.set()
            
        # Join outside the lock to avoid holding it during potentially long wait
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _run(self) -> None:
        """Main client execution loop."""
        while self.is_running and not self._stop_event.is_set():
            try:
                task = self.server.get_task_for_client(self.client_id)
                if task:
                    self._process_task(task)
                else:
                    time.sleep(0.1)  # Brief pause when no tasks available
            except Exception as e:
                print(f"Client {self.client_id} error: {e}")
                time.sleep(0.1)

    def _process_task(self, task: Task) -> None:
        """Process a task.
        
        Args:
            task: Task to process
        """
        print(f"Client {self.client_id} processing task '{task.description}'...")
        
        # Simulate processing time (1-5 seconds)
        processing_time = random.uniform(1, 5)
        
        # Check if we should stop during processing
        if self._stop_event.wait(timeout=processing_time):
            # Client was stopped during processing
            return
        
        # Generate random result
        results = ["Success", "Failed", "Partial Success", "Error", "Completed"]
        result = random.choice(results)
        
        # Submit result back to server
        self.server.submit_result(task.id, self.client_id, result)


class Server:
    """Server that manages tasks and client coordination."""
    
    def __init__(self):
        """Initialize server."""
        self.task_queue = queue.Queue()
        self.active_tasks: dict[int, Task] = {}
        self.completed_tasks: dict[int, Task] = {}  # Store completed tasks for history
        self.task_counter = 0
        self.task_lock = threading.Lock()
        self.result_events: dict[int, threading.Event] = {}
        self.client_assignments = {}  # task_id -> client_id

    def add_task(self, description: str, timeout: float) -> Task:
        """Add a new task to the queue.
        
        Args:
            description: Task description
            timeout: Timeout in seconds
            
        Returns:
            Created task
        """
        with self.task_lock:
            self.task_counter += 1
            task = Task(
                id=self.task_counter,
                description=description,
                timeout=timeout
            )
            self.active_tasks[task.id] = task
            self.result_events[task.id] = threading.Event()
            self.task_queue.put(task)
            return task

    def get_task_for_client(self, client_id: int) -> Optional[Task]:
        """Get next available task for a client.
        
        Args:
            client_id: ID of requesting client
            
        Returns:
            Task if available, None otherwise
        """
        with self.task_lock:
            try:
                task = self.task_queue.get_nowait()
                # Modify task properties atomically within the lock
                task.status = TaskStatus.PROCESSING
                task.assigned_client_id = client_id
                self.client_assignments[task.id] = client_id
                return task
            except queue.Empty:
                return None

    def submit_result(self, task_id: int, client_id: int, result: str) -> None:
        """Submit task result from client.
        
        Args:
            task_id: ID of completed task
            client_id: ID of client that completed the task
            result: Task result
        """
        with self.task_lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                # Only accept results from the assigned client and if task hasn't timed out
                if (task.assigned_client_id == client_id and 
                    task.status == TaskStatus.PROCESSING):
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    
                    # Signal that result is available
                    if task_id in self.result_events:
                        self.result_events[task_id].set()

    def wait_for_task_result(self, task: Task) -> bool:
        """Wait for task result with timeout.
        
        Args:
            task: Task to wait for
            
        Returns:
            True if task completed, False if timed out
        """
        # Get event reference safely under lock
        with self.task_lock:
            event = self.result_events.get(task.id)
            if not event:
                return False
        
        print("Waiting for a client...")
        completed = event.wait(timeout=task.timeout)
        
        with self.task_lock:
            # Double-check event still exists after waiting
            if task.id not in self.result_events:
                return False
                
            if completed and task.status == TaskStatus.COMPLETED:
                return True
            else:
                task.status = TaskStatus.TIMEOUT
                # Remove from client assignment if timed out
                if task.id in self.client_assignments:
                    del self.client_assignments[task.id]
                return False

    def get_pending_task_count(self) -> int:
        """Get number of pending tasks.
        
        Returns:
            Number of pending tasks
        """
        # qsize() is thread-safe but can be inaccurate in high concurrency
        # For better accuracy, we could maintain a counter, but qsize() is sufficient for status reporting
        return self.task_queue.qsize()

    def cleanup_completed_task(self, task_id: int) -> None:
        """Clean up completed or timed out task.
        
        Args:
            task_id: ID of task to clean up
        """
        with self.task_lock:
            # Move completed/timed out task to history before cleaning up
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.status in [TaskStatus.COMPLETED, TaskStatus.TIMEOUT]:
                    self.completed_tasks[task_id] = task
            
            self.active_tasks.pop(task_id, None)
            self.result_events.pop(task_id, None)
            self.client_assignments.pop(task_id, None)

    def get_all_tasks(self) -> dict[str, list[Task]]:
        """Get all tasks organized by status.
        
        Returns:
            Dictionary with 'active' and 'completed' task lists
        """
        with self.task_lock:
            # Get active tasks (pending and processing)
            active_tasks = []
            for task in self.active_tasks.values():
                active_tasks.append(task)
            
            # Get completed tasks (completed and timeout)
            completed_tasks = list(self.completed_tasks.values())
            
            return {
                'active': active_tasks,
                'completed': completed_tasks
            }


class BridgeSystem:
    """Main bridge system coordinating server and clients."""
    
    def __init__(self):
        """Initialize bridge system."""
        self.server = Server()
        self.clients = {
            1: Client(1, self.server),
            2: Client(2, self.server),
            3: Client(3, self.server)
        }
        
    def start_client(self, client_id: int) -> bool:
        """Start a specific client.
        
        Args:
            client_id: ID of client to start
            
        Returns:
            True if started successfully, False otherwise
        """
        if client_id in self.clients:
            self.clients[client_id].start()
            return True
        return False
        
    def stop_client(self, client_id: int) -> bool:
        """Stop a specific client.
        
        Args:
            client_id: ID of client to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if client_id in self.clients:
            self.clients[client_id].stop()
            return True
        return False
        
    def get_client_status(self) -> dict[int, str]:
        """Get status of all clients.
        
        Returns:
            Dictionary mapping client ID to status
        """
        status = {}
        for client_id, client in self.clients.items():
            # Read client state with proper synchronization
            with client._state_lock:
                status[client_id] = "UP" if client.is_running else "DOWN"
        return status
    
    def add_task(self, description: str, timeout: float) -> None:
        """Add and process a task.
        
        Args:
            description: Task description
            timeout: Timeout in seconds
        """
        task = self.server.add_task(description, timeout)
        
        # Wait for result or timeout
        if self.server.wait_for_task_result(task):
            print(f"Task '{task.description}' completed by Client {task.assigned_client_id}: {task.result}")
        else:
            print(f"Task '{task.description}' timed out. No clients responded in time.")
        
        # Clean up task
        self.server.cleanup_completed_task(task.id)
    
    def show_status(self) -> None:
        """Display system status."""
        print("Clients status:")
        for client_id, status in self.get_client_status().items():
            print(f"Client {client_id}: {status}")
        print(f"Pending tasks: {self.server.get_pending_task_count()}")
    
    def show_task_list(self) -> None:
        """Display all tasks (active and completed)."""
        tasks = self.server.get_all_tasks()
        
        print("\n" + "=" * 50)
        print("TASK LIST")
        print("=" * 50)
        
        # Display active tasks
        print("\nACTIVE TASKS:")
        print("-" * 30)
        if tasks['active']:
            for task in sorted(tasks['active'], key=lambda t: t.id):
                status_str = task.status.value.upper()
                client_info = f" (Client {task.assigned_client_id})" if task.assigned_client_id else ""
                print(f"[{task.id:3d}] {status_str:10} | {task.description}{client_info}")
                print(f"      Timeout: {task.timeout}s | Created: {time.strftime('%H:%M:%S', time.localtime(task.created_at))}")
        else:
            print("No active tasks.")
        
        # Display completed tasks
        print("\nCOMPLETED TASKS:")
        print("-" * 30)
        if tasks['completed']:
            for task in sorted(tasks['completed'], key=lambda t: t.id, reverse=True)[:10]:  # Show last 10
                status_str = task.status.value.upper()
                client_info = f" (Client {task.assigned_client_id})" if task.assigned_client_id else ""
                result_info = f" -> {task.result}" if task.result else ""
                print(f"[{task.id:3d}] {status_str:10} | {task.description}{client_info}{result_info}")
                print(f"      Timeout: {task.timeout}s | Created: {time.strftime('%H:%M:%S', time.localtime(task.created_at))}")
            if len(tasks['completed']) > 10:
                print(f"... and {len(tasks['completed']) - 10} more completed tasks")
        else:
            print("No completed tasks.")
        
        print("=" * 50)
    
    def shutdown(self) -> None:
        """Shutdown all clients."""
        for client in self.clients.values():
            client.stop()


class ConsoleUI:
    """Console user interface for the bridge system."""
    
    def __init__(self):
        """Initialize console UI."""
        self.bridge = BridgeSystem()
        self.running = True
    
    def display_menu(self) -> None:
        """Display main menu."""
        print("\nMenu:")
        print("1. Add task")
        print("2. Start client 1")
        print("3. Stop client 1")
        print("4. Start client 2")
        print("5. Stop client 2")
        print("6. Start client 3")
        print("7. Stop client 3")
        print("8. Show status")
        print("9. Show task list")
        print("10. Exit")
    
    def handle_add_task(self) -> None:
        """Handle adding a new task."""
        try:
            description = input("Enter task description: ").strip()
            if not description:
                print("Task description cannot be empty.")
                return
            
            timeout_str = input("Enter timeout in seconds: ").strip()
            timeout = float(timeout_str)
            if timeout <= 0:
                print("Timeout must be positive.")
                return
            
            self.bridge.add_task(description, timeout)
        except ValueError:
            print("Invalid timeout value. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
    
    def handle_client_action(self, action: str, client_id: int) -> None:
        """Handle client start/stop actions.
        
        Args:
            action: "start" or "stop"
            client_id: ID of client
        """
        if action == "start":
            if self.bridge.start_client(client_id):
                print(f"Client {client_id} started.")
            else:
                print(f"Failed to start Client {client_id}.")
        elif action == "stop":
            if self.bridge.stop_client(client_id):
                print(f"Client {client_id} stopped.")
            else:
                print(f"Failed to stop Client {client_id}.")
    
    def run(self) -> None:
        """Run the console UI main loop."""
        print("In-Memory Bridge System")
        print("=" * 30)
        
        while self.running:
            try:
                self.display_menu()
                choice = input("> ").strip()
                
                if choice == "1":
                    self.handle_add_task()
                elif choice == "2":
                    self.handle_client_action("start", 1)
                elif choice == "3":
                    self.handle_client_action("stop", 1)
                elif choice == "4":
                    self.handle_client_action("start", 2)
                elif choice == "5":
                    self.handle_client_action("stop", 2)
                elif choice == "6":
                    self.handle_client_action("start", 3)
                elif choice == "7":
                    self.handle_client_action("stop", 3)
                elif choice == "8":
                    self.bridge.show_status()
                elif choice == "9":
                    self.bridge.show_task_list()
                elif choice == "10":
                    print("Exiting.")
                    self.running = False
                else:
                    print("Invalid choice. Please select 1-10.")
                    
            except KeyboardInterrupt:
                print("\nExiting.")
                self.running = False
            except Exception as e:
                print(f"An error occurred: {e}")
        
        # Shutdown system
        self.bridge.shutdown()


def main() -> None:
    """Main entry point for the application."""
    ui = ConsoleUI()
    ui.run()


if __name__ == "__main__":
    main()