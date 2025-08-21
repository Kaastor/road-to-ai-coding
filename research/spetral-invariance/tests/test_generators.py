"""
Tests for Hamiltonian generators.
"""

import numpy as np
from spectral_qnn.core.generators import HamiltonianGenerators


def test_pauli_matrices():
    """Test basic Pauli matrices."""
    # Test Pauli-Z eigenvalues
    pauli_z = HamiltonianGenerators.pauli_z()
    eigenvals = HamiltonianGenerators.get_eigenvalues(pauli_z)
    expected = np.array([-1, 1])
    assert np.allclose(eigenvals, expected)
    
    # Test scaled Pauli-Z
    scaled_z = HamiltonianGenerators.scaled_pauli_z(0.5)
    scaled_eigenvals = HamiltonianGenerators.get_eigenvalues(scaled_z)
    expected_scaled = np.array([-0.5, 0.5])
    assert np.allclose(scaled_eigenvals, expected_scaled)


def test_hamming_encoding():
    """Test Hamming encoding generator creation."""
    generators = HamiltonianGenerators.hamming_encoding_generators(2, 2)
    
    # Should have 2 layers, each with 2 qubits
    assert len(generators) == 2
    assert all(len(layer) == 2 for layer in generators)
    
    # All generators should be identical (scaled Pauli-Z/2)
    for layer in generators:
        for gen in layer:
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            expected = np.array([-0.5, 0.5])
            assert np.allclose(eigenvals, expected)


def test_sequential_exponential():
    """Test sequential exponential encoding."""
    generators = HamiltonianGenerators.sequential_exponential_generators(2, 3)
    
    # Check scaling factors by layer
    expected_scales = [0.5, 1.0, 2.5]  # β * 0.5 where β = [1, 2, 5]
    
    for layer_idx, layer in enumerate(generators):
        for gen in layer:
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2
            assert np.isclose(scale, expected_scales[layer_idx])


def test_ternary_encoding():
    """Test ternary encoding."""
    generators = HamiltonianGenerators.ternary_encoding_generators(2, 2)
    
    # Expected scaling: β = 3^(layer + n_layers * qubit)
    # Layer 0: qubit 0: 3^0=1, qubit 1: 3^2=9  
    # Layer 1: qubit 0: 3^1=3, qubit 1: 3^3=27
    expected_betas = [[1, 9], [3, 27]]
    
    for layer_idx, layer in enumerate(generators):
        for qubit_idx, gen in enumerate(layer):
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2  # Should be β * 0.5
            expected_scale = expected_betas[layer_idx][qubit_idx] * 0.5
            assert np.isclose(scale, expected_scale)


def test_equal_layers_maximal():
    """Test equal layers maximal encoding."""
    generators = HamiltonianGenerators.equal_layers_maximal_generators(2, 2)
    
    # Expected: β_r = (2L + 1)^(r-1) = (2*2 + 1)^(r-1) = 5^(r-1)
    # Qubit 0: 5^0 = 1, Qubit 1: 5^1 = 5
    expected_scales = [0.5, 2.5]  # β * 0.5
    
    # All layers should be identical (equal encoding)
    for layer in generators:
        for qubit_idx, gen in enumerate(layer):
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2
            assert np.isclose(scale, expected_scales[qubit_idx])


def test_generator_analysis():
    """Test generator spectrum analysis."""
    generators = HamiltonianGenerators.hamming_encoding_generators(2, 2)
    analysis = HamiltonianGenerators.analyze_generator_spectrum(generators)
    
    assert analysis['total_generators'] == 4
    assert analysis['layers'] == 2
    assert analysis['qubits_per_layer'] == 2
    assert len(analysis['unique_scales']) == 1
    assert np.isclose(analysis['unique_scales'][0], 0.5)


if __name__ == "__main__":
    test_pauli_matrices()
    print("✓ Pauli matrices test passed")
    
    test_hamming_encoding()
    print("✓ Hamming encoding test passed")
    
    test_sequential_exponential()
    print("✓ Sequential exponential test passed")
    
    test_ternary_encoding()
    print("✓ Ternary encoding test passed")
    
    test_equal_layers_maximal()
    print("✓ Equal layers maximal test passed")
    
    test_generator_analysis()
    print("✓ Generator analysis test passed")
    
    print("\nAll generator tests passed!")