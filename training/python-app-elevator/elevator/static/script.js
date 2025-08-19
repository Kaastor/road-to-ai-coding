class ElevatorUI {
    constructor() {
        this.elevatorCar = document.getElementById('elevator-car');
        this.statusFloor = document.getElementById('status-floor');
        this.statusState = document.getElementById('status-state');
        this.statusQueue = document.getElementById('status-queue');
        this.elevatorFloor = document.getElementById('elevator-floor');
        this.elevatorDirection = document.getElementById('elevator-direction');
        
        this.initEventHandlers();
        this.startStatusPolling();
    }
    
    initEventHandlers() {
        // Call buttons event handler (single handler for all up/down buttons)
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('call-button')) {
                const floor = parseInt(event.target.dataset.floor);
                const direction = event.target.dataset.direction;
                this.callElevator(floor, direction);
                this.highlightButton(event.target);
            }
        });
        
        // Control panel buttons event handler (single handler for all floor buttons)
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('floor-button')) {
                const floor = parseInt(event.target.dataset.floor);
                this.selectFloor(floor);
                this.highlightButton(event.target);
            }
        });
    }
    
    async callElevator(floor, direction) {
        try {
            const response = await fetch('/call', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    floor: floor,
                    direction: direction
                })
            });
            
            if (!response.ok) {
                console.error('Failed to call elevator:', response.statusText);
            }
        } catch (error) {
            console.error('Error calling elevator:', error);
        }
    }
    
    async selectFloor(floor) {
        try {
            const response = await fetch('/select', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    floor: floor
                })
            });
            
            if (!response.ok) {
                console.error('Failed to select floor:', response.statusText);
            }
        } catch (error) {
            console.error('Error selecting floor:', error);
        }
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/status');
            if (response.ok) {
                const status = await response.json();
                this.updateUI(status);
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }
    
    updateUI(status) {
        // Update status display
        this.statusFloor.textContent = status.current_floor;
        this.statusState.textContent = status.state.toUpperCase();
        this.statusQueue.textContent = JSON.stringify(status.queue);
        
        // Update elevator car display
        this.elevatorFloor.textContent = status.current_floor;
        this.elevatorDirection.textContent = status.direction.toUpperCase();
        
        // Move elevator car to correct position
        this.elevatorCar.setAttribute('data-floor', status.current_floor);
    }
    
    highlightButton(button) {
        button.classList.add('active');
        setTimeout(() => {
            button.classList.remove('active');
        }, 1000);
    }
    
    startStatusPolling() {
        // Update status every second
        setInterval(() => {
            this.updateStatus();
        }, 1000);
        
        // Initial status update
        this.updateStatus();
    }
}

// Initialize the elevator UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ElevatorUI();
});