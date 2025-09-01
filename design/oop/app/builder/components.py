"""Computer components for the Builder pattern."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CPU:
    """Represents a CPU component."""
    
    model: str
    cores: int
    frequency: float  # GHz
    socket: str  # e.g., "LGA1700", "AM4"
    tdp: int  # Thermal Design Power in watts
    
    def __post_init__(self) -> None:
        """Validate CPU parameters."""
        if self.cores <= 0:
            raise ValueError("CPU cores must be positive")
        if self.frequency <= 0:
            raise ValueError("CPU frequency must be positive")
        if self.tdp <= 0:
            raise ValueError("CPU TDP must be positive")


@dataclass
class RAM:
    """Represents a RAM component."""
    
    capacity: int  # GB
    speed: int  # MHz (e.g., 3200 for DDR4-3200)
    type: str  # e.g., "DDR4", "DDR5"
    modules: int  # Number of memory modules
    
    def __post_init__(self) -> None:
        """Validate RAM parameters."""
        if self.capacity <= 0:
            raise ValueError("RAM capacity must be positive")
        if self.speed <= 0:
            raise ValueError("RAM speed must be positive")
        if self.modules <= 0:
            raise ValueError("Number of RAM modules must be positive")


@dataclass
class GPU:
    """Represents a GPU component."""
    
    model: str
    vram: int  # GB
    power_consumption: int  # Watts
    interface: str  # e.g., "PCIe 4.0 x16"
    
    def __post_init__(self) -> None:
        """Validate GPU parameters."""
        if self.vram <= 0:
            raise ValueError("GPU VRAM must be positive")
        if self.power_consumption <= 0:
            raise ValueError("GPU power consumption must be positive")


@dataclass
class Motherboard:
    """Represents a motherboard component."""
    
    model: str
    socket: str  # Must match CPU socket
    ram_type: str  # Must match RAM type
    max_ram: int  # Maximum RAM capacity in GB
    pcie_slots: int  # Number of PCIe slots
    
    def __post_init__(self) -> None:
        """Validate motherboard parameters."""
        if self.max_ram <= 0:
            raise ValueError("Maximum RAM capacity must be positive")
        if self.pcie_slots < 0:
            raise ValueError("PCIe slots cannot be negative")


@dataclass
class PowerSupply:
    """Represents a power supply component."""
    
    model: str
    wattage: int  # Maximum power output in watts
    efficiency: str  # e.g., "80+ Gold"
    modular: bool  # Whether cables are modular
    
    def __post_init__(self) -> None:
        """Validate power supply parameters."""
        if self.wattage <= 0:
            raise ValueError("Power supply wattage must be positive")