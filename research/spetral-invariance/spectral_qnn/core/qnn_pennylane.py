"""
Basic Quantum Neural Network implementation using PennyLane

Implements the QNN structure from the paper:
f(x) = ⟨0|U†(x,θ)MU(x,θ)|0⟩

Where U(x,θ) consists of alternating data encoding S_l(x) and parameter layers W_l(θ)
"""

import pennylane as qml
import numpy as np
from typing import List, Optional, Callable
from scipy.linalg import expm
try:
    from .generators import HamiltonianGenerators
except ImportError:
    from generators import HamiltonianGenerators


class QuantumNeuralNetwork:
    """
    Basic QNN implementation following the paper's definition.
    
    Supports both parallel and sequential ansätze for multivariate inputs.
    """
    
    def __init__(self, n_qubits: int, n_layers: int, ansatz_type: str = "parallel", 
                 encoding_strategy: str = "sequential_exponential"):
        """
        Initialize QNN structure.
        
        Args:
            n_qubits: Number of qubits (R in paper)
            n_layers: Number of layers (L in paper) 
            ansatz_type: "parallel" or "sequential"
            encoding_strategy: Generator encoding strategy
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.ansatz_type = ansatz_type
        self.encoding_strategy = encoding_strategy
        self.device = qml.device('default.qubit', wires=n_qubits)
        
        # Generate the appropriate generators for this QNN
        self.generators = self._create_generators()
        
        # Initialize parameters randomly
        self.n_params = self._count_parameters()
        self.params = np.random.normal(0, 0.1, self.n_params)
    
    def _create_generators(self) -> List[List[np.ndarray]]:
        """
        Create generators based on the specified encoding strategy.
        
        Returns:
            List of layers, each containing generators for each qubit
        """
        if self.encoding_strategy == "hamming":
            return HamiltonianGenerators.hamming_encoding_generators(self.n_qubits, self.n_layers)
        elif self.encoding_strategy == "sequential_exponential":
            return HamiltonianGenerators.sequential_exponential_generators(self.n_qubits, self.n_layers)
        elif self.encoding_strategy == "ternary":
            return HamiltonianGenerators.ternary_encoding_generators(self.n_qubits, self.n_layers)
        elif self.encoding_strategy == "equal_maximal":
            return HamiltonianGenerators.equal_layers_maximal_generators(self.n_qubits, self.n_layers)
        else:
            raise ValueError(f"Unknown encoding strategy: {self.encoding_strategy}")
    
    def _count_parameters(self) -> int:
        """Count total parameters needed for the circuit."""
        # Each layer has rotation parameters for each qubit
        return (self.n_layers + 1) * self.n_qubits * 3  # 3 Pauli rotations per qubit
    
    def data_encoding_layer(self, x: float, layer_idx: int):
        """
        Data encoding layer S_l(x) = exp(-ix H_l).
        
        Args:
            x: Input data point
            layer_idx: Layer index
        """
        layer_generators = self.generators[layer_idx]
        
        for qubit in range(self.n_qubits):
            generator = layer_generators[qubit]
            
            # For 2x2 Pauli matrices, we can use direct rotation gates
            if generator.shape == (2, 2):
                self._apply_pauli_rotation(generator, x, qubit)
            else:
                # For larger matrices, we need to decompose or use QubitUnitary
                self._apply_general_unitary(generator, x, qubit)
    
    def _apply_pauli_rotation(self, generator: np.ndarray, x: float, qubit: int):
        """
        Apply rotation for Pauli-based generators using efficient PennyLane gates.
        
        Args:
            generator: 2x2 Hermitian generator matrix
            x: Input data point  
            qubit: Target qubit
        """
        # Check if it's a scaled Pauli-Z (most common case)
        pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        # Extract scaling factor by comparing with Pauli-Z pattern
        if np.allclose(generator.imag, 0):  # Real matrix
            real_gen = generator.real
            if np.allclose(real_gen[0, 1], 0) and np.allclose(real_gen[1, 0], 0):  # Diagonal
                scale = (real_gen[0, 0] - real_gen[1, 1]) / 2.0
                qml.RZ(-2 * x * scale, wires=qubit)
                return
        
        # Fallback: use general unitary
        self._apply_general_unitary(generator, x, qubit)
    
    def _apply_general_unitary(self, generator: np.ndarray, x: float, qubit: int):
        """
        Apply general unitary exp(-ix H) using matrix exponentiation.
        
        Args:
            generator: Hermitian generator matrix
            x: Input data point
            qubit: Target qubit
        """
        # Compute unitary: U = exp(-ix H)
        unitary = expm(-1j * x * generator)
        
        # Apply as QubitUnitary
        qml.QubitUnitary(unitary, wires=qubit)
    
    def parameter_layer(self, params: np.ndarray, layer_idx: int):
        """
        Parameter encoding layer W_l(θ).
        
        Args:
            params: Parameter array
            layer_idx: Layer index
        """
        start_idx = layer_idx * self.n_qubits * 3
        
        for qubit in range(self.n_qubits):
            param_idx = start_idx + qubit * 3
            qml.RX(params[param_idx], wires=qubit)
            qml.RY(params[param_idx + 1], wires=qubit)
            qml.RZ(params[param_idx + 2], wires=qubit)
            
        # Add entangling gates
        for qubit in range(self.n_qubits - 1):
            qml.CNOT(wires=[qubit, qubit + 1])
    
    def create_circuit(self, x: float, params: Optional[np.ndarray] = None) -> Callable:
        """
        Create the complete QNN circuit U(x,θ).
        
        Args:
            x: Input data point
            params: Circuit parameters (uses self.params if None)
            
        Returns:
            QNode function
        """
        if params is None:
            params = self.params
            
        @qml.qnode(self.device)
        def circuit():
            # Initial parameter layer
            self.parameter_layer(params, 0)
            
            # Alternating data encoding and parameter layers
            for layer in range(self.n_layers):
                self.data_encoding_layer(x, layer)
                self.parameter_layer(params, layer + 1)
            
            # Measurement - return expectation of Z on first qubit
            return qml.expval(qml.PauliZ(0))
        
        return circuit
    
    def forward(self, x: float, params: Optional[np.ndarray] = None) -> float:
        """
        Forward pass: compute f(x) = ⟨0|U†(x,θ)MU(x,θ)|0⟩.
        
        Args:
            x: Input value
            params: Circuit parameters
            
        Returns:
            QNN output value
        """
        circuit = self.create_circuit(x, params)
        return circuit()
    
    def get_shape(self) -> tuple:
        """Return the shape (R, L) of the QNN."""
        return (self.n_qubits, self.n_layers)
    
    def get_encoding_strategy(self) -> str:
        """Return the encoding strategy used."""
        return self.encoding_strategy
    
    def get_generators(self) -> List[List[np.ndarray]]:
        """Return the generators used in each layer."""
        return self.generators


if __name__ == "__main__":
    # Test different encoding strategies
    strategies = ["hamming", "sequential_exponential", "ternary", "equal_maximal"]
    
    print("=== QNN with Different Encoding Strategies ===")
    for strategy in strategies:
        print(f"\nTesting {strategy} encoding:")
        try:
            qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=2, encoding_strategy=strategy)
            result = qnn.forward(0.5)
            print(f"  QNN output for x=0.5: {result:.4f}")
            print(f"  QNN shape (R, L): {qnn.get_shape()}")
            print(f"  Generators shape: {len(qnn.generators)}x{len(qnn.generators[0])}")
        except Exception as e:
            print(f"  Error: {e}")