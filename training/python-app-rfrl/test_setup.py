#!/usr/bin/env python3
"""Test script to verify the RF jamming detection project setup."""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
        
        import gymnasium as gym
        print(f"✓ Gymnasium {gym.__version__}")
        
        import stable_baselines3
        print(f"✓ Stable Baselines3 {stable_baselines3.__version__}")
        
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        
        import matplotlib
        print(f"✓ Matplotlib {matplotlib.__version__}")
        
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
        
        # Test RFRL Gym
        import rfrl_gym
        print("✓ RFRL Gym imported successfully")
        
        # Test creating an environment
        env = gym.make('RFRLGym-v0')
        print("✓ RFRL Gym environment created successfully")
        env.close()
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_project_structure():
    """Test that the project structure is correctly set up."""
    expected_dirs = [
        'app',
        'app/api',
        'app/core', 
        'app/models',
        'app/scenarios',
        'app/training',
        'app/utils',
        'rfrl-gym'
    ]
    
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            print(f"✗ Missing directory: {dir_path}")
            return False
        print(f"✓ Directory exists: {dir_path}")
    
    return True

def main():
    """Run all setup tests."""
    print("Testing RF Jamming Detection RL Project Setup")
    print("=" * 50)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing project structure...")
    structure_ok = test_project_structure()
    
    print("\n" + "=" * 50)
    if imports_ok and structure_ok:
        print("✓ All tests passed! Project setup is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())