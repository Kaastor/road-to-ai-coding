"""
Tests for frequency spectrum analyzer.
"""

import numpy as np
from spectral_qnn.core.frequency_analyzer import FrequencySpectrumAnalyzer


def test_eigenvalue_differences():
    """Test eigenvalue difference computation."""
    analyzer = FrequencySpectrumAnalyzer()
    
    # Test with Pauli-Z eigenvalues [1, -1]
    eigenvals = np.array([1.0, -1.0])
    differences = analyzer.compute_eigenvalue_differences(eigenvals)
    
    expected = {0.0, 2.0, -2.0}  # 1-1=0, 1-(-1)=2, (-1)-1=-2, (-1)-(-1)=0
    assert differences == expected


def test_minkowski_sum():
    """Test Minkowski sum computation."""
    analyzer = FrequencySpectrumAnalyzer()
    
    set1 = {0, 1, -1}
    set2 = {0, 2}
    result = analyzer.minkowski_sum(set1, set2)
    
    expected = {0, 1, -1, 2, 3, 1}  # All combinations
    expected = {0, 1, -1, 2, 3}  # Remove duplicates
    assert result == expected


def test_hamming_spectrum():
    """Test Hamming encoding spectrum calculation."""
    analyzer = FrequencySpectrumAnalyzer()
    
    # Test case from paper: R=2, L=1, Pauli-Z
    spectrum = analyzer.compute_hamming_spectrum(n_qubits=2, n_layers=1)
    expected = np.array([-4, -2, 0, 2, 4])  # 2 * Z_2
    
    assert np.array_equal(spectrum, expected)


def test_maximality_analysis():
    """Test spectrum maximality analysis."""
    analyzer = FrequencySpectrumAnalyzer()
    
    # Perfect spectrum Z_3 = {-3, -2, -1, 0, 1, 2, 3}
    perfect_spectrum = np.array([-3, -2, -1, 0, 1, 2, 3])
    analysis = analyzer.analyze_maximality(perfect_spectrum)
    
    assert analysis['size'] == 7
    assert analysis['max_k_in_spectrum'] == 3
    assert analysis['is_symmetric'] == True
    assert analysis['num_gaps'] == 0


def test_area_invariance():
    """Test area-preserving transformation invariance."""
    analyzer = FrequencySpectrumAnalyzer()
    
    # Same area shapes
    same_area_shapes = [(2, 2), (4, 1), (1, 4)]  # Area = 4
    assert analyzer.demonstrate_area_invariance(same_area_shapes)
    
    # Different area shapes
    diff_area_shapes = [(2, 2), (3, 2)]  # Area 4 vs 6
    assert not analyzer.demonstrate_area_invariance(diff_area_shapes)


if __name__ == "__main__":
    # Run tests
    test_eigenvalue_differences()
    print("✓ Eigenvalue differences test passed")
    
    test_minkowski_sum()
    print("✓ Minkowski sum test passed")
    
    test_hamming_spectrum()
    print("✓ Hamming spectrum test passed")
    
    test_maximality_analysis()
    print("✓ Maximality analysis test passed")
    
    test_area_invariance()
    print("✓ Area invariance test passed")
    
    print("\nAll frequency analyzer tests passed!")