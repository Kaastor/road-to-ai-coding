"""FastAPI endpoints for elevator control."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .elevator import Elevator
from .models import Direction, ElevatorStatus

logger = logging.getLogger(__name__)

app = FastAPI(title="Elevator App", version="1.0.0")
elevator = Elevator(total_floors=4)

# Serve static files for the web interface
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class FloorCallRequest(BaseModel):
    """Request model for calling elevator to a floor."""
    floor: int
    direction: str


class FloorSelectRequest(BaseModel):
    """Request model for selecting a floor from inside elevator."""
    floor: int


@app.get("/")
async def root():
    """Root endpoint serving basic info."""
    return {"message": "Elevator App API", "status": "running"}


@app.get("/status", response_model=ElevatorStatus)
async def get_status():
    """Get current elevator status."""
    return elevator.get_status()


@app.post("/call")
async def call_elevator(request: FloorCallRequest):
    """Call elevator to a specific floor."""
    try:
        direction = Direction(request.direction.lower())
        await elevator.call_elevator(request.floor, direction)
        return {"message": f"Elevator called to floor {request.floor}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/select")
async def select_floor(request: FloorSelectRequest):
    """Select floor from elevator control panel."""
    try:
        await elevator.select_floor(request.floor)
        return {"message": f"Floor {request.floor} selected"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))