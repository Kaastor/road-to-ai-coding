"""
Tests for 2D sub-generator maximality analysis.
"""

import numpy as np
from spectral_qnn.maximality.two_dim_analysis import TwoDimMaximalityAnalyzer


def test_equal_layers_spectrum_size():
    """Test theoretical spectrum size calculation for equal layers."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test case from paper: R=2, L=2 should give (2*2+1)^2 - 1 = 25 - 1 = 24
    size = analyzer.compute_equal_layers_spectrum_size(n_qubits=2, n_layers=2)
    expected = (2 * 2 + 1)**2 - 1  # 5^2 - 1 = 24
    assert size == expected
    
    # Test R=3, L=1: (2*1+1)^3 - 1 = 3^3 - 1 = 26
    size = analyzer.compute_equal_layers_spectrum_size(n_qubits=3, n_layers=1)
    expected = (2 * 1 + 1)**3 - 1  # 3^3 - 1 = 26
    assert size == expected


def test_equal_layers_maximality_verification():
    """Test equal layers maximality verification."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test small case R=2, L=1
    result = analyzer.verify_equal_layers_maximality(n_qubits=2, n_layers=1)
    
    assert result['n_qubits'] == 2
    assert result['n_layers'] == 1
    assert result['theoretical_max_size'] == 8  # (2*1+1)^2 - 1 = 8
    assert result['scaling_base'] == 3  # 2*1+1
    assert result['scaling_factors'] == [1, 3]  # 3^0, 3^1
    assert isinstance(result['actual_spectrum_size'], int)
    assert isinstance(result['is_maximal'], bool)


def test_scaling_factor_generation():
    """Test scaling factor generation methods."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test Fibonacci scaling
    fib_scaling = analyzer._fibonacci_scaling(5)
    expected_fib = [1, 1, 2, 3, 5]
    assert fib_scaling == expected_fib
    
    # Test prime scaling
    prime_scaling = analyzer._prime_scaling(5)
    expected_primes = [2, 3, 5, 7, 11]
    assert prime_scaling == expected_primes


def test_arbitrary_encoding_optimization():
    """Test arbitrary encoding optimization."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test small case R=2, L=1
    result = analyzer.find_arbitrary_encoding_optimum(n_qubits=2, n_layers=1)
    
    assert 'best_spectrum_size' in result
    assert 'best_scaling_factors' in result
    assert 'equal_layers_size' in result
    assert 'improvement_over_equal' in result
    assert 'is_better_than_equal' in result
    
    assert isinstance(result['best_spectrum_size'], int)
    assert result['best_spectrum_size'] > 0


def test_comprehensive_maximality_analysis():
    """Test comprehensive maximality analysis."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test small configuration space
    results = analyzer.analyze_maximality_conditions(max_qubits=2, max_layers=2)
    
    assert 'equal_layers_results' in results
    assert 'arbitrary_encoding_results' in results
    assert 'summary_statistics' in results
    
    stats = results['summary_statistics']
    assert 'total_configurations' in stats
    assert 'equal_layers_maximal_count' in stats
    assert 'equal_layers_maximal_rate' in stats
    assert 'arbitrary_improvements' in stats
    assert 'arbitrary_improvement_rate' in stats
    
    # Should have analyzed 2x2 = 4 configurations
    assert stats['total_configurations'] == 4
    assert 0 <= stats['equal_layers_maximal_rate'] <= 1
    assert 0 <= stats['arbitrary_improvement_rate'] <= 1


def test_scaling_factor_evaluation():
    """Test scaling factor evaluation method."""
    analyzer = TwoDimMaximalityAnalyzer()
    
    # Test with simple scaling factors
    scaling_factors = [1, 2]
    spectrum_size, spectrum = analyzer._evaluate_scaling_factors(
        scaling_factors, n_qubits=2, n_layers=1
    )
    
    assert isinstance(spectrum_size, int)
    assert spectrum_size > 0
    assert isinstance(spectrum, set)
    assert len(spectrum) == spectrum_size


if __name__ == "__main__":
    test_equal_layers_spectrum_size()
    print("✓ Equal layers spectrum size test passed")
    
    test_equal_layers_maximality_verification()
    print("✓ Equal layers maximality verification test passed")
    
    test_scaling_factor_generation()
    print("✓ Scaling factor generation test passed")
    
    test_arbitrary_encoding_optimization()
    print("✓ Arbitrary encoding optimization test passed")
    
    test_comprehensive_maximality_analysis()
    print("✓ Comprehensive maximality analysis test passed")
    
    test_scaling_factor_evaluation()
    print("✓ Scaling factor evaluation test passed")
    
    print("\nAll maximality tests passed!")