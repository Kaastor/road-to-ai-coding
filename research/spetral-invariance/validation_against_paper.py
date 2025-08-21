"""
Validation of implementation against the research paper:
"Spectral invariance and maximality properties of the frequency spectrum of quantum neural networks"

This script validates:
1. QNN architecture definition (Section 2)
2. Frequency spectrum calculation (Definition 3, Equation 4)
3. Area-preserving transformations (Theorem 9)
4. Maximality conditions (Theorems 12-13)
5. 2D sub-generator properties (Section 4.1)
"""

import numpy as np
from spectral_qnn.core.simple_qnn import SimpleQuantumNeuralNetwork
from spectral_qnn.core.frequency_analyzer import FrequencySpectrumAnalyzer
from spectral_qnn.core.generators import HamiltonianGenerators
from spectral_qnn.maximality.two_dim_analysis import TwoDimMaximalityAnalyzer


class PaperValidation:
    """Validate implementation against paper specifications."""
    
    def __init__(self):
        self.analyzer = FrequencySpectrumAnalyzer()
        self.maximality_analyzer = TwoDimMaximalityAnalyzer()
        self.validation_results = {}
    
    def validate_qnn_architecture(self):
        """
        Validate QNN architecture against Section 2 of the paper.
        
        Paper Definition: QNN with R qubits, L layers, generators G_{r,l}
        """
        print("=== 1. QNN Architecture Validation ===")
        
        # Test basic QNN structure
        R, L = 3, 2  # 3 qubits, 2 layers
        qnn = SimpleQuantumNeuralNetwork(R, L)
        
        # Validate structure
        assert qnn.n_qubits == R, f"Expected {R} qubits, got {qnn.n_qubits}"
        assert qnn.n_layers == L, f"Expected {L} layers, got {qnn.n_layers}"
        assert qnn.get_shape() == (R, L), f"Expected shape ({R}, {L}), got {qnn.get_shape()}"
        
        # Validate generator structure
        generators = HamiltonianGenerators.hamming_encoding_generators(R, L)
        assert len(generators) == L, f"Expected {L} layers of generators, got {len(generators)}"
        assert all(len(layer) == R for layer in generators), f"Each layer should have {R} generators"
        
        print(f"✓ QNN structure (R={R}, L={L}) matches paper definition")
        
        # Validate Hermitian property of generators
        all_hermitian = True
        for layer_idx, layer in enumerate(generators):
            for qubit_idx, gen in enumerate(layer):
                if not np.allclose(gen, gen.conj().T):
                    all_hermitian = False
                    print(f"✗ Generator G_{{{qubit_idx+1},{layer_idx+1}}} is not Hermitian")
        
        if all_hermitian:
            print("✓ All generators are Hermitian (satisfy paper requirement)")
        
        self.validation_results['qnn_architecture'] = {
            'structure_correct': True,
            'generators_hermitian': all_hermitian,
            'test_passed': all_hermitian
        }
    
    def validate_frequency_spectrum_definition(self):
        """
        Validate frequency spectrum calculation against Definition 3, Equation 4.
        
        Paper: Ω = ⊕_{r,l} Ω_{r,l} where Ω_{r,l} are eigenvalue differences
        """
        print("\n=== 2. Frequency Spectrum Definition Validation ===")
        
        # Test with paper example: R=2, L=1, Pauli-Z generators
        R, L = 2, 1
        
        # Manual calculation per paper
        # For Pauli-Z: eigenvalues = {1, -1}
        # Differences: Ω_{r,l} = {0, 2, -2}
        # Total: Ω = {0, 2, -2} ⊕ {0, 2, -2} = {-4, -2, 0, 2, 4}
        
        expected_spectrum = {-4, -2, 0, 2, 4}
        
        # Test our implementation
        qnn = SimpleQuantumNeuralNetwork(R, L)
        computed_spectrum = qnn.compute_hamming_encoding_spectrum()
        computed_set = set(computed_spectrum)
        
        print(f"Expected spectrum: {sorted(expected_spectrum)}")
        print(f"Computed spectrum: {sorted(computed_set)}")
        
        spectrum_correct = computed_set == expected_spectrum
        print(f"{'✓' if spectrum_correct else '✗'} Spectrum calculation matches paper")
        
        # Test Minkowski sum implementation
        pauli_z_eigenvals = np.array([1, -1])
        diffs = self.analyzer.compute_eigenvalue_differences(pauli_z_eigenvals)
        expected_diffs = {0, 2, -2}
        
        diffs_correct = diffs == expected_diffs
        print(f"{'✓' if diffs_correct else '✗'} Eigenvalue differences calculation correct")
        
        # Test Minkowski sum
        minkowski_result = self.analyzer.minkowski_sum(diffs, diffs)
        minkowski_correct = minkowski_result == expected_spectrum
        print(f"{'✓' if minkowski_correct else '✗'} Minkowski sum implementation correct")
        
        self.validation_results['frequency_spectrum'] = {
            'spectrum_correct': spectrum_correct,
            'eigenvalue_diffs_correct': diffs_correct,
            'minkowski_sum_correct': minkowski_correct,
            'test_passed': spectrum_correct and diffs_correct and minkowski_correct
        }
    
    def validate_area_preserving_invariance(self):
        """
        Validate area-preserving transformation invariance (Theorem 9).
        
        Paper: QNNs with same area A = R × L have identical frequency spectra
        """
        print("\n=== 3. Area-Preserving Invariance Validation ===")
        
        # Test configurations with same area A = 6
        configs = [(2, 3), (3, 2), (1, 6), (6, 1)]
        spectra = []
        
        for R, L in configs:
            qnn = SimpleQuantumNeuralNetwork(R, L)
            spectrum = qnn.compute_hamming_encoding_spectrum()
            spectra.append(set(spectrum))
            print(f"Config ({R}×{L}): spectrum size = {len(spectrum)}")
        
        # Check if all spectra are identical
        all_identical = all(spectrum == spectra[0] for spectrum in spectra[1:])
        
        print(f"{'✓' if all_identical else '✗'} Area-preserving invariance {'holds' if all_identical else 'violated'}")
        
        # Test the demonstrate_spectral_invariance method
        qnn1 = SimpleQuantumNeuralNetwork(2, 3)
        qnn2 = SimpleQuantumNeuralNetwork(3, 2)
        invariance_method_works = qnn1.demonstrate_spectral_invariance(qnn2)
        
        print(f"{'✓' if invariance_method_works else '✗'} demonstrate_spectral_invariance method works")
        
        self.validation_results['area_invariance'] = {
            'theoretical_invariance': all_identical,
            'method_works': invariance_method_works,
            'test_passed': all_identical and invariance_method_works
        }
    
    def validate_maximality_conditions(self):
        """
        Validate maximality conditions from Theorems 12-13.
        
        Paper Theorem 12: For equal data encoding layers, β_r = (2L + 1)^(r-1)
        gives maximum spectrum size |Ω| = (2L + 1)^R - 1
        """
        print("\n=== 4. Maximality Conditions Validation ===")
        
        # Test Theorem 12: Equal data encoding layers
        R, L = 2, 2  # Simple case
        
        # Paper formula: |Ω| = (2L + 1)^R - 1 = (2×2 + 1)^2 - 1 = 5^2 - 1 = 24
        expected_max_size = (2 * L + 1)**R - 1
        
        # Test our implementation
        computed_max_size = self.maximality_analyzer.compute_equal_layers_spectrum_size(R, L)
        
        print(f"Expected max spectrum size: {expected_max_size}")
        print(f"Computed max spectrum size: {computed_max_size}")
        
        theoretical_correct = computed_max_size == expected_max_size
        print(f"{'✓' if theoretical_correct else '✗'} Theoretical maximum calculation correct")
        
        # Test maximality verification
        result = self.maximality_analyzer.verify_equal_layers_maximality(R, L)
        scaling_correct = result['scaling_factors'] == [1, 5]  # (2L+1)^0, (2L+1)^1
        
        print(f"Expected scaling factors: [1, 5]")
        print(f"Computed scaling factors: {result['scaling_factors']}")
        print(f"{'✓' if scaling_correct else '✗'} Scaling factors match Theorem 12")
        
        self.validation_results['maximality'] = {
            'theoretical_formula_correct': theoretical_correct,
            'scaling_factors_correct': scaling_correct,
            'test_passed': theoretical_correct and scaling_correct
        }
    
    def validate_2d_subgenerator_properties(self):
        """
        Validate 2D sub-generator properties (Section 4.1).
        
        Paper: 2D sub-generators are Pauli matrices with eigenvalues {±1}
        """
        print("\n=== 5. 2D Sub-Generator Properties Validation ===")
        
        # Test Pauli matrices implementation
        pauli_z = HamiltonianGenerators.pauli_z()
        expected_pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        pauli_z_correct = np.allclose(pauli_z, expected_pauli_z)
        print(f"{'✓' if pauli_z_correct else '✗'} Pauli-Z matrix correct")
        
        # Test eigenvalues
        eigenvals = HamiltonianGenerators.get_eigenvalues(pauli_z)
        expected_eigenvals = np.array([-1, 1])  # Sorted
        
        eigenvals_correct = np.allclose(eigenvals, expected_eigenvals)
        print(f"Expected eigenvalues: {expected_eigenvals}")
        print(f"Computed eigenvalues: {eigenvals}")
        print(f"{'✓' if eigenvals_correct else '✗'} Pauli-Z eigenvalues correct")
        
        # Test scaled Pauli-Z (used in generators)
        scaled_pauli = HamiltonianGenerators.scaled_pauli_z(0.5)
        scaled_eigenvals = HamiltonianGenerators.get_eigenvalues(scaled_pauli)
        expected_scaled = np.array([-0.5, 0.5])
        
        scaled_correct = np.allclose(scaled_eigenvals, expected_scaled)
        print(f"{'✓' if scaled_correct else '✗'} Scaled Pauli-Z (β=0.5) correct")
        
        # Test 2D sub-generator dimension
        dimension_correct = pauli_z.shape == (2, 2)
        print(f"{'✓' if dimension_correct else '✗'} 2D sub-generator dimension correct")
        
        self.validation_results['2d_subgenerators'] = {
            'pauli_z_correct': pauli_z_correct,
            'eigenvalues_correct': eigenvals_correct,
            'scaled_correct': scaled_correct,
            'dimension_correct': dimension_correct,
            'test_passed': all([pauli_z_correct, eigenvals_correct, scaled_correct, dimension_correct])
        }
    
    def validate_encoding_strategies(self):
        """
        Validate different encoding strategies from the paper.
        """
        print("\n=== 6. Encoding Strategies Validation ===")
        
        R, L = 2, 3
        
        # Test Hamming encoding (all generators identical)
        hamming_gens = HamiltonianGenerators.hamming_encoding_generators(R, L)
        
        # All generators should be identical (scaled Pauli-Z/2)
        base_gen = HamiltonianGenerators.scaled_pauli_z(0.5)
        all_identical = True
        
        for layer in hamming_gens:
            for gen in layer:
                if not np.allclose(gen, base_gen):
                    all_identical = False
                    break
        
        print(f"{'✓' if all_identical else '✗'} Hamming encoding (identical generators) correct")
        
        # Test Sequential Exponential encoding
        seq_gens = HamiltonianGenerators.sequential_exponential_generators(R, L)
        
        # Check scaling per paper: β_l = 2^(l-1) for l < L, β_L = 2^(L-1) + 1
        expected_betas = [1, 2, 5]  # For L=3: [2^0, 2^1, 2^2+1] = [1, 2, 5]
        
        seq_scaling_correct = True
        for layer_idx, layer in enumerate(seq_gens):
            for gen in layer:
                eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
                scale = abs(eigenvals[1] - eigenvals[0]) / 2  # Should be β * 0.5
                expected_scale = expected_betas[layer_idx] * 0.5
                
                if not np.isclose(scale, expected_scale):
                    seq_scaling_correct = False
                    break
        
        print(f"{'✓' if seq_scaling_correct else '✗'} Sequential exponential scaling correct")
        
        # Test Ternary encoding
        ternary_gens = HamiltonianGenerators.ternary_encoding_generators(R, L)
        
        # Check ternary scaling: β_{r,l} = 3^(l-1+L*(r-1))
        # For R=2, L=3: β values should follow 3^(layer + 3*qubit) pattern
        ternary_scaling_correct = True
        for layer_idx, layer in enumerate(ternary_gens):
            for qubit_idx, gen in enumerate(layer):
                eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
                scale = abs(eigenvals[1] - eigenvals[0]) / 2
                expected_beta = 3**(layer_idx + L * qubit_idx)
                expected_scale = expected_beta * 0.5
                
                if not np.isclose(scale, expected_scale, rtol=1e-10):
                    print(f"Ternary mismatch: layer={layer_idx}, qubit={qubit_idx}, "
                          f"expected={expected_scale}, got={scale}")
                    ternary_scaling_correct = False
        
        print(f"{'✓' if ternary_scaling_correct else '✗'} Ternary encoding scaling correct")
        
        self.validation_results['encoding_strategies'] = {
            'hamming_correct': all_identical,
            'sequential_correct': seq_scaling_correct,
            'ternary_correct': ternary_scaling_correct,
            'test_passed': all([all_identical, seq_scaling_correct, ternary_scaling_correct])
        }
    
    def run_comprehensive_validation(self):
        """Run all validation tests and provide summary."""
        print("=" * 60)
        print("COMPREHENSIVE VALIDATION AGAINST RESEARCH PAPER")
        print("=" * 60)
        
        self.validate_qnn_architecture()
        self.validate_frequency_spectrum_definition()
        self.validate_area_preserving_invariance()
        self.validate_maximality_conditions()
        self.validate_2d_subgenerator_properties()
        self.validate_encoding_strategies()
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results.values() 
                          if result['test_passed'])
        
        for test_name, result in self.validation_results.items():
            status = "PASS" if result['test_passed'] else "FAIL"
            print(f"{test_name:25}: {status}")
        
        print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✓ IMPLEMENTATION FULLY COMPLIANT WITH RESEARCH PAPER")
        else:
            print("✗ IMPLEMENTATION HAS DISCREPANCIES WITH RESEARCH PAPER")
            
        return self.validation_results


if __name__ == "__main__":
    validator = PaperValidation()
    results = validator.run_comprehensive_validation()