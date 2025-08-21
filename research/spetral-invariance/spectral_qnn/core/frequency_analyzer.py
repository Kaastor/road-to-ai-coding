"""
Frequency Spectrum Analyzer for Quantum Neural Networks

Implements the mathematical framework from the paper for calculating
and analyzing frequency spectra of QNNs.
"""

import numpy as np
from typing import List, Set, Dict, Tuple
from scipy import linalg


class FrequencySpectrumAnalyzer:
    """
    Analyzes frequency spectra of QNNs based on generator eigenvalues.
    
    Implements key formulas from the paper:
    - Theorem 7: Ω = Σ_l Δσ(H_l) for univariate QNNs
    - Theorem 8: Multivariate frequency spectrum as Cartesian product
    - Theorem 10: Hamming encoding Ω = (λ-μ)·Z_RL
    """
    
    def __init__(self):
        """Initialize the frequency spectrum analyzer."""
        pass
    
    def compute_eigenvalue_differences(self, eigenvalues: np.ndarray) -> Set[float]:
        """
        Compute Δσ(H) = {λ_i - λ_j | λ_i, λ_j ∈ σ(H)}.
        
        Args:
            eigenvalues: Array of eigenvalues of a Hermitian matrix
            
        Returns:
            Set of all pairwise differences
        """
        differences = set()
        for i in range(len(eigenvalues)):
            for j in range(len(eigenvalues)):
                diff = eigenvalues[i] - eigenvalues[j]
                differences.add(float(diff))
        return differences
    
    def minkowski_sum(self, set1: Set[float], set2: Set[float]) -> Set[float]:
        """
        Compute Minkowski sum A + B = {a + b | a ∈ A, b ∈ B}.
        
        Args:
            set1, set2: Sets of real numbers
            
        Returns:
            Minkowski sum of the two sets
        """
        result = set()
        for a in set1:
            for b in set2:
                result.add(a + b)
        return result
    
    def compute_layer_spectrum(self, generators: List[np.ndarray]) -> Set[float]:
        """
        Compute frequency spectrum for a single layer with multiple generators.
        
        Args:
            generators: List of Hermitian matrices (generators for each qubit)
            
        Returns:
            Frequency spectrum for this layer
        """
        if not generators:
            return {0.0}
        
        # Start with differences from first generator
        first_eigenvals = linalg.eigvals(generators[0])
        layer_spectrum = self.compute_eigenvalue_differences(np.real(first_eigenvals))
        
        # Add contributions from remaining generators (Minkowski sum)
        for generator in generators[1:]:
            eigenvals = linalg.eigvals(generator)
            differences = self.compute_eigenvalue_differences(np.real(eigenvals))
            layer_spectrum = self.minkowski_sum(layer_spectrum, differences)
        
        return layer_spectrum
    
    def compute_univariate_spectrum(self, all_generators: List[List[np.ndarray]]) -> np.ndarray:
        """
        Compute frequency spectrum for univariate QNN (Theorem 7).
        
        Args:
            all_generators: List of layers, each containing list of generators
            
        Returns:
            Complete frequency spectrum Ω = Σ_l Δσ(H_l)
        """
        if not all_generators:
            return np.array([0.0])
        
        # Compute spectrum for first layer
        total_spectrum = self.compute_layer_spectrum(all_generators[0])
        
        # Add spectra from remaining layers (Minkowski sum)
        for layer_generators in all_generators[1:]:
            layer_spectrum = self.compute_layer_spectrum(layer_generators)
            total_spectrum = self.minkowski_sum(total_spectrum, layer_spectrum)
        
        return np.array(sorted(list(total_spectrum)))
    
    def compute_hamming_spectrum(self, n_qubits: int, n_layers: int, 
                                eigenvalue_diff: float = 2.0) -> np.ndarray:
        """
        Compute frequency spectrum for Hamming encoding (Theorem 10).
        
        Args:
            n_qubits: Number of qubits (R)
            n_layers: Number of layers (L)
            eigenvalue_diff: λ - μ for the generator (default 2 for Pauli-Z)
            
        Returns:
            Ω = (λ-μ) · Z_RL
        """
        max_freq = int(eigenvalue_diff * n_qubits * n_layers)
        # Z_k = {-k, ..., 0, ..., k} with step size eigenvalue_diff
        frequencies = np.arange(-max_freq, max_freq + eigenvalue_diff, eigenvalue_diff)
        return frequencies
    
    def analyze_maximality(self, spectrum: np.ndarray) -> Dict[str, any]:
        """
        Analyze maximality properties of a frequency spectrum.
        
        Args:
            spectrum: Frequency spectrum array
            
        Returns:
            Dictionary with maximality analysis
        """
        spectrum_set = set(spectrum)
        
        # Find largest K such that Z_K ⊆ Ω
        max_k = 0
        for k in range(1, len(spectrum)):
            z_k = set(range(-k, k + 1))
            if z_k.issubset(spectrum_set):
                max_k = k
            else:
                break
        
        # Check if spectrum is symmetric around 0
        is_symmetric = all(-freq in spectrum_set for freq in spectrum if freq != 0)
        
        # Count gaps in spectrum
        if len(spectrum) > 1:
            min_freq, max_freq = int(min(spectrum)), int(max(spectrum))
            full_range = set(range(min_freq, max_freq + 1))
            gaps = full_range - spectrum_set
            num_gaps = len(gaps)
        else:
            num_gaps = 0
        
        return {
            'size': len(spectrum),
            'max_k_in_spectrum': max_k,
            'is_symmetric': is_symmetric,
            'min_frequency': float(min(spectrum)),
            'max_frequency': float(max(spectrum)),
            'num_gaps': num_gaps,
            'density': len(spectrum_set) / (max(spectrum) - min(spectrum) + 1) if len(spectrum) > 1 else 1.0
        }
    
    def demonstrate_area_invariance(self, shapes: List[Tuple[int, int]]) -> bool:
        """
        Demonstrate spectral invariance under area-preserving transformations.
        
        Args:
            shapes: List of (n_qubits, n_layers) tuples with same area
            
        Returns:
            True if all shapes have the same spectrum
        """
        if not shapes:
            return True
        
        # Check all shapes have same area
        areas = [r * l for r, l in shapes]
        if not all(area == areas[0] for area in areas):
            return False
        
        # Compute spectra for all shapes (using Hamming encoding)
        spectra = []
        for n_qubits, n_layers in shapes:
            spectrum = self.compute_hamming_spectrum(n_qubits, n_layers)
            spectra.append(set(spectrum))
        
        # Check all spectra are identical
        first_spectrum = spectra[0]
        return all(spectrum == first_spectrum for spectrum in spectra[1:])


if __name__ == "__main__":
    # Test the frequency analyzer
    print("=== Frequency Spectrum Analyzer Test ===")
    
    analyzer = FrequencySpectrumAnalyzer()
    
    # Test Hamming encoding spectrum
    spectrum = analyzer.compute_hamming_spectrum(n_qubits=2, n_layers=2)
    print(f"Hamming spectrum (R=2, L=2): {spectrum}")
    
    # Analyze maximality
    analysis = analyzer.analyze_maximality(spectrum)
    print(f"Spectrum analysis: {analysis}")
    
    # Test area invariance
    shapes = [(2, 2), (4, 1), (1, 4)]  # All have area = 4
    is_invariant = analyzer.demonstrate_area_invariance(shapes)
    print(f"Area invariance for shapes {shapes}: {is_invariant}")
    
    print("Frequency analyzer test completed!")