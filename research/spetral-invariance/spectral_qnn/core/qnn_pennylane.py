"""
Basic Quantum Neural Network implementation using PennyLane

Implements the QNN structure from the paper:
f(x) = ⟨0|U†(x,θ)MU(x,θ)|0⟩

Where U(x,θ) consists of alternating data encoding S_l(x) and parameter layers W_l(θ)
"""

import pennylane as qml
import numpy as np
from typing import List, Optional, Callable


class QuantumNeuralNetwork:
    """
    Basic QNN implementation following the paper's definition.
    
    Supports both parallel and sequential ansätze for multivariate inputs.
    """
    
    def __init__(self, n_qubits: int, n_layers: int, ansatz_type: str = "parallel"):
        """
        Initialize QNN structure.
        
        Args:
            n_qubits: Number of qubits (R in paper)
            n_layers: Number of layers (L in paper) 
            ansatz_type: "parallel" or "sequential"
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.ansatz_type = ansatz_type
        self.device = qml.device('default.qubit', wires=n_qubits)
        
        # Initialize parameters randomly
        self.n_params = self._count_parameters()
        self.params = np.random.normal(0, 0.1, self.n_params)
    
    def _count_parameters(self) -> int:
        """Count total parameters needed for the circuit."""
        # Each layer has rotation parameters for each qubit
        return (self.n_layers + 1) * self.n_qubits * 3  # 3 Pauli rotations per qubit
    
    def data_encoding_layer(self, x: float, generators: List[np.ndarray], layer_idx: int):
        """
        Data encoding layer S_l(x) = exp(-ix H_l).
        
        Args:
            x: Input data point
            generators: List of Hermitian generators H_l for each qubit
            layer_idx: Layer index
        """
        for qubit in range(self.n_qubits):
            # For now, use simple Pauli-Z encoding: exp(-ix σ_z/2)
            qml.RZ(-x, wires=qubit)
    
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
                self.data_encoding_layer(x, [], layer)
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


if __name__ == "__main__":
    # Quick test
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=2)
    result = qnn.forward(0.5)
    print(f"QNN output for x=0.5: {result:.4f}")
    print(f"QNN shape (R, L): {qnn.get_shape()}")