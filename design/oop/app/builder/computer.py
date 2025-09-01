"""Computer class for the Builder pattern."""

from dataclasses import dataclass
from typing import Optional

from .components import CPU, RAM, GPU, Motherboard, PowerSupply


@dataclass
class Computer:
    """Represents a complete computer configuration."""
    
    cpu: CPU
    motherboard: Motherboard
    ram: RAM
    power_supply: PowerSupply
    gpu: Optional[GPU] = None
    name: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate the complete computer configuration."""
        self._validate_compatibility()
    
    def _validate_compatibility(self) -> None:
        """Validate component compatibility."""
        # CPU and motherboard socket compatibility
        if self.cpu.socket != self.motherboard.socket:
            raise ValueError(
                f"CPU socket {self.cpu.socket} incompatible with "
                f"motherboard socket {self.motherboard.socket}"
            )
        
        # RAM and motherboard compatibility
        if self.ram.type != self.motherboard.ram_type:
            raise ValueError(
                f"RAM type {self.ram.type} incompatible with "
                f"motherboard RAM type {self.motherboard.ram_type}"
            )
        
        # RAM capacity check
        if self.ram.capacity > self.motherboard.max_ram:
            raise ValueError(
                f"RAM capacity {self.ram.capacity}GB exceeds "
                f"motherboard maximum {self.motherboard.max_ram}GB"
            )
        
        # Power supply capacity check
        total_power = self.cpu.tdp
        if self.gpu:
            total_power += self.gpu.power_consumption
        
        # Add some headroom (20%) for other components and efficiency
        required_power = int(total_power * 1.2)
        if self.power_supply.wattage < required_power:
            raise ValueError(
                f"Power supply {self.power_supply.wattage}W insufficient for "
                f"system requiring ~{required_power}W"
            )
    
    def get_total_power_consumption(self) -> int:
        """Calculate estimated total power consumption."""
        total = self.cpu.tdp
        if self.gpu:
            total += self.gpu.power_consumption
        return total
    
    def get_summary(self) -> str:
        """Get a formatted summary of the computer configuration."""
        summary = []
        if self.name:
            summary.append(f"Computer: {self.name}")
        
        summary.extend([
            f"CPU: {self.cpu.model} ({self.cpu.cores} cores, {self.cpu.frequency}GHz)",
            f"Motherboard: {self.motherboard.model}",
            f"RAM: {self.ram.capacity}GB {self.ram.type}-{self.ram.speed} ({self.ram.modules} modules)",
            f"Power Supply: {self.power_supply.model} ({self.power_supply.wattage}W)",
        ])
        
        if self.gpu:
            summary.append(f"GPU: {self.gpu.model} ({self.gpu.vram}GB VRAM)")
        
        summary.append(f"Estimated Power: {self.get_total_power_consumption()}W")
        
        return "\n".join(summary)