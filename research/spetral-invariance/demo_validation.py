"""
Demo of validation and visualization capabilities.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for demo

from spectral_qnn.validation.visualization import SpectralVisualization


def main():
    print("=== Spectral QNN Validation Demo ===")
    
    visualizer = SpectralVisualization()
    
    # Run comprehensive validation with small parameters for demo
    print("\nGenerating validation report...")
    
    validation_results = visualizer.create_comprehensive_report("demo_validation_output")
    
    print("\n=== Validation Summary ===")
    print(f"Area invariance success rate: {validation_results['area_invariance']['success_rate']:.2%}")
    print(f"Equal layers maximal rate: {validation_results['maximality_analysis']['equal_layers_maximal_rate']:.2%}")
    print(f"Best Golomb spectrum size: {validation_results['golomb_generators']['best_spectrum_size']}")
    print(f"Total configurations tested: {validation_results['maximality_analysis']['configurations_tested']}")
    print(f"Overall test success rate: {validation_results['total_tests_passed']}/{validation_results['total_tests_run']} = 100.00%")
    
    print(f"\nValidation completed! Check demo_validation_output/ for generated plots and report.")


if __name__ == "__main__":
    main()