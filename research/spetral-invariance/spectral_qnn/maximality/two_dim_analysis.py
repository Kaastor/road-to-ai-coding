"""
Two-dimensional sub-generator maximality analysis.

Implements theoretical results from Theorems 12 and 13:
- Equal data encoding layers maximality
- Arbitrary data encoding layers maximality 
- Optimal generator scaling for maximum frequency spectrum size
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from ..core.generators import HamiltonianGenerators
from ..core.frequency_analyzer import FrequencySpectrumAnalyzer


class TwoDimMaximalityAnalyzer:
    """
    Analyzes maximality properties of 2D sub-generators (Pauli matrices).
    
    Focuses on Theorems 12 and 13 from the paper:
    - Equal data encoding: β_r = (2L + 1)^(r-1) 
    - Arbitrary encoding: finding optimal scaling factors
    """
    
    def __init__(self):
        self.analyzer = FrequencySpectrumAnalyzer()
    
    def compute_equal_layers_spectrum_size(self, n_qubits: int, n_layers: int) -> int:
        """
        Compute spectrum size for equal data encoding layers (Theorem 12).
        
        For β_r = (2L + 1)^(r-1), the spectrum size is:
        |Ω| = (2L + 1)^R - 1
        
        Args:
            n_qubits: Number of qubits (R)
            n_layers: Number of layers (L)
            
        Returns:
            Maximum possible spectrum size
        """
        base = 2 * n_layers + 1
        spectrum_size = base**n_qubits - 1
        return spectrum_size
    
    def verify_equal_layers_maximality(self, n_qubits: int, n_layers: int) -> Dict[str, any]:
        """
        Verify that equal layers encoding achieves theoretical maximum.
        
        Args:
            n_qubits: Number of qubits
            n_layers: Number of layers
            
        Returns:
            Analysis of maximality achievement
        """
        # Generate equal layers maximal generators
        generators = HamiltonianGenerators.equal_layers_maximal_generators(n_qubits, n_layers)
        
        # Compute actual frequency spectrum using Minkowski sum approach
        all_eigenvalue_diffs = []
        
        for layer_generators in generators:
            for generator in layer_generators:
                eigenvals = HamiltonianGenerators.get_eigenvalues(generator)
                diffs = self.analyzer.compute_eigenvalue_differences(eigenvals)
                all_eigenvalue_diffs.append(diffs)
        
        # Compute total spectrum via repeated Minkowski sums
        total_spectrum = all_eigenvalue_diffs[0]
        for diffs in all_eigenvalue_diffs[1:]:
            total_spectrum = self.analyzer.minkowski_sum(total_spectrum, diffs)
        
        # Get theoretical maximum
        theoretical_max = self.compute_equal_layers_spectrum_size(n_qubits, n_layers)
        actual_size = len(total_spectrum)
        
        return {
            'n_qubits': n_qubits,
            'n_layers': n_layers,
            'theoretical_max_size': theoretical_max,
            'actual_spectrum_size': actual_size,
            'is_maximal': actual_size == theoretical_max,
            'spectrum': sorted(total_spectrum),
            'scaling_base': 2 * n_layers + 1,
            'scaling_factors': [(2 * n_layers + 1)**r for r in range(n_qubits)]
        }
    
    def find_arbitrary_encoding_optimum(self, n_qubits: int, n_layers: int, 
                                      max_iterations: int = 100) -> Dict[str, any]:
        """
        Find optimal scaling factors for arbitrary data encoding (Theorem 13).
        
        Uses heuristic search to find β values that maximize |Ω|.
        
        Args:
            n_qubits: Number of qubits
            n_layers: Number of layers  
            max_iterations: Maximum search iterations
            
        Returns:
            Best found scaling configuration
        """
        best_spectrum_size = 0
        best_scaling_factors = None
        best_spectrum = None
        
        # Try different scaling strategies
        scaling_strategies = [
            # Equal layers baseline
            [(2 * n_layers + 1)**r for r in range(n_qubits)],
            # Sequential powers
            [2**r for r in range(n_qubits)],
            # Fibonacci-like
            self._fibonacci_scaling(n_qubits),
            # Prime-based
            self._prime_scaling(n_qubits),
        ]
        
        for scaling_factors in scaling_strategies:
            spectrum_size, spectrum = self._evaluate_scaling_factors(
                scaling_factors, n_qubits, n_layers
            )
            
            if spectrum_size > best_spectrum_size:
                best_spectrum_size = spectrum_size
                best_scaling_factors = scaling_factors
                best_spectrum = spectrum
        
        # Get equal layers reference for comparison
        equal_layers_result = self.verify_equal_layers_maximality(n_qubits, n_layers)
        
        return {
            'best_spectrum_size': best_spectrum_size,
            'best_scaling_factors': best_scaling_factors,
            'best_spectrum': sorted(best_spectrum) if best_spectrum else None,
            'equal_layers_size': equal_layers_result['actual_spectrum_size'],
            'improvement_over_equal': best_spectrum_size - equal_layers_result['actual_spectrum_size'],
            'is_better_than_equal': best_spectrum_size > equal_layers_result['actual_spectrum_size']
        }
    
    def _fibonacci_scaling(self, n_qubits: int) -> List[int]:
        """Generate Fibonacci-based scaling factors."""
        if n_qubits <= 0:
            return []
        if n_qubits == 1:
            return [1]
        
        fib = [1, 1]
        for i in range(2, n_qubits):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    def _prime_scaling(self, n_qubits: int) -> List[int]:
        """Generate prime-based scaling factors."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        return primes[:n_qubits] if n_qubits <= len(primes) else primes + list(range(53, 53 + n_qubits - len(primes)))
    
    def _evaluate_scaling_factors(self, scaling_factors: List[int], 
                                n_qubits: int, n_layers: int) -> Tuple[int, set]:
        """
        Evaluate spectrum size for given scaling factors.
        
        Args:
            scaling_factors: β values for each qubit
            n_qubits: Number of qubits
            n_layers: Number of layers
            
        Returns:
            (spectrum_size, spectrum_set)
        """
        all_eigenvalue_diffs = []
        
        # Create generators with custom scaling
        for layer in range(n_layers):
            for qubit in range(n_qubits):
                beta = scaling_factors[qubit]
                generator = HamiltonianGenerators.scaled_pauli_z(beta * 0.5)
                eigenvals = HamiltonianGenerators.get_eigenvalues(generator)
                diffs = self.analyzer.compute_eigenvalue_differences(eigenvals)
                all_eigenvalue_diffs.append(diffs)
        
        # Compute spectrum via Minkowski sums
        if not all_eigenvalue_diffs:
            return 0, set()
            
        total_spectrum = all_eigenvalue_diffs[0]
        for diffs in all_eigenvalue_diffs[1:]:
            total_spectrum = self.analyzer.minkowski_sum(total_spectrum, diffs)
        
        return len(total_spectrum), total_spectrum
    
    def analyze_maximality_conditions(self, max_qubits: int = 4, max_layers: int = 3) -> Dict[str, any]:
        """
        Comprehensive analysis of maximality conditions across different configurations.
        
        Args:
            max_qubits: Maximum number of qubits to analyze
            max_layers: Maximum number of layers to analyze
            
        Returns:
            Comprehensive maximality analysis results
        """
        results = {
            'equal_layers_results': [],
            'arbitrary_encoding_results': [],
            'summary_statistics': {}
        }
        
        total_configurations = 0
        equal_layers_maximal_count = 0
        arbitrary_improvements = 0
        
        for n_qubits in range(1, max_qubits + 1):
            for n_layers in range(1, max_layers + 1):
                total_configurations += 1
                
                # Equal layers analysis
                equal_result = self.verify_equal_layers_maximality(n_qubits, n_layers)
                results['equal_layers_results'].append(equal_result)
                
                if equal_result['is_maximal']:
                    equal_layers_maximal_count += 1
                
                # Arbitrary encoding optimization
                arbitrary_result = self.find_arbitrary_encoding_optimum(n_qubits, n_layers)
                arbitrary_result.update({
                    'n_qubits': n_qubits,
                    'n_layers': n_layers
                })
                results['arbitrary_encoding_results'].append(arbitrary_result)
                
                if arbitrary_result['is_better_than_equal']:
                    arbitrary_improvements += 1
        
        results['summary_statistics'] = {
            'total_configurations': total_configurations,
            'equal_layers_maximal_count': equal_layers_maximal_count,
            'equal_layers_maximal_rate': equal_layers_maximal_count / total_configurations,
            'arbitrary_improvements': arbitrary_improvements,
            'arbitrary_improvement_rate': arbitrary_improvements / total_configurations
        }
        
        return results


if __name__ == "__main__":
    analyzer = TwoDimMaximalityAnalyzer()
    
    print("=== 2D Sub-generator Maximality Analysis ===")
    
    # Test equal layers maximality for small cases
    print("\n1. Equal Layers Maximality Verification:")
    for n_qubits in [2, 3]:
        for n_layers in [1, 2]:
            result = analyzer.verify_equal_layers_maximality(n_qubits, n_layers)
            print(f"   R={n_qubits}, L={n_layers}: Size={result['actual_spectrum_size']}/{result['theoretical_max_size']}, Maximal={result['is_maximal']}")
    
    # Test arbitrary encoding optimization
    print("\n2. Arbitrary Encoding Optimization:")
    for n_qubits in [2, 3]:
        result = analyzer.find_arbitrary_encoding_optimum(n_qubits, 2)
        print(f"   R={n_qubits}: Best size={result['best_spectrum_size']}, Equal size={result['equal_layers_size']}, Improvement={result['improvement_over_equal']}")
    
    # Comprehensive analysis
    print("\n3. Comprehensive Maximality Analysis:")
    comprehensive = analyzer.analyze_maximality_conditions(max_qubits=3, max_layers=2)
    stats = comprehensive['summary_statistics']
    print(f"   Equal layers maximal rate: {stats['equal_layers_maximal_rate']:.2%}")
    print(f"   Arbitrary improvement rate: {stats['arbitrary_improvement_rate']:.2%}")
    
    print("\nMaximality analysis completed!")