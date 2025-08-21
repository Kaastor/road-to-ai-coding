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
    assert isinstance(result, (float, np.floating))
    assert -1 <= result <= 1  # Expectation value bounds
    
    # Test with different input
    result2 = qnn.forward(np.pi)
    assert isinstance(result2, (float, np.floating))


def test_qnn_different_inputs():
    """Test QNN produces different outputs for different inputs."""
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=1)
    
    result1 = qnn.forward(0.0)
    result2 = qnn.forward(1.0)
    
    # Should produce different outputs (with high probability)
    # Note: This could theoretically fail due to quantum nature, but very unlikely
    assert abs(result1 - result2) > 1e-6


if __name__ == "__main__":
    # Run basic tests
    test_qnn_initialization()
    test_qnn_forward_pass()
    test_qnn_different_inputs()
    print("All basic QNN tests passed!")