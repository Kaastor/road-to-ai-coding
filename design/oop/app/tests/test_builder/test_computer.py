"""Tests for the Computer class."""

import pytest

from app.builder.computer import Computer
from app.builder.components import CPU, RAM, GPU, Motherboard, PowerSupply


class TestComputer:
    """Test Computer class."""
    
    @pytest.fixture
    def valid_components(self):
        """Fixture providing valid components for testing."""
        return {
            'cpu': CPU("Intel i7-13700K", 16, 3.4, "LGA1700", 125),
            'motherboard': Motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3),
            'ram': RAM(32, 5600, "DDR5", 2),
            'gpu': GPU("RTX 4080", 16, 320, "PCIe 4.0 x16"),
            'power_supply': PowerSupply("Corsair RM850x", 850, "80+ Gold", True)
        }
    
    def test_valid_computer_creation(self, valid_components):
        """Test creating a valid computer."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply'],
            gpu=valid_components['gpu'],
            name="Test PC"
        )
        
        assert computer.cpu == valid_components['cpu']
        assert computer.motherboard == valid_components['motherboard']
        assert computer.ram == valid_components['ram']
        assert computer.gpu == valid_components['gpu']
        assert computer.power_supply == valid_components['power_supply']
        assert computer.name == "Test PC"
    
    def test_computer_without_gpu(self, valid_components):
        """Test creating a computer without GPU."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply']
        )
        
        assert computer.gpu is None
    
    def test_socket_incompatibility(self, valid_components):
        """Test socket incompatibility validation."""
        # Create CPU with different socket
        amd_cpu = CPU("AMD Ryzen 7 7700X", 8, 4.5, "AM5", 105)
        
        with pytest.raises(ValueError, match="CPU socket AM5 incompatible with motherboard socket LGA1700"):
            Computer(
                cpu=amd_cpu,
                motherboard=valid_components['motherboard'],
                ram=valid_components['ram'],
                power_supply=valid_components['power_supply']
            )
    
    def test_ram_type_incompatibility(self, valid_components):
        """Test RAM type incompatibility validation."""
        # Create DDR4 RAM for DDR5 motherboard
        ddr4_ram = RAM(16, 3200, "DDR4", 2)
        
        with pytest.raises(ValueError, match="RAM type DDR4 incompatible with motherboard RAM type DDR5"):
            Computer(
                cpu=valid_components['cpu'],
                motherboard=valid_components['motherboard'],
                ram=ddr4_ram,
                power_supply=valid_components['power_supply']
            )
    
    def test_ram_capacity_exceeds_motherboard_limit(self, valid_components):
        """Test RAM capacity exceeding motherboard limit."""
        # Create motherboard with low max RAM
        limited_mb = Motherboard("Budget Board", "LGA1700", "DDR5", 16, 2)
        
        with pytest.raises(ValueError, match="RAM capacity 32GB exceeds motherboard maximum 16GB"):
            Computer(
                cpu=valid_components['cpu'],
                motherboard=limited_mb,
                ram=valid_components['ram'],
                power_supply=valid_components['power_supply']
            )
    
    def test_insufficient_power_supply(self, valid_components):
        """Test insufficient power supply validation."""
        # Create weak power supply
        weak_psu = PowerSupply("Weak PSU", 300, "80+ Bronze", False)
        
        with pytest.raises(ValueError, match="Power supply 300W insufficient for system requiring"):
            Computer(
                cpu=valid_components['cpu'],
                motherboard=valid_components['motherboard'],
                ram=valid_components['ram'],
                power_supply=weak_psu,
                gpu=valid_components['gpu']
            )
    
    def test_power_calculation_without_gpu(self, valid_components):
        """Test power calculation without GPU."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply']
        )
        
        assert computer.get_total_power_consumption() == 125  # CPU TDP only
    
    def test_power_calculation_with_gpu(self, valid_components):
        """Test power calculation with GPU."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply'],
            gpu=valid_components['gpu']
        )
        
        assert computer.get_total_power_consumption() == 445  # CPU TDP + GPU power
    
    def test_get_summary_with_name(self, valid_components):
        """Test getting computer summary with name."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply'],
            gpu=valid_components['gpu'],
            name="Gaming Rig"
        )
        
        summary = computer.get_summary()
        
        assert "Computer: Gaming Rig" in summary
        assert "CPU: Intel i7-13700K (16 cores, 3.4GHz)" in summary
        assert "Motherboard: ASUS Z790" in summary
        assert "RAM: 32GB DDR5-5600 (2 modules)" in summary
        assert "GPU: RTX 4080 (16GB VRAM)" in summary
        assert "Power Supply: Corsair RM850x (850W)" in summary
        assert "Estimated Power: 445W" in summary
    
    def test_get_summary_without_name_and_gpu(self, valid_components):
        """Test getting computer summary without name and GPU."""
        computer = Computer(
            cpu=valid_components['cpu'],
            motherboard=valid_components['motherboard'],
            ram=valid_components['ram'],
            power_supply=valid_components['power_supply']
        )
        
        summary = computer.get_summary()
        
        assert "Computer:" not in summary  # No name line
        assert "GPU:" not in summary  # No GPU line
        assert "CPU: Intel i7-13700K (16 cores, 3.4GHz)" in summary
        assert "Estimated Power: 125W" in summary