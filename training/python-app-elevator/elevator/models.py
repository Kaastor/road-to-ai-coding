"""Data models for the elevator application."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class Direction(Enum):
    """Elevator movement direction."""
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


class ElevatorState(Enum):
    """Elevator operational state."""
    IDLE = "idle"
    MOVING = "moving"
    DOORS_OPEN = "doors_open"


@dataclass
class ElevatorRequest:
    """Represents a request for the elevator."""
    floor: int
    direction: Direction
    timestamp: float


@dataclass
class ElevatorStatus:
    """Current status of the elevator."""
    current_floor: int
    direction: Direction
    state: ElevatorState
    queue: List[int]