#!/usr/bin/env python3
"""
Example usage of QNN with R=1, L=2, sequential exponential encoding.

This demonstrates how generators are properly used in the quantum neural network
according to the paper's theoretical framework.
"""

import numpy as np
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spectral_qnn.core.qnn_pennylane import QuantumNeuralNetwork
from spectral_qnn.core.generators import HamiltonianGenerators
from spectral_qnn.core.frequency_analyzer import FrequencySpectrumAnalyzer


def main():
    print("=== QNN Example: R=1, L=2, Sequential Exponential Encoding ===")
    
    # Parameters
    R = 1  # 1 qubit
    L = 2  # 2 layers
    
    print(f"Configuration: R={R} qubits, L={L} layers")
    
    # 1. Create the QNN with sequential exponential encoding
    print("\n1. Creating QNN with sequential exponential encoding...")
    qnn = QuantumNeuralNetwork(
        n_qubits=R, 
        n_layers=L, 
        encoding_strategy="sequential_exponential"
    )
    
    print(f"   QNN created with shape: {qnn.get_shape()}")
    print(f"   Encoding strategy: {qnn.get_encoding_strategy()}")
    
    # 2. Examine the generators
    print("\n2. Examining the generators...")
    generators = qnn.get_generators()
    
    print(f"   Number of layers: {len(generators)}")
    for layer_idx, layer_gens in enumerate(generators):
        print(f"   Layer {layer_idx}: {len(layer_gens)} generators")
        for qubit_idx, gen in enumerate(layer_gens):
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            print(f"      Qubit {qubit_idx}: shape={gen.shape}, eigenvals={eigenvals}")
    
    # 3. Analyze the frequency spectrum
    print("\n3. Analyzing frequency spectrum...")
    analyzer = FrequencySpectrumAnalyzer()
    
    # Get eigenvalue differences for each generator
    all_eigenval_diffs = []
    for layer_idx, layer_gens in enumerate(generators):
        print(f"   Layer {layer_idx}:")
        for qubit_idx, gen in enumerate(layer_gens):
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            diffs = analyzer.compute_eigenvalue_differences(eigenvals)
            all_eigenval_diffs.append(diffs)
            print(f"      Qubit {qubit_idx}: eigenvals={eigenvals}, diffs={sorted(diffs)}")
    
    # Compute combined spectrum using Minkowski sums
    combined_spectrum = all_eigenval_diffs[0]
    for diffs in all_eigenval_diffs[1:]:
        combined_spectrum = analyzer.minkowski_sum(combined_spectrum, diffs)
    
    print(f"   Combined frequency spectrum: {sorted(combined_spectrum)}")
    print(f"   Spectrum size: {len(combined_spectrum)}")
    
    # 4. Test the QNN with different input values
    print("\n4. Testing QNN outputs...")
    test_inputs = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for x in test_inputs:
        output = qnn.forward(x)
        print(f"   f({x:4.2f}) = {output:8.4f}")
    
    # 5. Compare with other encoding strategies
    print("\n5. Comparing with other encoding strategies...")
    strategies = ["hamming", "ternary", "equal_maximal"]
    
    for strategy in strategies:
        try:
            qnn_comp = QuantumNeuralNetwork(R, L, encoding_strategy=strategy)
            output_comp = qnn_comp.forward(0.5)
            
            # Analyze spectrum
            gens_comp = qnn_comp.get_generators()
            spectrum_size = 0
            if gens_comp:
                all_diffs = []
                for layer_gens in gens_comp:
                    for gen in layer_gens:
                        eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
                        diffs = analyzer.compute_eigenvalue_differences(eigenvals)
                        all_diffs.append(diffs)
                
                if all_diffs:
                    combined = all_diffs[0]
                    for diffs in all_diffs[1:]:
                        combined = analyzer.minkowski_sum(combined, diffs)
                    spectrum_size = len(combined)
            
            print(f"   {strategy:15}: f(0.5)={output_comp:8.4f}, spectrum_size={spectrum_size}")
            
        except Exception as e:
            print(f"   {strategy:15}: Error - {e}")
    
    # 6. Theoretical verification
    print("\n6. Theoretical verification (Sequential Exponential)...")
    print("   According to the paper, sequential exponential encoding uses:")
    print("   β_l = 2^(l-1) for l < L, β_L = 2^(L-1) + 1")
    print(f"   For L={L}: β_1 = 2^0 = 1, β_2 = 2^1 + 1 = 3")
    
    # Verify our generators match this
    expected_betas = [1, 3]  # For L=2
    print("   Verifying generator scaling:")
    for layer_idx, layer_gens in enumerate(generators):
        for qubit_idx, gen in enumerate(layer_gens):
            # For Pauli-Z based generators, the scaling is in the eigenvalue difference
            eigenvals = HamiltonianGenerators.get_eigenvalues(gen)
            scale = abs(eigenvals[1] - eigenvals[0]) / 2.0  # Should be β/2
            expected_scale = expected_betas[layer_idx] / 2.0
            print(f"      Layer {layer_idx}, Qubit {qubit_idx}: scale={scale:.3f}, expected={expected_scale:.3f}")
    
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()