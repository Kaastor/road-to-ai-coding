"""
Demo of 2D sub-generator maximality analysis.
"""

from spectral_qnn.maximality.two_dim_analysis import TwoDimMaximalityAnalyzer


def main():
    analyzer = TwoDimMaximalityAnalyzer()
    
    print("=== 2D Sub-generator Maximality Analysis Demo ===")
    
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


if __name__ == "__main__":
    main()