"""
Script to fix PennyLane compatibility issues.

This script provides step-by-step instructions and automated fixes
for the autoray.NumpyMimic compatibility issue.
"""

import subprocess
import sys
import importlib


def run_command(command):
    """Run shell command and return success status."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Command: {command}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False


def test_pennylane_import():
    """Test if PennyLane can be imported successfully."""
    try:
        import pennylane as qml
        print("✅ PennyLane import successful!")
        print(f"PennyLane version: {qml.__version__}")
        return True
    except Exception as e:
        print(f"❌ PennyLane import failed: {e}")
        return False


def fix_numpy_version():
    """Fix by downgrading NumPy to 1.x series."""
    print("=== Fixing PennyLane Compatibility (NumPy Downgrade) ===")
    
    commands = [
        "poetry remove numpy",
        "poetry add 'numpy>=1.24.0,<2.0.0'",
        "poetry lock --no-update",
        "poetry install"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd):
            print(f"❌ Failed: {cmd}")
            return False
    
    return test_pennylane_import()


def fix_pennylane_version():
    """Fix by updating PennyLane to latest compatible version."""
    print("=== Fixing PennyLane Compatibility (PennyLane Update) ===")
    
    commands = [
        "poetry add 'pennylane>=0.36.0'",
        "poetry lock --no-update", 
        "poetry install"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd):
            print(f"❌ Failed: {cmd}")
            return False
    
    return test_pennylane_import()


def fix_autoray_version():
    """Fix by pinning autoray to compatible version."""
    print("=== Fixing PennyLane Compatibility (Autoray Pin) ===")
    
    commands = [
        "poetry add 'autoray>=0.6.11,<0.7.0'",
        "poetry lock --no-update",
        "poetry install"
    ]
    
    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        if not run_command(cmd):
            print(f"❌ Failed: {cmd}")
            return False
    
    return test_pennylane_import()


def main():
    """Main fix function with multiple strategies."""
    print("PennyLane Compatibility Fix Tool")
    print("=" * 50)
    
    # Test current state
    print("Testing current PennyLane import...")
    if test_pennylane_import():
        print("✅ PennyLane is already working! No fix needed.")
        return
    
    # Try different fix strategies
    strategies = [
        ("NumPy Downgrade (Most Reliable)", fix_numpy_version),
        ("Autoray Version Pin", fix_autoray_version),
        ("PennyLane Update", fix_pennylane_version)
    ]
    
    for strategy_name, fix_function in strategies:
        print(f"\n{'='*50}")
        print(f"Trying Strategy: {strategy_name}")
        print('='*50)
        
        if fix_function():
            print(f"✅ SUCCESS: {strategy_name} worked!")
            print("\nPennyLane is now compatible. You can use:")
            print("- poetry run python spectral_qnn/core/qnn_pennylane.py")
            print("- poetry run python -m pytest tests/test_qnn_basic.py")
            return
        else:
            print(f"❌ FAILED: {strategy_name} didn't work.")
    
    print("\n" + "="*50)
    print("❌ All automatic fixes failed.")
    print("Manual resolution required:")
    print("1. Check Poetry documentation: https://python-poetry.org/docs/")
    print("2. Create fresh environment: poetry env remove --all && poetry install")
    print("3. Use conda instead: conda create -n qnn-env python=3.11")
    print("4. Contact PennyLane support: https://github.com/PennyLaneAI/pennylane/issues")


if __name__ == "__main__":
    main()