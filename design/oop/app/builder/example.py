"""Example usage of the Builder pattern for Computer construction."""

import logging
from typing import Any

from .builder import ComputerBuilder, GamingComputerBuilder, WorkstationBuilder
from .computer import Computer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_basic_builder() -> None:
    """Demonstrate basic ComputerBuilder usage."""
    logger.info("=== Basic Builder Pattern Demo ===")
    
    builder = ComputerBuilder()
    
    try:
        # Build a custom computer with fluent interface
        computer = (builder
                   .with_name("Custom Gaming PC")
                   .with_cpu("AMD Ryzen 7 7700X", 8, 4.5, "AM5", 105)
                   .with_motherboard("MSI MAG B650 TOMAHAWK", "AM5", "DDR5", 128, 2)
                   .with_ram(32, 5600, "DDR5", 2)
                   .with_gpu("RTX 4070 Ti", 12, 285, "PCIe 4.0 x16")
                   .with_power_supply("EVGA SuperNOVA 750 G6", 750, "80+ Gold", True)
                   .build())
        
        logger.info("Successfully built computer:")
        logger.info(computer.get_summary())
        
    except ValueError as e:
        logger.error(f"Failed to build computer: {e}")


def demonstrate_preset_builders() -> None:
    """Demonstrate preset builders for specific use cases."""
    logger.info("\n=== Preset Builders Demo ===")
    
    # Gaming computer presets
    gaming_builder = GamingComputerBuilder()
    
    logger.info("Budget Gaming PC:")
    budget_pc = gaming_builder.budget_gaming().build()
    logger.info(budget_pc.get_summary())
    
    logger.info("\nHigh-End Gaming PC:")
    gaming_builder.reset()  # Reset builder state
    high_end_pc = gaming_builder.high_end_gaming().build()
    logger.info(high_end_pc.get_summary())
    
    # Workstation presets
    workstation_builder = WorkstationBuilder()
    
    logger.info("\nDevelopment Workstation:")
    dev_workstation = workstation_builder.development_workstation().build()
    logger.info(dev_workstation.get_summary())


def demonstrate_validation() -> None:
    """Demonstrate validation features."""
    logger.info("\n=== Validation Demo ===")
    
    builder = ComputerBuilder()
    
    # Test 1: Missing required components
    logger.info("Test 1: Missing required components")
    try:
        incomplete_pc = builder.with_cpu("Intel i5", 6, 3.0, "LGA1700", 65).build()
    except ValueError as e:
        logger.info(f"✓ Caught expected error: {e}")
    
    # Test 2: Incompatible socket types
    logger.info("Test 2: Incompatible CPU and motherboard sockets")
    try:
        builder.reset()
        incompatible_pc = (builder
                          .with_cpu("AMD Ryzen 5 7600X", 6, 4.7, "AM5", 105)  # AM5 socket
                          .with_motherboard("Intel Z690", "LGA1700", "DDR4", 128, 2)  # LGA1700 socket
                          .with_ram(16, 3200, "DDR4", 2)
                          .with_power_supply("Corsair 650W", 650, "80+ Bronze")
                          .build())
    except ValueError as e:
        logger.info(f"✓ Caught expected error: {e}")
    
    # Test 3: Incompatible RAM type
    logger.info("Test 3: Incompatible RAM type")
    try:
        builder.reset()
        incompatible_ram = (builder
                           .with_cpu("Intel i7-12700K", 12, 3.6, "LGA1700", 125)
                           .with_motherboard("DDR5 Motherboard", "LGA1700", "DDR5", 128, 2)
                           .with_ram(32, 3200, "DDR4", 2)  # DDR4 instead of DDR5
                           .with_power_supply("Corsair 750W", 750, "80+ Gold")
                           .build())
    except ValueError as e:
        logger.info(f"✓ Caught expected error: {e}")
    
    # Test 4: Insufficient power supply
    logger.info("Test 4: Insufficient power supply")
    try:
        builder.reset()
        underpowered = (builder
                       .with_cpu("Intel i9-13900K", 24, 3.0, "LGA1700", 125)
                       .with_motherboard("Intel Z790", "LGA1700", "DDR5", 128, 4)
                       .with_ram(32, 5600, "DDR5", 2)
                       .with_gpu("RTX 4090", 24, 450, "PCIe 4.0 x16")
                       .with_power_supply("Weak PSU", 400, "80+ Bronze")  # Too weak
                       .build())
    except ValueError as e:
        logger.info(f"✓ Caught expected error: {e}")


def demonstrate_configuration_tracking() -> None:
    """Demonstrate configuration tracking during build."""
    logger.info("\n=== Configuration Tracking Demo ===")
    
    builder = ComputerBuilder()
    
    logger.info("Initial configuration:")
    logger.info(builder.get_current_configuration())
    
    builder.with_cpu("Intel i7-13700K", 16, 3.4, "LGA1700", 125)
    logger.info("After adding CPU:")
    logger.info(builder.get_current_configuration())
    
    builder.with_motherboard("ASUS Z790", "LGA1700", "DDR5", 128, 3)
    logger.info("After adding motherboard:")
    logger.info(builder.get_current_configuration())
    
    builder.with_ram(32, 5600, "DDR5", 2)
    logger.info("After adding RAM:")
    logger.info(builder.get_current_configuration())


def main() -> None:
    """Run all demonstration examples."""
    demonstrate_basic_builder()
    demonstrate_preset_builders()
    demonstrate_validation()
    demonstrate_configuration_tracking()


if __name__ == "__main__":
    main()