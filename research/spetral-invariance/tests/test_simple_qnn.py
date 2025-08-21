"""
Tests for simplified QNN implementation.
"""

import numpy as np
from spectral_qnn.core.simple_qnn import SimpleQuantumNeuralNetwork


def test_simple_qnn_initialization():
    """Test simplified QNN initialization."""
    qnn = SimpleQuantumNeuralNetwork(n_qubits=2, n_layers=3)
    
    assert qnn.n_qubits == 2
    assert qnn.n_layers == 3
    assert qnn.get_shape() == (2, 3)
    assert len(qnn.generators) == 3  # n_layers
    assert len(qnn.generators[0]) == 2  # n_qubits


def test_hamming_encoding_spectrum():
    """Test Hamming encoding spectrum calculation."""
    qnn = SimpleQuantumNeuralNetwork(n_qubits=2, n_layers=1)
    spectrum = qnn.compute_hamming_encoding_spectrum()
    
    # For R=2, L=1, Pauli-Z: should be 2 * Z_2 = 2 * {-2, 0, 2} = {-4, -2, 0, 2, 4}
    expected = np.array([-4, -2, 0, 2, 4])
    assert np.array_equal(spectrum, expected)


def test_spectral_invariance():
    """Test spectral invariance under area-preserving transformations."""
    # Same area A = 4
    qnn1 = SimpleQuantumNeuralNetwork(n_qubits=2, n_layers=2)
    qnn2 = SimpleQuantumNeuralNetwork(n_qubits=4, n_layers=1) 
    qnn3 = SimpleQuantumNeuralNetwork(n_qubits=1, n_layers=4)
    
    # All should have same frequency spectrum
    assert qnn1.demonstrate_spectral_invariance(qnn2)
    assert qnn1.demonstrate_spectral_invariance(qnn3)
    assert qnn2.demonstrate_spectral_invariance(qnn3)
    
    # Different area should not be invariant
    qnn4 = SimpleQuantumNeuralNetwork(n_qubits=3, n_layers=2)  # Area = 6
    assert not qnn1.demonstrate_spectral_invariance(qnn4)


if __name__ == "__main__":
    # Run tests manually
    test_simple_qnn_initialization()
    print("✓ Initialization test passed")
    
    test_hamming_encoding_spectrum()
    print("✓ Hamming encoding test passed")
    
    test_spectral_invariance()
    print("✓ Spectral invariance test passed")
    
    print("\nAll simplified QNN tests passed!")