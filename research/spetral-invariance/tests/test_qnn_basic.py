"""
Basic tests for QNN implementation.
"""

import pytest
import numpy as np
from spectral_qnn.core.qnn_pennylane import QuantumNeuralNetwork


def test_qnn_initialization():
    """Test QNN can be initialized with correct parameters."""
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=3)
    
    assert qnn.n_qubits == 2
    assert qnn.n_layers == 3
    assert qnn.get_shape() == (2, 3)
    assert len(qnn.params) == qnn.n_params


def test_qnn_forward_pass():
    """Test QNN forward pass produces valid output."""
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=1)
    
    result = qnn.forward(0.0)
    # PennyLane returns tensors, so convert to float for testing
    result_val = float(result)
    assert isinstance(result_val, float)
    assert -1 <= result_val <= 1  # Expectation value bounds
    
    # Test with different input
    result2 = qnn.forward(np.pi)
    result2_val = float(result2)
    assert isinstance(result2_val, float)


def test_qnn_different_inputs():
    """Test QNN produces different outputs for different inputs."""
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=1)
    
    result1 = qnn.forward(0.0)
    result2 = qnn.forward(1.0)
    
    # Convert to float for comparison
    result1_val = float(result1)
    result2_val = float(result2)
    
    # Should produce different outputs (with high probability)
    # Note: This could theoretically fail due to quantum nature, but very unlikely
    assert abs(result1_val - result2_val) > 1e-6


if __name__ == "__main__":
    # Run basic tests
    test_qnn_initialization()
    test_qnn_forward_pass()
    test_qnn_different_inputs()
    print("All basic QNN tests passed!")