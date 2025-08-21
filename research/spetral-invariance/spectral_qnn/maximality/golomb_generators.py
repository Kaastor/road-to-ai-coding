"""
Arbitrary dimensional generators using Golomb rulers for maximality.

Implements generalized maximality analysis beyond 2D sub-generators:
- Golomb ruler construction for optimal frequency separation
- Arbitrary dimensional Hermitian generators
- Multi-dimensional maximality conditions
"""

import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from itertools import combinations
from ..core.generators import HamiltonianGenerators
from ..core.frequency_analyzer import FrequencySpectrumAnalyzer


class GolombGenerators:
    """
    Generators based on Golomb rulers for arbitrary dimensional maximality.
    
    Golomb rulers provide optimal frequency separation patterns that can be
    used to construct generators with maximal frequency spectra.
    """
    
    def __init__(self):
        self.analyzer = FrequencySpectrumAnalyzer()
    
    def generate_golomb_ruler(self, order: int, max_length: int = None) -> List[int]:
        """
        Generate a Golomb ruler of given order.
        
        A Golomb ruler is a set of marks along a ruler such that 
        no two pairs of marks measure the same distance.
        
        Args:
            order: Number of marks on the ruler
            max_length: Maximum ruler length (if None, uses heuristic)
            
        Returns:
            List of mark positions forming a Golomb ruler
        """
        if order <= 1:
            return [0] if order == 1 else []
        
        if max_length is None:
            # Heuristic: optimal Golomb rulers grow approximately quadratically
            max_length = order * order
        
        # Use backtracking to find a valid Golomb ruler
        ruler = self._backtrack_golomb(order, max_length)
        if ruler is None:
            # Fallback to simple construction if optimal not found
            ruler = self._simple_golomb_construction(order)
        
        return sorted(ruler)
    
    def _backtrack_golomb(self, order: int, max_length: int) -> Optional[List[int]]:
        """Backtracking search for Golomb ruler."""
        def is_valid_partial(marks: List[int]) -> bool:
            """Check if partial ruler has unique differences."""
            differences = set()
            for i in range(len(marks)):
                for j in range(i + 1, len(marks)):
                    diff = marks[j] - marks[i]
                    if diff in differences:
                        return False
                    differences.add(diff)
            return True
        
        def backtrack(marks: List[int], remaining: int) -> Optional[List[int]]:
            if remaining == 0:
                return marks[:]
            
            start = marks[-1] + 1 if marks else 0
            for pos in range(start, max_length + 1):
                marks.append(pos)
                if is_valid_partial(marks):
                    result = backtrack(marks, remaining - 1)
                    if result is not None:
                        return result
                marks.pop()
            return None
        
        return backtrack([0], order - 1)
    
    def _simple_golomb_construction(self, order: int) -> List[int]:
        """Simple Golomb ruler construction (not optimal but valid)."""
        if order <= 4:
            # Known small Golomb rulers
            rulers = {
                1: [0],
                2: [0, 1],
                3: [0, 1, 3],
                4: [0, 1, 4, 9]
            }
            return rulers[order]
        
        # Simple construction: powers of 2 pattern
        ruler = [0]
        pos = 1
        for i in range(1, order):
            ruler.append(pos)
            pos += i + 1
        
        return ruler
    
    def create_golomb_based_generators(self, dimension: int, n_generators: int, 
                                     golomb_order: int = None) -> List[np.ndarray]:
        """
        Create arbitrary dimensional generators using Golomb ruler eigenvalues.
        
        Args:
            dimension: Matrix dimension for each generator
            n_generators: Number of generators to create
            golomb_order: Order of Golomb ruler (if None, uses n_generators)
            
        Returns:
            List of Hermitian generators with Golomb-based eigenvalue patterns
        """
        if golomb_order is None:
            golomb_order = min(dimension, n_generators + 2)
        
        golomb_ruler = self.generate_golomb_ruler(golomb_order)
        
        generators = []
        for i in range(n_generators):
            # Create diagonal matrix with Golomb ruler based eigenvalues
            eigenvals = np.zeros(dimension)
            
            # Map Golomb ruler positions to eigenvalues
            for j in range(min(dimension, len(golomb_ruler))):
                eigenvals[j] = golomb_ruler[j] - golomb_ruler[0]  # Normalize to start at 0
            
            # Add variation based on generator index
            eigenvals = eigenvals + i * 0.1  # Small shift for each generator
            
            # Create Hermitian matrix with these eigenvalues
            generator = self._create_hermitian_with_eigenvalues(eigenvals)
            generators.append(generator)
        
        return generators
    
    def _create_hermitian_with_eigenvalues(self, eigenvals: np.ndarray) -> np.ndarray:
        """
        Create a Hermitian matrix with specified eigenvalues.
        
        Args:
            eigenvals: Desired eigenvalues
            
        Returns:
            Hermitian matrix with given eigenvalues
        """
        n = len(eigenvals)
        
        # Generate random unitary matrix for eigenvectors
        A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        Q, _ = np.linalg.qr(A)  # QR decomposition gives unitary Q
        
        # Create diagonal matrix with eigenvalues
        D = np.diag(eigenvals)
        
        # Construct Hermitian matrix: H = Q D Q†
        H = Q @ D @ Q.conj().T
        
        return H
    
    def analyze_golomb_spectrum(self, generators: List[np.ndarray]) -> Dict[str, any]:
        """
        Analyze frequency spectrum of Golomb-based generators.
        
        Args:
            generators: List of generators to analyze
            
        Returns:
            Spectrum analysis results
        """
        all_eigenvalue_diffs = []
        
        for generator in generators:
            eigenvals = HamiltonianGenerators.get_eigenvalues(generator)
            diffs = self.analyzer.compute_eigenvalue_differences(eigenvals)
            all_eigenvalue_diffs.append(diffs)
        
        # Compute combined spectrum via Minkowski sums
        if not all_eigenvalue_diffs:
            return {'spectrum': set(), 'size': 0, 'generators': 0}
        
        combined_spectrum = all_eigenvalue_diffs[0]
        for diffs in all_eigenvalue_diffs[1:]:
            combined_spectrum = self.analyzer.minkowski_sum(combined_spectrum, diffs)
        
        # Analyze spectrum properties
        spectrum_list = sorted(combined_spectrum)
        gaps = []
        if len(spectrum_list) > 1:
            for i in range(1, len(spectrum_list)):
                gap = spectrum_list[i] - spectrum_list[i-1]
                gaps.append(gap)
        
        return {
            'spectrum': combined_spectrum,
            'spectrum_size': len(combined_spectrum),
            'spectrum_list': spectrum_list,
            'generators_count': len(generators),
            'generator_dimensions': [gen.shape[0] for gen in generators],
            'gaps': gaps,
            'min_gap': min(gaps) if gaps else 0,
            'max_gap': max(gaps) if gaps else 0,
            'unique_gaps': len(set(gaps)) if gaps else 0
        }
    
    def compare_golomb_vs_standard(self, dimension: int, n_generators: int, 
                                  n_layers: int = 1) -> Dict[str, any]:
        """
        Compare Golomb-based generators vs standard approaches.
        
        Args:
            dimension: Generator dimension
            n_generators: Number of generators per approach
            n_layers: Number of layers for standard approaches
            
        Returns:
            Comparison results
        """
        # Generate Golomb-based generators
        golomb_gens = self.create_golomb_based_generators(dimension, n_generators)
        golomb_analysis = self.analyze_golomb_spectrum(golomb_gens)
        
        # Generate standard Pauli-Z based generators for comparison
        if dimension == 2:
            # Use 2D sub-generators (Pauli matrices)
            standard_gens = []
            for i in range(n_generators):
                gen = HamiltonianGenerators.scaled_pauli_z((i + 1) * 0.5)
                standard_gens.append(gen)
        else:
            # Use random Hermitian generators
            standard_gens = []
            for i in range(n_generators):
                gen = HamiltonianGenerators.random_hermitian(dimension, seed=i)
                standard_gens.append(gen)
        
        standard_analysis = self.analyze_golomb_spectrum(standard_gens)
        
        return {
            'golomb_results': golomb_analysis,
            'standard_results': standard_analysis,
            'golomb_advantage': {
                'spectrum_size_ratio': golomb_analysis['spectrum_size'] / max(standard_analysis['spectrum_size'], 1),
                'unique_gaps_ratio': golomb_analysis['unique_gaps'] / max(standard_analysis['unique_gaps'], 1),
                'min_gap_ratio': golomb_analysis['min_gap'] / max(standard_analysis['min_gap'], 1) if standard_analysis['min_gap'] > 0 else float('inf')
            }
        }
    
    def find_optimal_golomb_configuration(self, max_dimension: int = 5, 
                                        max_generators: int = 4) -> Dict[str, any]:
        """
        Find optimal Golomb ruler configuration for maximality.
        
        Args:
            max_dimension: Maximum generator dimension to test
            max_generators: Maximum number of generators to test
            
        Returns:
            Optimal configuration results
        """
        best_config = None
        best_spectrum_size = 0
        all_results = []
        
        for dimension in range(2, max_dimension + 1):
            for n_generators in range(1, max_generators + 1):
                comparison = self.compare_golomb_vs_standard(dimension, n_generators)
                
                golomb_size = comparison['golomb_results']['spectrum_size']
                config = {
                    'dimension': dimension,
                    'n_generators': n_generators,
                    'spectrum_size': golomb_size,
                    'comparison': comparison
                }
                
                all_results.append(config)
                
                if golomb_size > best_spectrum_size:
                    best_spectrum_size = golomb_size
                    best_config = config
        
        return {
            'best_configuration': best_config,
            'all_results': all_results,
            'total_configurations_tested': len(all_results)
        }


if __name__ == "__main__":
    golomb_gen = GolombGenerators()
    
    print("=== Golomb Rulers Generators Analysis ===")
    
    # Test Golomb ruler generation
    print("\n1. Golomb Ruler Generation:")
    for order in range(2, 6):
        ruler = golomb_gen.generate_golomb_ruler(order)
        print(f"   Order {order}: {ruler}")
    
    # Test generator creation and analysis
    print("\n2. Golomb-based Generator Analysis:")
    for dimension in [2, 3]:
        generators = golomb_gen.create_golomb_based_generators(dimension, 3)
        analysis = golomb_gen.analyze_golomb_spectrum(generators)
        print(f"   Dimension {dimension}: Spectrum size = {analysis['spectrum_size']}, Generators = {analysis['generators_count']}")
    
    # Comparison with standard approaches
    print("\n3. Golomb vs Standard Comparison:")
    comparison = golomb_gen.compare_golomb_vs_standard(dimension=3, n_generators=2)
    golomb_size = comparison['golomb_results']['spectrum_size']
    standard_size = comparison['standard_results']['spectrum_size']
    ratio = comparison['golomb_advantage']['spectrum_size_ratio']
    print(f"   Golomb: {golomb_size}, Standard: {standard_size}, Ratio: {ratio:.2f}")
    
    # Find optimal configuration
    print("\n4. Optimal Configuration Search:")
    optimal = golomb_gen.find_optimal_golomb_configuration(max_dimension=4, max_generators=3)
    best = optimal['best_configuration']
    print(f"   Best: Dim={best['dimension']}, Gens={best['n_generators']}, Size={best['spectrum_size']}")
    
    print("\nGolomb generators analysis completed!")