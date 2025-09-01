"""Tests for computer components."""

import pytest

from app.builder.components import CPU, RAM, GPU, Motherboard, PowerSupply


class TestCPU:
    """Test CPU component."""
    
    def test_valid_cpu_creation(self):
        """Test creating a valid CPU."""
        cpu = CPU("Intel i7-13700K", 16, 3.4, "LGA1700", 125)
        
        assert cpu.model == "Intel i7-13700K"
        assert cpu.cores == 16
        assert cpu.frequency == 3.4
        assert cpu.socket == "LGA1700"
        assert cpu.tdp == 125
    
    def test_cpu_validation_cores(self):
        """Test CPU validation for cores."""
        with pytest.raises(ValueError, match="CPU cores must be positive"):
            CPU("Intel i7", 0, 3.4, "LGA1700", 125)
    
    def test_cpu_validation_frequency(self):
        """Test CPU validation for frequency."""
        with pytest.raises(ValueError, match="CPU frequency must be positive"):
            CPU("Intel i7", 8, 0, "LGA1700", 125)
    
    def test_cpu_validation_tdp(self):
        """Test CPU validation for TDP."""
        with pytest.raises(ValueError, match="CPU TDP must be positive"):
            CPU("Intel i7", 8, 3.4, "LGA1700", 0)


class TestRAM:
    """Test RAM component."""
    
    def test_valid_ram_creation(self):
        """Test creating valid RAM."""
        ram = RAM(32, 5600, "DDR5", 2)
        
        assert ram.capacity == 32
        assert ram.speed == 5600
        assert ram.type == "DDR5"
        assert ram.modules == 2
    
    def test_ram_validation_capacity(self):
        """Test RAM validation for capacity."""
        with pytest.raises(ValueError, match="RAM capacity must be positive"):
            RAM(0, 3200, "DDR4", 2)
    
    def test_ram_validation_speed(self):
        """Test RAM validation for speed."""
        with pytest.raises(ValueError, match="RAM speed must be positive"):
            RAM(16, 0, "DDR4", 2)
    
    def test_ram_validation_modules(self):
        """Test RAM validation for modules."""
        with pytest.raises(ValueError, match="Number of RAM modules must be positive"):
            RAM(16, 3200, "DDR4", 0)


class TestGPU:
    """Test GPU component."""
    
    def test_valid_gpu_creation(self):
        """Test creating a valid GPU."""
        gpu = GPU("RTX 4080", 16, 320, "PCIe 4.0 x16")
        
        assert gpu.model == "RTX 4080"
        assert gpu.vram == 16
        assert gpu.power_consumption == 320
        assert gpu.interface == "PCIe 4.0 x16"
    
    def test_gpu_validation_vram(self):
        """Test GPU validation for VRAM."""
        with pytest.raises(ValueError, match="GPU VRAM must be positive"):
            GPU("RTX 4080", 0, 320, "PCIe 4.0 x16")
    
    def test_gpu_validation_power(self):
        """Test GPU validation for power consumption."""
        with pytest.raises(ValueError, match="GPU power consumption must be positive"):
            GPU("RTX 4080", 16, 0, "PCIe 4.0 x16")


class TestMotherboard:
    """Test Motherboard component."""
    
    def test_valid_motherboard_creation(self):
        """Test creating a valid motherboard."""
        mb = Motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3)
        
        assert mb.model == "ASUS Z790"
        assert mb.socket == "LGA1700"
        assert mb.ram_type == "DDR5"
        assert mb.max_ram == 128
        assert mb.pcie_slots == 3
    
    def test_motherboard_validation_max_ram(self):
        """Test motherboard validation for max RAM."""
        with pytest.raises(ValueError, match="Maximum RAM capacity must be positive"):
            Motherboard("ASUS Z790", "LGA1700", "DDR5", 0, 3)
    
    def test_motherboard_validation_pcie_slots(self):
        """Test motherboard validation for PCIe slots."""
        with pytest.raises(ValueError, match="PCIe slots cannot be negative"):
            Motherboard("ASUS Z790", "LGA1700", "DDR5", 128, -1)


class TestPowerSupply:
    """Test PowerSupply component."""
    
    def test_valid_power_supply_creation(self):
        """Test creating a valid power supply."""
        psu = PowerSupply("Corsair RM750x", 750, "80+ Gold", True)
        
        assert psu.model == "Corsair RM750x"
        assert psu.wattage == 750
        assert psu.efficiency == "80+ Gold"
        assert psu.modular is True
    
    def test_power_supply_validation_wattage(self):
        """Test power supply validation for wattage."""
        with pytest.raises(ValueError, match="Power supply wattage must be positive"):
            PowerSupply("Corsair RM750x", 0, "80+ Gold", True)