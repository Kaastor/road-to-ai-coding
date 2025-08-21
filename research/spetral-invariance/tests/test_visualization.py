"""
Tests for visualization and validation suite.
"""

import os
import tempfile
from spectral_qnn.validation.visualization import SpectralVisualization


def test_visualization_initialization():
    """Test visualization suite initialization."""
    visualizer = SpectralVisualization()
    
    assert visualizer.analyzer is not None
    assert visualizer.maximality_analyzer is not None
    assert visualizer.golomb_generator is not None


def test_comprehensive_report_generation():
    """Test comprehensive validation report generation."""
    visualizer = SpectralVisualization()
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        validation_results = visualizer.create_comprehensive_report(temp_dir)
        
        # Check that files were created
        assert os.path.exists(f"{temp_dir}/area_invariance.png")
        assert os.path.exists(f"{temp_dir}/golomb_comparison.png")
        assert os.path.exists(f"{temp_dir}/validation_summary.txt")
        
        # Check validation results structure
        assert 'area_invariance' in validation_results
        assert 'maximality_analysis' in validation_results
        assert 'golomb_generators' in validation_results
        assert 'total_tests_run' in validation_results
        assert 'total_tests_passed' in validation_results
        
        # Check area invariance results
        area_inv = validation_results['area_invariance']
        assert 'tests_run' in area_inv
        assert 'tests_passed' in area_inv
        assert 'success_rate' in area_inv
        assert 0 <= area_inv['success_rate'] <= 1
        
        # Check maximality analysis results
        max_analysis = validation_results['maximality_analysis']
        assert 'configurations_tested' in max_analysis
        assert 'equal_layers_maximal_rate' in max_analysis
        assert 'arbitrary_improvement_rate' in max_analysis
        assert isinstance(max_analysis['configurations_tested'], int)
        assert max_analysis['configurations_tested'] > 0
        
        # Check Golomb generators results
        golomb_res = validation_results['golomb_generators']
        assert 'configurations_tested' in golomb_res
        assert 'best_spectrum_size' in golomb_res
        assert 'best_dimension' in golomb_res
        assert 'best_generators' in golomb_res
        assert isinstance(golomb_res['best_spectrum_size'], int)
        assert golomb_res['best_spectrum_size'] > 0


def test_validation_report_content():
    """Test that validation report contains expected content."""
    visualizer = SpectralVisualization()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        validation_results = visualizer.create_comprehensive_report(temp_dir)
        
        # Read and check report file content
        report_file = f"{temp_dir}/validation_summary.txt"
        with open(report_file, 'r') as f:
            content = f.read()
        
        # Check for expected sections
        assert "SPECTRAL QNN VALIDATION REPORT" in content
        assert "Area Invariance Testing:" in content
        assert "Maximality Analysis:" in content
        assert "Golomb Generators:" in content
        assert "Overall Testing:" in content
        
        # Check for key metrics
        assert "Success Rate:" in content
        assert "Tests Run:" in content
        assert "Tests Passed:" in content
        assert "Best Spectrum Size:" in content


if __name__ == "__main__":
    test_visualization_initialization()
    print("✓ Visualization initialization test passed")
    
    test_comprehensive_report_generation()
    print("✓ Comprehensive report generation test passed")
    
    test_validation_report_content()
    print("✓ Validation report content test passed")
    
    print("\nAll visualization tests passed!")