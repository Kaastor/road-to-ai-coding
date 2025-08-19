"""Tests for elevator API endpoints."""

import pytest
from fastapi.testclient import TestClient
from elevator.api import app


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


class TestElevatorAPI:
    """Test cases for elevator API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Elevator App API"
        assert data["status"] == "running"
    
    def test_get_status_endpoint(self, client):
        """Test status endpoint returns elevator status."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields are present
        assert "current_floor" in data
        assert "direction" in data
        assert "state" in data
        assert "queue" in data
    
    def test_call_elevator_valid_request(self, client):
        """Test calling elevator with valid request."""
        response = client.post("/call", json={
            "floor": 3,
            "direction": "up"
        })
        assert response.status_code == 200
        data = response.json()
        assert "Elevator called to floor 3" in data["message"]
    
    def test_call_elevator_invalid_direction(self, client):
        """Test calling elevator with invalid direction."""
        response = client.post("/call", json={
            "floor": 3,
            "direction": "invalid"
        })
        assert response.status_code == 400
    
    def test_call_elevator_invalid_floor(self, client):
        """Test calling elevator to invalid floor."""
        response = client.post("/call", json={
            "floor": 0,
            "direction": "up"
        })
        assert response.status_code == 400
    
    def test_select_floor_valid_request(self, client):
        """Test selecting valid floor."""
        response = client.post("/select", json={
            "floor": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert "Floor 2 selected" in data["message"]
    
    def test_select_floor_invalid_request(self, client):
        """Test selecting invalid floor."""
        response = client.post("/select", json={
            "floor": 5
        })
        assert response.status_code == 400
    
    def test_missing_request_body(self, client):
        """Test endpoints with missing request body."""
        response = client.post("/call")
        assert response.status_code == 422  # Validation error
        
        response = client.post("/select")
        assert response.status_code == 422  # Validation error