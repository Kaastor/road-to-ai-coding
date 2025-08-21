"""
Test suite to validate compliance with research paper specifications.
"""

import numpy as np
from spectral_qnn.core.simple_qnn import SimpleQuantumNeuralNetwork
from spectral_qnn.core.frequency_analyzer import FrequencySpectrumAnalyzer
from spectral_qnn.core.generators import HamiltonianGenerators
from spectral_qnn.maximality.two_dim_analysis import TwoDimMaximalityAnalyzer


def test_paper_qnn_architecture():
    """Test QNN architecture matches paper definition."""
    R, L = 3, 2
    qnn = SimpleQuantumNeuralNetwork(R, L)
    
    assert qnn.n_qubits == R
    assert qnn.n_layers == L
    assert qnn.get_shape() == (R, L)
    
    # Verify generator structure
    generators = HamiltonianGenerators.hamming_encoding_generators(R, L)
    assert len(generators) == L
    assert all(len(layer) == R for layer in generators)
    
    # Verify Hermitian property
    for layer in generators:
        for gen in layer:
            assert np.allclose(gen, gen.conj().T), "Generator must be Hermitian"


def test_paper_frequency_spectrum_definition():
    """Test frequency spectrum calculation against paper Definition 3."""
    # Paper example: R=2, L=1 with Pauli-Z should give {-4, -2, 0, 2, 4}
    R, L = 2, 1
    expected_spectrum = {-4, -2, 0, 2, 4}
    
    qnn = SimpleQuantumNeuralNetwork(R, L)
    computed_spectrum = set(qnn.compute_hamming_encoding_spectrum())
    
    assert computed_spectrum == expected_spectrum, f"Expected {expected_spectrum}, got {computed_spectrum}"
    
    # Test eigenvalue differences for Pauli-Z
    analyzer = FrequencySpectrumAnalyzer()
    pauli_z_eigenvals = np.array([1, -1])
    diffs = analyzer.compute_eigenvalue_differences(pauli_z_eigenvals)
    expected_diffs = {0, 2, -2}
    
    assert diffs == expected_diffs, f"Expected differences {expected_diffs}, got {diffs}"


def test_paper_area_preserving_invariance():
    """Test area-preserving transformation invariance (Theorem 9)."""
    # Test configurations with same area A = 6
    configs = [(2, 3), (3, 2), (1, 6)]
    spectra = []
    
    for R, L in configs:
        qnn = SimpleQuantumNeuralNetwork(R, L)
        spectrum = set(qnn.compute_hamming_encoding_spectrum())
        spectra.append(spectrum)
    
    # All spectra should be identical
    assert all(spectrum == spectra[0] for spectrum in spectra[1:]), "Area-preserving invariance violated"
    
    # Test method
    qnn1 = SimpleQuantumNeuralNetwork(2, 3)
    qnn2 = SimpleQuantumNeuralNetwork(3, 2)
    assert qnn1.demonstrate_spectral_invariance(qnn2), "Spectral invariance method failed"


def test_paper_maximality_conditions():
    """Test maximality conditions from Theorem 12."""
    R, L = 2, 2
    
    # Paper formula: |Ω| = (2L + 1)^R - 1 = 5^2 - 1 = 24
    expected_max_size = (2 * L + 1)**R - 1
    
    maximality_analyzer = TwoDimMaximalityAnalyzer()
    computed_max_size = maximality_analyzer.compute_equal_layers_spectrum_size(R, L)
    
    assert computed_max_size == expected_max_size, f"Expected {expected_max_size}, got {computed_max_size}"
    
    # Test scaling factors
    result = maximality_analyzer.verify_equal_layers_maximality(R, L)
    expected_scaling = [1, 5]  # (2L+1)^0, (2L+1)^1 = [1, 5]
    
    assert result['scaling_factors'] == expected_scaling, f"Expected {expected_scaling}, got {result['scaling_factors']}"


def test_paper_2d_subgenerator_properties():
    """Test 2D sub-generator properties (Section 4.1)."""
    # Test Pauli-Z matrix
    pauli_z = HamiltonianGenerators.pauli_z()
    expected_pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    assert np.allclose(pauli_z, expected_pauli_z), "Pauli-Z matrix incorrect"
    
    # Test eigenvalues
    eigenvals = HamiltonianGenerators.get_eigenvalues(pauli_z)
    expected_eigenvals = np.array([-1, 1])  # Sorted
    
    assert np.allclose(eigenvals, expected_eigenvals), f"Expected eigenvalues {expected_eigenvals}, got {eigenvals}"
    
    # Test scaled Pauli-Z
    scaled_pauli = HamiltonianGenerators.scaled_pauli_z(0.5)
    scaled_eigenvals = HamiltonianGenerators.get_eigenvalues(scaled_pauli)
    expected_scaled = np.array([-0.5, 0.5])
    
    assert np.allclose(scaled_eigenvals, expected_scaled), "Scaled Pauli-Z incorrect"
    
    # Test dimension
    assert pauli_z.shape == (2, 2), "2D sub-generator should be 2×2"


def test_paper_encoding_strategies():
    """Test encoding strategies match paper specifications."""
    R, L = 2, 3
    
    # Test Hamming encoding (all generators identical)
    hamming_gens = HamiltonianGenerators.hamming_encoding_generators(R, L)
    base_gen = HamiltonianGenerators.scaled_pauli_z(0.5)
    
    for layer in hamming_gens:
        for gen in layer:
            assert np.allclose(gen, base_gen), "Hamming encoding generators should be identical"
    
    # Test Sequential Exponential encoding scaling
    seq_gens = HamiltonianGenerators.sequential_exponential_generators(R, L)
    expected_betas = [1, 2, 5]  # [2^0, 2^1, 2^2+1]
    
    for layer_idx, layer in enumerate(seq_gens):
        for gen in layer:
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2
            expected_scale = expected_betas[layer_idx] * 0.5
            assert np.isclose(scale, expected_scale), f"Sequential scaling mismatch at layer {layer_idx}"
    
    # Test Ternary encoding scaling
    ternary_gens = HamiltonianGenerators.ternary_encoding_generators(R, L)
    
    for layer_idx, layer in enumerate(ternary_gens):
        for qubit_idx, gen in enumerate(layer):
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2
            expected_beta = 3**(layer_idx + L * qubit_idx)
            expected_scale = expected_beta * 0.5
            assert np.isclose(scale, expected_scale, rtol=1e-10), f"Ternary scaling mismatch"


if __name__ == "__main__":
    test_paper_qnn_architecture()
    print("✓ Paper QNN architecture test passed")
    
    test_paper_frequency_spectrum_definition()
    print("✓ Paper frequency spectrum definition test passed")
    
    test_paper_area_preserving_invariance()
    print("✓ Paper area-preserving invariance test passed")
    
    test_paper_maximality_conditions()
    print("✓ Paper maximality conditions test passed")
    
    test_paper_2d_subgenerator_properties()
    print("✓ Paper 2D sub-generator properties test passed")
    
    test_paper_encoding_strategies()
    print("✓ Paper encoding strategies test passed")
    
    print("\nAll paper compliance tests passed!")