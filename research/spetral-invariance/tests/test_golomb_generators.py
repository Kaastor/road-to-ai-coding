"""
Tests for Golomb ruler based generators.
"""

import numpy as np
from spectral_qnn.maximality.golomb_generators import GolombGenerators


def test_golomb_ruler_generation():
    """Test Golomb ruler generation."""
    golomb_gen = GolombGenerators()
    
    # Test small orders
    ruler1 = golomb_gen.generate_golomb_ruler(1)
    assert ruler1 == [0]
    
    ruler2 = golomb_gen.generate_golomb_ruler(2)
    assert len(ruler2) == 2
    assert ruler2[0] == 0  # Should start with 0
    assert len(set(ruler2)) == 2  # All unique
    
    ruler3 = golomb_gen.generate_golomb_ruler(3)
    assert len(ruler3) == 3
    assert ruler3 == sorted(ruler3)  # Should be sorted
    
    # Verify Golomb property: all pairwise differences unique
    differences = set()
    for i in range(len(ruler3)):
        for j in range(i + 1, len(ruler3)):
            diff = ruler3[j] - ruler3[i]
            assert diff not in differences, f"Duplicate difference {diff}"
            differences.add(diff)


def test_golomb_generator_creation():
    """Test creation of Golomb-based generators."""
    golomb_gen = GolombGenerators()
    
    # Test generator creation
    generators = golomb_gen.create_golomb_based_generators(dimension=3, n_generators=2)
    
    assert len(generators) == 2
    assert all(gen.shape == (3, 3) for gen in generators)
    
    # Check that generators are Hermitian
    for gen in generators:
        assert np.allclose(gen, gen.conj().T), "Generator should be Hermitian"


def test_hermitian_eigenvalue_construction():
    """Test creation of Hermitian matrix with specified eigenvalues."""
    golomb_gen = GolombGenerators()
    
    eigenvals = np.array([1.0, 2.0, 3.0])
    matrix = golomb_gen._create_hermitian_with_eigenvalues(eigenvals)
    
    # Check Hermitian property
    assert np.allclose(matrix, matrix.conj().T)
    
    # Check eigenvalues (up to reordering)
    computed_eigenvals = np.linalg.eigvals(matrix)
    assert np.allclose(sorted(np.real(eigenvals)), sorted(np.real(computed_eigenvals)))


def test_golomb_spectrum_analysis():
    """Test spectrum analysis of Golomb generators."""
    golomb_gen = GolombGenerators()
    
    # Create simple generators for testing
    generators = golomb_gen.create_golomb_based_generators(dimension=2, n_generators=2)
    analysis = golomb_gen.analyze_golomb_spectrum(generators)
    
    assert 'spectrum' in analysis
    assert 'spectrum_size' in analysis
    assert 'generators_count' in analysis
    assert 'generator_dimensions' in analysis
    
    assert analysis['generators_count'] == 2
    assert analysis['generator_dimensions'] == [2, 2]
    assert isinstance(analysis['spectrum_size'], int)
    assert analysis['spectrum_size'] > 0


def test_golomb_vs_standard_comparison():
    """Test comparison between Golomb and standard generators."""
    golomb_gen = GolombGenerators()
    
    comparison = golomb_gen.compare_golomb_vs_standard(dimension=2, n_generators=2)
    
    assert 'golomb_results' in comparison
    assert 'standard_results' in comparison
    assert 'golomb_advantage' in comparison
    
    golomb_res = comparison['golomb_results']
    standard_res = comparison['standard_results']
    advantage = comparison['golomb_advantage']
    
    assert isinstance(golomb_res['spectrum_size'], int)
    assert isinstance(standard_res['spectrum_size'], int)
    assert 'spectrum_size_ratio' in advantage
    assert 'unique_gaps_ratio' in advantage


def test_simple_golomb_construction():
    """Test simple Golomb ruler construction fallback."""
    golomb_gen = GolombGenerators()
    
    # Test known small rulers
    ruler1 = golomb_gen._simple_golomb_construction(1)
    assert ruler1 == [0]
    
    ruler2 = golomb_gen._simple_golomb_construction(2)
    assert ruler2 == [0, 1]
    
    ruler3 = golomb_gen._simple_golomb_construction(3)
    assert ruler3 == [0, 1, 3]
    
    # Test larger construction
    ruler5 = golomb_gen._simple_golomb_construction(5)
    assert len(ruler5) == 5
    assert ruler5[0] == 0
    assert ruler5 == sorted(ruler5)


def test_optimal_configuration_search():
    """Test optimal configuration search."""
    golomb_gen = GolombGenerators()
    
    # Test small search space
    optimal = golomb_gen.find_optimal_golomb_configuration(max_dimension=3, max_generators=2)
    
    assert 'best_configuration' in optimal
    assert 'all_results' in optimal
    assert 'total_configurations_tested' in optimal
    
    best = optimal['best_configuration']
    assert best is not None
    assert 'dimension' in best
    assert 'n_generators' in best
    assert 'spectrum_size' in best
    
    # Should test dimensions 2-3 with generators 1-2 = 2x2 = 4 configurations
    assert optimal['total_configurations_tested'] == 4


if __name__ == "__main__":
    test_golomb_ruler_generation()
    print("✓ Golomb ruler generation test passed")
    
    test_golomb_generator_creation()
    print("✓ Golomb generator creation test passed")
    
    test_hermitian_eigenvalue_construction()
    print("✓ Hermitian eigenvalue construction test passed")
    
    test_golomb_spectrum_analysis()
    print("✓ Golomb spectrum analysis test passed")
    
    test_golomb_vs_standard_comparison()
    print("✓ Golomb vs standard comparison test passed")
    
    test_simple_golomb_construction()
    print("✓ Simple Golomb construction test passed")
    
    test_optimal_configuration_search()
    print("✓ Optimal configuration search test passed")
    
    print("\nAll Golomb generators tests passed!")