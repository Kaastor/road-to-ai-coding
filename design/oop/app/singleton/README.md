# Thread-Safe Singleton Pattern Implementation

This module implements a thread-safe Singleton pattern for a database connection manager, ensuring only one instance exists across multiple threads.

## Features

- **Thread-Safe**: Uses double-checked locking pattern with threading.Lock
- **Connection Management**: Tracks active connections per thread
- **Logging**: Comprehensive logging of all operations and thread activities
- **Demonstration**: Multi-threaded demo showing concurrent usage

## Usage

```python
from app.singleton import DatabaseConnectionManager

# Get the singleton instance (same instance across all threads)
db_manager = DatabaseConnectionManager()

# Get a connection for the current thread
connection = db_manager.get_connection()

# Perform database operations
db_manager.simulate_database_operation("SELECT * FROM users", 0.1)

# Close the connection when done
db_manager.close_connection()

# Get instance information
info = db_manager.get_instance_info()
print(f"Total connections created: {info['total_connections_created']}")
```

## Running the Demo

```bash
poetry run python -m app.singleton.demo
```

## Running Tests

```bash
poetry run python -m pytest app/tests/test_singleton.py -v
```

## Implementation Details

### Thread Safety
- Uses `threading.Lock` for synchronization
- Double-checked locking pattern prevents race conditions
- Lazy initialization ensures singleton is created only when needed

### Connection Management
- Each thread gets its own connection ID
- Connections are tracked per thread ID
- Proper cleanup when connections are closed

### Logging
- Thread-aware logging shows which thread performs which operation
- Comprehensive logging of instance creation, connections, and operations
- Helps with debugging multi-threaded scenarios