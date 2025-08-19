"""Tests for elevator core functionality."""

import pytest
import asyncio
from elevator.elevator import Elevator
from elevator.models import Direction, ElevatorState


@pytest.fixture
def elevator():
    """Create a fresh elevator instance for testing."""
    return Elevator(total_floors=4)


class TestElevator:
    """Test cases for Elevator class."""
    
    def test_initialization(self, elevator):
        """Test elevator initialization."""
        assert elevator.total_floors == 4
        assert elevator.current_floor == 1
        assert elevator.direction == Direction.IDLE
        assert elevator.state == ElevatorState.IDLE
        assert elevator.request_queue == []
        assert not elevator.is_running
    
    @pytest.mark.asyncio
    async def test_call_elevator_valid_floor(self, elevator):
        """Test calling elevator to valid floor."""
        # Mock the processing to avoid automatic queue clearing
        original_process = elevator.process_requests
        async def mock_process():
            pass
        elevator.process_requests = mock_process
        
        await elevator.call_elevator(3, Direction.UP)
        assert 3 in elevator.request_queue
        
        # Restore original method
        elevator.process_requests = original_process
    
    @pytest.mark.asyncio
    async def test_call_elevator_invalid_floor(self, elevator):
        """Test calling elevator to invalid floor."""
        with pytest.raises(ValueError):
            await elevator.call_elevator(0, Direction.UP)
        
        with pytest.raises(ValueError):
            await elevator.call_elevator(5, Direction.UP)
    
    @pytest.mark.asyncio
    async def test_select_floor_valid(self, elevator):
        """Test selecting valid floor from control panel."""
        await elevator.select_floor(2)
        assert 2 in elevator.request_queue
    
    @pytest.mark.asyncio
    async def test_select_floor_invalid(self, elevator):
        """Test selecting invalid floor from control panel."""
        with pytest.raises(ValueError):
            await elevator.select_floor(0)
        
        with pytest.raises(ValueError):
            await elevator.select_floor(5)
    
    @pytest.mark.asyncio
    async def test_move_to_floor_up(self, elevator):
        """Test moving elevator up."""
        await elevator.move_to_floor(3)
        assert elevator.current_floor == 3
        assert elevator.state == ElevatorState.DOORS_OPEN
    
    @pytest.mark.asyncio
    async def test_move_to_floor_down(self, elevator):
        """Test moving elevator down."""
        elevator.current_floor = 4  # Start from 4th floor
        await elevator.move_to_floor(2)
        assert elevator.current_floor == 2
        assert elevator.state == ElevatorState.DOORS_OPEN
    
    @pytest.mark.asyncio
    async def test_move_to_same_floor(self, elevator):
        """Test moving to same floor (should not move)."""
        initial_floor = elevator.current_floor
        await elevator.move_to_floor(initial_floor)
        assert elevator.current_floor == initial_floor
    
    def test_get_status(self, elevator):
        """Test getting elevator status."""
        elevator.request_queue = [2, 4]
        status = elevator.get_status()
        
        assert status.current_floor == 1
        assert status.direction == Direction.IDLE
        assert status.state == ElevatorState.IDLE
        assert status.queue == [2, 4]
    
    @pytest.mark.asyncio
    async def test_duplicate_requests_ignored(self, elevator):
        """Test that duplicate floor requests are ignored."""
        # Mock the processing to avoid automatic queue clearing
        original_process = elevator.process_requests
        async def mock_process():
            pass
        elevator.process_requests = mock_process
        
        await elevator.call_elevator(3, Direction.UP)
        await elevator.call_elevator(3, Direction.UP)
        
        # Should only have one instance of floor 3
        assert elevator.request_queue.count(3) == 1
        
        # Restore original method
        elevator.process_requests = original_process
    
    @pytest.mark.asyncio
    async def test_wait_for_passenger_input(self, elevator):
        """Test passenger input waiting (timing test)."""
        import time
        
        elevator.state = ElevatorState.DOORS_OPEN
        start_time = time.time()
        
        await elevator.wait_for_passenger_input()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should take approximately 5 seconds (allowing some tolerance)
        assert 4.8 <= elapsed <= 5.2
        assert elevator.state == ElevatorState.IDLE