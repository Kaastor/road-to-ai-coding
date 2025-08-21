"""
Demo of Golomb ruler based generators for arbitrary dimensions.
"""

from spectral_qnn.maximality.golomb_generators import GolombGenerators


def main():
    golomb_gen = GolombGenerators()
    
    print("=== Golomb Rulers Generators Demo ===")
    
    # Test Golomb ruler generation
    print("\n1. Golomb Ruler Generation:")
    for order in range(2, 6):
        ruler = golomb_gen.generate_golomb_ruler(order)
        print(f"   Order {order}: {ruler}")
    
    # Test generator creation and analysis
    print("\n2. Golomb-based Generator Analysis:")
    for dimension in [2, 3, 4]:
        generators = golomb_gen.create_golomb_based_generators(dimension, 3)
        analysis = golomb_gen.analyze_golomb_spectrum(generators)
        print(f"   Dimension {dimension}: Spectrum size = {analysis['spectrum_size']}, Generators = {analysis['generators_count']}")
        print(f"                       Gaps: min={analysis['min_gap']:.2f}, max={analysis['max_gap']:.2f}, unique={analysis['unique_gaps']}")
    
    # Comparison with standard approaches
    print("\n3. Golomb vs Standard Comparison:")
    for dimension in [2, 3]:
        comparison = golomb_gen.compare_golomb_vs_standard(dimension=dimension, n_generators=3)
        golomb_size = comparison['golomb_results']['spectrum_size']
        standard_size = comparison['standard_results']['spectrum_size']
        ratio = comparison['golomb_advantage']['spectrum_size_ratio']
        print(f"   Dimension {dimension}: Golomb={golomb_size}, Standard={standard_size}, Ratio={ratio:.2f}")
    
    # Find optimal configuration
    print("\n4. Optimal Configuration Search:")
    optimal = golomb_gen.find_optimal_golomb_configuration(max_dimension=4, max_generators=3)
    best = optimal['best_configuration']
    print(f"   Best Configuration: Dimension={best['dimension']}, Generators={best['n_generators']}")
    print(f"   Spectrum Size: {best['spectrum_size']}")
    print(f"   Configurations Tested: {optimal['total_configurations_tested']}")
    
    print("\nGolomb generators demo completed!")


if __name__ == "__main__":
    main()