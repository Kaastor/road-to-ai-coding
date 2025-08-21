"""
Hamiltonian Generators for Quantum Neural Networks

Implements various generator types mentioned in the paper:
- Pauli matrices (2D sub-generators)
- Arbitrary Hermitian generators
- Scaled generators for different encoding strategies
"""

import numpy as np
from typing import List, Tuple, Dict, Union
from scipy import linalg


class HamiltonianGenerators:
    """
    Factory and utility class for creating Hamiltonian generators.
    
    Supports the various encoding strategies from the paper:
    - Hamming encoding (equal generators)
    - Sequential/Parallel exponential encoding  
    - Ternary encoding
    - Custom generators for maximality
    """
    
    @staticmethod
    def pauli_x() -> np.ndarray:
        """Pauli-X matrix."""
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def pauli_y() -> np.ndarray:
        """Pauli-Y matrix."""
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def pauli_z() -> np.ndarray:
        """Pauli-Z matrix."""
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def scaled_pauli_z(scale: float) -> np.ndarray:
        """Scaled Pauli-Z matrix for encoding strategies."""
        return scale * HamiltonianGenerators.pauli_z()
    
    @staticmethod
    def random_hermitian(size: int, seed: int = None) -> np.ndarray:
        """
        Generate random Hermitian matrix.
        
        Args:
            size: Matrix dimension
            seed: Random seed for reproducibility
            
        Returns:
            Random Hermitian matrix
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Generate random complex matrix
        A = np.random.randn(size, size) + 1j * np.random.randn(size, size)
        
        # Make it Hermitian: H = (A + A†) / 2
        H = (A + A.conj().T) / 2
        return H
    
    @classmethod
    def hamming_encoding_generators(cls, n_qubits: int, n_layers: int) -> List[List[np.ndarray]]:
        """
        Create generators for Hamming encoding strategy.
        All generators are identical Pauli-Z/2.
        
        Args:
            n_qubits: Number of qubits
            n_layers: Number of layers
            
        Returns:
            List of layers, each containing identical generators
        """
        base_generator = cls.scaled_pauli_z(0.5)  # Z/2
        
        generators = []
        for layer in range(n_layers):
            layer_generators = [base_generator.copy() for _ in range(n_qubits)]
            generators.append(layer_generators)
        
        return generators
    
    @classmethod
    def sequential_exponential_generators(cls, n_qubits: int, n_layers: int) -> List[List[np.ndarray]]:
        """
        Create generators for sequential exponential encoding (Equation 14).
        
        β_l = 2^(l-1) for l < L, β_L = 2^(L-1) + 1
        
        Args:
            n_qubits: Number of qubits  
            n_layers: Number of layers
            
        Returns:
            Generators with exponential scaling per layer
        """
        generators = []
        
        for layer in range(n_layers):
            if layer < n_layers - 1:
                beta = 2**(layer)  # 2^(l-1) but 0-indexed
            else:
                beta = 2**(n_layers - 1) + 1  # Special case for last layer
            
            layer_generators = []
            for qubit in range(n_qubits):
                generator = cls.scaled_pauli_z(beta * 0.5)  # β * Z/2
                layer_generators.append(generator)
            
            generators.append(layer_generators)
        
        return generators
    
    @classmethod
    def ternary_encoding_generators(cls, n_qubits: int, n_layers: int) -> List[List[np.ndarray]]:
        """
        Create generators for ternary encoding strategy.
        
        β_{r,l} = 3^(l-1+L*(r-1)) for maximum frequency spectrum.
        
        Args:
            n_qubits: Number of qubits
            n_layers: Number of layers
            
        Returns:
            Generators with ternary scaling
        """
        generators = []
        
        for layer in range(n_layers):
            layer_generators = []
            for qubit in range(n_qubits):
                # 0-indexed: β = 3^(layer + n_layers * qubit)
                beta = 3**(layer + n_layers * qubit)
                generator = cls.scaled_pauli_z(beta * 0.5)  # β * Z/2
                layer_generators.append(generator)
            
            generators.append(layer_generators)
        
        return generators
    
    @classmethod
    def equal_layers_maximal_generators(cls, n_qubits: int, n_layers: int) -> List[List[np.ndarray]]:
        """
        Create generators for maximal frequency spectrum with equal data encoding layers.
        
        From Theorem 12: β_r = (2L + 1)^(r-1)
        
        Args:
            n_qubits: Number of qubits
            n_layers: Number of layers
            
        Returns:
            Maximal generators for equal layers case
        """
        generators = []
        
        # All layers have the same generators (equal encoding)
        layer_generators = []
        for qubit in range(n_qubits):
            beta = (2 * n_layers + 1)**qubit  # (2L + 1)^(r-1), 0-indexed
            generator = cls.scaled_pauli_z(beta * 0.5)  # β * Z/2
            layer_generators.append(generator)
        
        # Replicate for all layers (equal encoding)
        for layer in range(n_layers):
            generators.append([g.copy() for g in layer_generators])
        
        return generators
    
    @staticmethod
    def get_eigenvalues(generator: np.ndarray) -> np.ndarray:
        """
        Get eigenvalues of a Hermitian generator.
        
        Args:
            generator: Hermitian matrix
            
        Returns:
            Real eigenvalues sorted in ascending order
        """
        eigenvals = linalg.eigvals(generator)
        return np.sort(np.real(eigenvals))
    
    @staticmethod 
    def analyze_generator_spectrum(generators: List[List[np.ndarray]]) -> Dict[str, any]:
        """
        Analyze the spectrum properties of a set of generators.
        
        Args:
            generators: List of layers containing generators
            
        Returns:
            Analysis dictionary with spectrum properties
        """
        all_eigenvals = []
        scaling_factors = []
        
        for layer_idx, layer_generators in enumerate(generators):
            for qubit_idx, generator in enumerate(layer_generators):
                eigenvals = HamiltonianGenerators.get_eigenvalues(generator)
                all_eigenvals.append(eigenvals)
                
                # Try to extract scaling factor (assuming scaled Pauli-Z)
                if len(eigenvals) == 2:
                    scale = abs(eigenvals[0] - eigenvals[1]) / 2  # |λ - μ| / 2
                    scaling_factors.append(scale)
        
        return {
            'total_generators': sum(len(layer) for layer in generators),
            'layers': len(generators),
            'qubits_per_layer': len(generators[0]) if generators else 0,
            'eigenvalue_ranges': [(min(ev), max(ev)) for ev in all_eigenvals],
            'scaling_factors': scaling_factors,
            'unique_scales': sorted(list(set(scaling_factors))),
            'max_eigenvalue_diff': max(abs(ev[1] - ev[0]) for ev in all_eigenvals) if all_eigenvals else 0
        }


if __name__ == "__main__":
    # Test generator creation and analysis
    print("=== Hamiltonian Generators Test ===")
    
    # Test different encoding strategies
    print("\n1. Hamming Encoding (R=2, L=2):")
    hamming_gens = HamiltonianGenerators.hamming_encoding_generators(2, 2)
    hamming_analysis = HamiltonianGenerators.analyze_generator_spectrum(hamming_gens)
    print(f"   Analysis: {hamming_analysis}")
    
    print("\n2. Sequential Exponential Encoding (R=2, L=3):")
    seq_exp_gens = HamiltonianGenerators.sequential_exponential_generators(2, 3)
    seq_analysis = HamiltonianGenerators.analyze_generator_spectrum(seq_exp_gens)
    print(f"   Analysis: {seq_analysis}")
    
    print("\n3. Ternary Encoding (R=2, L=2):")
    ternary_gens = HamiltonianGenerators.ternary_encoding_generators(2, 2)
    ternary_analysis = HamiltonianGenerators.analyze_generator_spectrum(ternary_gens)
    print(f"   Analysis: {ternary_analysis}")
    
    print("\n4. Equal Layers Maximal (R=2, L=2):")
    maximal_gens = HamiltonianGenerators.equal_layers_maximal_generators(2, 2)
    maximal_analysis = HamiltonianGenerators.analyze_generator_spectrum(maximal_gens)
    print(f"   Analysis: {maximal_analysis}")
    
    print("\nGenerator tests completed!")