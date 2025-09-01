"""ComputerBuilder implementation with fluent interface."""

from typing import Optional, Self

from .computer import Computer
from .components import CPU, RAM, GPU, Motherboard, PowerSupply


class ComputerBuilder:
    """Builder for constructing Computer objects with fluent interface."""
    
    def __init__(self) -> None:
        """Initialize the builder with empty configuration."""
        self._cpu: Optional[CPU] = None
        self._motherboard: Optional[Motherboard] = None
        self._ram: Optional[RAM] = None
        self._gpu: Optional[GPU] = None
        self._power_supply: Optional[PowerSupply] = None
        self._name: Optional[str] = None
    
    def with_cpu(
        self, 
        model: str, 
        cores: int, 
        frequency: float, 
        socket: str, 
        tdp: int
    ) -> Self:
        """Add CPU component to the build."""
        self._cpu = CPU(model=model, cores=cores, frequency=frequency, socket=socket, tdp=tdp)
        return self
    
    def with_motherboard(
        self, 
        model: str, 
        socket: str, 
        ram_type: str, 
        max_ram: int, 
        pcie_slots: int
    ) -> Self:
        """Add motherboard component to the build."""
        self._motherboard = Motherboard(
            model=model, 
            socket=socket, 
            ram_type=ram_type, 
            max_ram=max_ram, 
            pcie_slots=pcie_slots
        )
        return self
    
    def with_ram(self, capacity: int, speed: int, type: str, modules: int = 1) -> Self:
        """Add RAM component to the build."""
        self._ram = RAM(capacity=capacity, speed=speed, type=type, modules=modules)
        return self
    
    def with_gpu(self, model: str, vram: int, power_consumption: int, interface: str) -> Self:
        """Add GPU component to the build."""
        self._gpu = GPU(
            model=model, 
            vram=vram, 
            power_consumption=power_consumption, 
            interface=interface
        )
        return self
    
    def with_power_supply(
        self, 
        model: str, 
        wattage: int, 
        efficiency: str, 
        modular: bool = False
    ) -> Self:
        """Add power supply component to the build."""
        self._power_supply = PowerSupply(
            model=model, 
            wattage=wattage, 
            efficiency=efficiency, 
            modular=modular
        )
        return self
    
    def with_name(self, name: str) -> Self:
        """Set the computer name."""
        self._name = name
        return self
    
    def build(self) -> Computer:
        """Build and return the final Computer object."""
        self._validate_required_components()
        
        return Computer(
            cpu=self._cpu,
            motherboard=self._motherboard,
            ram=self._ram,
            power_supply=self._power_supply,
            gpu=self._gpu,
            name=self._name
        )
    
    def _validate_required_components(self) -> None:
        """Validate that all required components are present."""
        required_components = {
            "CPU": self._cpu,
            "Motherboard": self._motherboard,
            "RAM": self._ram,
            "Power Supply": self._power_supply
        }
        
        missing = [name for name, component in required_components.items() if component is None]
        
        if missing:
            raise ValueError(f"Missing required components: {', '.join(missing)}")
    
    def reset(self) -> Self:
        """Reset the builder to empty state."""
        self._cpu = None
        self._motherboard = None
        self._ram = None
        self._gpu = None
        self._power_supply = None
        self._name = None
        return self
    
    def get_current_configuration(self) -> dict[str, Optional[str]]:
        """Get the current build configuration as a dictionary."""
        return {
            "cpu": self._cpu.model if self._cpu else None,
            "motherboard": self._motherboard.model if self._motherboard else None,
            "ram": f"{self._ram.capacity}GB {self._ram.type}" if self._ram else None,
            "gpu": self._gpu.model if self._gpu else None,
            "power_supply": f"{self._power_supply.model} ({self._power_supply.wattage}W)" if self._power_supply else None,
            "name": self._name
        }


class GamingComputerBuilder(ComputerBuilder):
    """Specialized builder for gaming computers with preset configurations."""
    
    def budget_gaming(self) -> Self:
        """Configure a budget gaming computer."""
        return (self
                .with_cpu("Intel Core i5-12400F", 6, 2.5, "LGA1700", 65)
                .with_motherboard("MSI B660M PRO-VDH", "LGA1700", "DDR4", 128, 2)
                .with_ram(16, 3200, "DDR4", 2)
                .with_gpu("RTX 3060", 12, 170, "PCIe 4.0 x16")
                .with_power_supply("Corsair CV650", 650, "80+ Bronze", False)
                .with_name("Budget Gaming PC"))
    
    def high_end_gaming(self) -> Self:
        """Configure a high-end gaming computer."""
        return (self
                .with_cpu("Intel Core i7-13700K", 16, 3.4, "LGA1700", 125)
                .with_motherboard("ASUS ROG Strix Z790-E", "LGA1700", "DDR5", 128, 4)
                .with_ram(32, 5600, "DDR5", 2)
                .with_gpu("RTX 4080", 16, 320, "PCIe 4.0 x16")
                .with_power_supply("Corsair RM850x", 850, "80+ Gold", True)
                .with_name("High-End Gaming PC"))


class WorkstationBuilder(ComputerBuilder):
    """Specialized builder for workstation computers."""
    
    def development_workstation(self) -> Self:
        """Configure a development workstation."""
        return (self
                .with_cpu("Intel Core i9-13900K", 24, 3.0, "LGA1700", 125)
                .with_motherboard("ASUS ProArt Z790-CREATOR", "LGA1700", "DDR5", 128, 4)
                .with_ram(64, 5600, "DDR5", 4)
                .with_gpu("RTX 4070", 12, 200, "PCIe 4.0 x16")
                .with_power_supply("Seasonic Focus GX-750", 750, "80+ Gold", True)
                .with_name("Development Workstation"))
    
    def content_creation(self) -> Self:
        """Configure a content creation workstation."""
        return (self
                .with_cpu("AMD Ryzen 9 7950X", 16, 4.5, "AM5", 170)
                .with_motherboard("ASUS ROG Crosshair X670E Hero", "AM5", "DDR5", 128, 4)
                .with_ram(128, 5600, "DDR5", 4)
                .with_gpu("RTX 4090", 24, 450, "PCIe 4.0 x16")
                .with_power_supply("Corsair AX1000", 1000, "80+ Titanium", True)
                .with_name("Content Creation Workstation"))