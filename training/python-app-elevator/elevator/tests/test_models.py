"""Tests for elevator data models."""

import pytest
from elevator.models import Direction, ElevatorState, ElevatorRequest, ElevatorStatus


def test_direction_enum():
    """Test Direction enum values."""
    assert Direction.UP.value == "up"
    assert Direction.DOWN.value == "down"
    assert Direction.IDLE.value == "idle"


def test_elevator_state_enum():
    """Test ElevatorState enum values."""
    assert ElevatorState.IDLE.value == "idle"
    assert ElevatorState.MOVING.value == "moving"
    assert ElevatorState.DOORS_OPEN.value == "doors_open"


def test_elevator_request():
    """Test ElevatorRequest dataclass."""
    request = ElevatorRequest(
        floor=3,
        direction=Direction.UP,
        timestamp=1234567.89
    )
    
    assert request.floor == 3
    assert request.direction == Direction.UP
    assert request.timestamp == 1234567.89


def test_elevator_status():
    """Test ElevatorStatus dataclass."""
    status = ElevatorStatus(
        current_floor=2,
        direction=Direction.DOWN,
        state=ElevatorState.MOVING,
        queue=[1, 4]
    )
    
    assert status.current_floor == 2
    assert status.direction == Direction.DOWN
    assert status.state == ElevatorState.MOVING
    assert status.queue == [1, 4]