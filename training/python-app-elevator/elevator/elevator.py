"""Core elevator logic and state management."""

import asyncio
import logging
from typing import List, Optional

from .models import Direction, ElevatorState, ElevatorRequest, ElevatorStatus

logger = logging.getLogger(__name__)


class Elevator:
    """Elevator simulation with event handling."""
    
    def __init__(self, total_floors: int = 4):
        """Initialize elevator with specified number of floors."""
        self.total_floors = total_floors
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.request_queue: List[int] = []
        self.is_running = False
        
    async def call_elevator(self, floor: int, direction: Direction) -> None:
        """Handle elevator call from a floor."""
        if floor < 1 or floor > self.total_floors:
            raise ValueError(f"Floor must be between 1 and {self.total_floors}")
            
        if floor not in self.request_queue:
            self.request_queue.append(floor)
            logger.info(f"Elevator called to floor {floor} going {direction.value}")
            
        if not self.is_running:
            await self.process_requests()
    
    async def select_floor(self, floor: int) -> None:
        """Handle floor selection from elevator control panel."""
        if floor < 1 or floor > self.total_floors:
            raise ValueError(f"Floor must be between 1 and {self.total_floors}")
            
        if floor != self.current_floor and floor not in self.request_queue:
            self.request_queue.append(floor)
            logger.info(f"Floor {floor} selected from control panel")
    
    async def process_requests(self) -> None:
        """Process all pending elevator requests."""
        self.is_running = True
        
        while self.request_queue:
            # Sort queue by proximity to current floor
            self.request_queue.sort(key=lambda x: abs(x - self.current_floor))
            next_floor = self.request_queue.pop(0)
            
            await self.move_to_floor(next_floor)
            await self.wait_for_passenger_input()
            
        # Return to ground floor when idle
        if self.current_floor != 1:
            await self.move_to_floor(1)
            
        self.is_running = False
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
    
    async def move_to_floor(self, target_floor: int) -> None:
        """Move elevator to specified floor."""
        if target_floor == self.current_floor:
            return
            
        self.direction = Direction.UP if target_floor > self.current_floor else Direction.DOWN
        self.state = ElevatorState.MOVING
        
        logger.info(f"Moving from floor {self.current_floor} to floor {target_floor}")
        
        # Simulate movement (1 second per floor)
        floors_to_move = abs(target_floor - self.current_floor)
        
        for _ in range(floors_to_move):
            await asyncio.sleep(1)
            if self.direction == Direction.UP:
                self.current_floor += 1
            else:
                self.current_floor -= 1
            logger.debug(f"Now at floor {self.current_floor}")
        
        self.state = ElevatorState.DOORS_OPEN
        logger.info(f"Arrived at floor {self.current_floor}")
    
    async def wait_for_passenger_input(self) -> None:
        """Wait 5 seconds for passenger to select floor."""
        logger.info("Doors open - waiting for floor selection")
        await asyncio.sleep(5)
        self.state = ElevatorState.IDLE
        logger.info("Doors closed")
    
    def get_status(self) -> ElevatorStatus:
        """Get current elevator status."""
        return ElevatorStatus(
            current_floor=self.current_floor,
            direction=self.direction,
            state=self.state,
            queue=self.request_queue.copy()
        )