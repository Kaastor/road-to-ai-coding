"""Tests for the ComputerBuilder classes."""

import pytest

from app.builder.builder import ComputerBuilder, GamingComputerBuilder, WorkstationBuilder
from app.builder.computer import Computer


class TestComputerBuilder:
    """Test ComputerBuilder class."""
    
    @pytest.fixture
    def builder(self):
        """Fixture providing a fresh ComputerBuilder instance."""
        return ComputerBuilder()
    
    def test_fluent_interface(self, builder):
        """Test fluent interface returns self for chaining."""
        result = builder.with_name("Test PC")
        assert result is builder
        
        result = builder.with_cpu("Intel i7", 8, 3.4, "LGA1700", 125)
        assert result is builder
    
    def test_complete_build(self, builder):
        """Test building a complete computer."""
        computer = (builder
                   .with_name("Test PC")
                   .with_cpu("Intel i7-13700K", 16, 3.4, "LGA1700", 125)
                   .with_motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3)
                   .with_ram(32, 5600, "DDR5", 2)
                   .with_gpu("RTX 4080", 16, 320, "PCIe 4.0 x16")
                   .with_power_supply("Corsair RM850x", 850, "80+ Gold", True)
                   .build())
        
        assert isinstance(computer, Computer)
        assert computer.name == "Test PC"
        assert computer.cpu.model == "Intel i7-13700K"
        assert computer.motherboard.model == "ASUS Z790"
        assert computer.ram.capacity == 32
        assert computer.gpu.model == "RTX 4080"
        assert computer.power_supply.model == "Corsair RM850x"
    
    def test_build_without_gpu(self, builder):
        """Test building a computer without GPU."""
        computer = (builder
                   .with_cpu("Intel i5-12400", 6, 2.5, "LGA1700", 65)
                   .with_motherboard("MSI B660", "LGA1700", "DDR4", 128, 2)
                   .with_ram(16, 3200, "DDR4", 2)
                   .with_power_supply("Corsair CV550", 550, "80+ Bronze", False)
                   .build())
        
        assert computer.gpu is None
    
    def test_missing_cpu(self, builder):
        """Test building without CPU raises error."""
        with pytest.raises(ValueError, match="Missing required components: CPU"):
            builder.with_motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3).build()
    
    def test_missing_multiple_components(self, builder):
        """Test building with multiple missing components."""
        with pytest.raises(ValueError, match="Missing required components"):
            builder.with_cpu("Intel i7", 8, 3.4, "LGA1700", 125).build()
    
    def test_reset_builder(self, builder):
        """Test resetting builder state."""
        builder.with_name("Test PC").with_cpu("Intel i7", 8, 3.4, "LGA1700", 125)
        
        config_before = builder.get_current_configuration()
        assert config_before["name"] == "Test PC"
        assert config_before["cpu"] == "Intel i7"
        
        builder.reset()
        
        config_after = builder.get_current_configuration()
        assert all(value is None for value in config_after.values())
    
    def test_configuration_tracking(self, builder):
        """Test configuration tracking during build."""
        initial_config = builder.get_current_configuration()
        assert all(value is None for value in initial_config.values())
        
        builder.with_cpu("Intel i7-13700K", 16, 3.4, "LGA1700", 125)
        config = builder.get_current_configuration()
        assert config["cpu"] == "Intel i7-13700K"
        assert config["motherboard"] is None
        
        builder.with_motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3)
        config = builder.get_current_configuration()
        assert config["motherboard"] == "ASUS Z790"
        
        builder.with_ram(32, 5600, "DDR5", 2)
        config = builder.get_current_configuration()
        assert config["ram"] == "32GB DDR5"
        
        builder.with_power_supply("Corsair RM850x", 850, "80+ Gold", True)
        config = builder.get_current_configuration()
        assert config["power_supply"] == "Corsair RM850x (850W)"
    
    def test_incompatible_components_validation(self, builder):
        """Test that incompatible components are caught during build."""
        with pytest.raises(ValueError, match="CPU socket AM5 incompatible"):
            (builder
             .with_cpu("AMD Ryzen 7", 8, 4.5, "AM5", 105)  # AM5 socket
             .with_motherboard("Intel Z790", "LGA1700", "DDR5", 128, 3)  # LGA1700 socket
             .with_ram(32, 5600, "DDR5", 2)
             .with_power_supply("Corsair RM750x", 750, "80+ Gold", True)
             .build())


class TestGamingComputerBuilder:
    """Test GamingComputerBuilder class."""
    
    @pytest.fixture
    def gaming_builder(self):
        """Fixture providing a GamingComputerBuilder instance."""
        return GamingComputerBuilder()
    
    def test_budget_gaming_preset(self, gaming_builder):
        """Test budget gaming preset configuration."""
        computer = gaming_builder.budget_gaming().build()
        
        assert computer.name == "Budget Gaming PC"
        assert computer.cpu.model == "Intel Core i5-12400F"
        assert computer.ram.capacity == 16
        assert computer.gpu.model == "RTX 3060"
        assert computer.power_supply.wattage == 650
    
    def test_high_end_gaming_preset(self, gaming_builder):
        """Test high-end gaming preset configuration."""
        computer = gaming_builder.high_end_gaming().build()
        
        assert computer.name == "High-End Gaming PC"
        assert computer.cpu.model == "Intel Core i7-13700K"
        assert computer.ram.capacity == 32
        assert computer.ram.type == "DDR5"
        assert computer.gpu.model == "RTX 4080"
        assert computer.power_supply.wattage == 850
    
    def test_builder_reuse_after_reset(self, gaming_builder):
        """Test reusing builder after reset."""
        # Build budget gaming PC
        budget_pc = gaming_builder.budget_gaming().build()
        assert budget_pc.name == "Budget Gaming PC"
        
        # Reset and build high-end PC
        gaming_builder.reset()
        high_end_pc = gaming_builder.high_end_gaming().build()
        assert high_end_pc.name == "High-End Gaming PC"
        assert high_end_pc.cpu.model != budget_pc.cpu.model


class TestWorkstationBuilder:
    """Test WorkstationBuilder class."""
    
    @pytest.fixture
    def workstation_builder(self):
        """Fixture providing a WorkstationBuilder instance."""
        return WorkstationBuilder()
    
    def test_development_workstation_preset(self, workstation_builder):
        """Test development workstation preset configuration."""
        computer = workstation_builder.development_workstation().build()
        
        assert computer.name == "Development Workstation"
        assert computer.cpu.model == "Intel Core i9-13900K"
        assert computer.cpu.cores == 24
        assert computer.ram.capacity == 64
        assert computer.gpu.model == "RTX 4070"
    
    def test_content_creation_preset(self, workstation_builder):
        """Test content creation workstation preset configuration."""
        computer = workstation_builder.content_creation().build()
        
        assert computer.name == "Content Creation Workstation"
        assert computer.cpu.model == "AMD Ryzen 9 7950X"
        assert computer.cpu.socket == "AM5"
        assert computer.ram.capacity == 128
        assert computer.gpu.model == "RTX 4090"
        assert computer.power_supply.wattage == 1000
    
    def test_workstation_power_requirements(self, workstation_builder):
        """Test that workstation configurations meet power requirements."""
        # Content creation workstation has high-power components
        computer = workstation_builder.content_creation().build()
        
        # Should not raise validation error for insufficient power
        assert computer.cpu.tdp == 170
        assert computer.gpu.power_consumption == 450
        assert computer.power_supply.wattage == 1000
        
        # Verify power calculation
        total_power = computer.get_total_power_consumption()
        required_power = int(total_power * 1.2)  # 20% headroom
        assert computer.power_supply.wattage >= required_power


class TestBuilderValidation:
    """Test builder validation scenarios."""
    
    def test_component_validation_in_builder(self):
        """Test that component validation works through builder."""
        builder = ComputerBuilder()
        
        # This should raise validation error for CPU with 0 cores
        with pytest.raises(ValueError, match="CPU cores must be positive"):
            builder.with_cpu("Invalid CPU", 0, 3.0, "LGA1700", 125)
    
    def test_ram_default_modules(self):
        """Test RAM with default number of modules."""
        builder = ComputerBuilder()
        
        computer = (builder
                   .with_cpu("Intel i5", 6, 3.0, "LGA1700", 65)
                   .with_motherboard("MSI B660", "LGA1700", "DDR4", 128, 2)
                   .with_ram(16, 3200, "DDR4")  # No modules specified, should default to 1
                   .with_power_supply("Corsair CV550", 550, "80+ Bronze")
                   .build())
        
        assert computer.ram.modules == 1
    
    def test_power_supply_default_modular(self):
        """Test power supply with default modular setting."""
        builder = ComputerBuilder()
        
        computer = (builder
                   .with_cpu("Intel i5", 6, 3.0, "LGA1700", 65)
                   .with_motherboard("MSI B660", "LGA1700", "DDR4", 128, 2)
                   .with_ram(16, 3200, "DDR4", 2)
                   .with_power_supply("Basic PSU", 550, "80+ Bronze")  # No modular specified
                   .build())
        
        assert computer.power_supply.modular is False