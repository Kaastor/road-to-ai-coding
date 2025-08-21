"""
QNN Training Demonstration

This script demonstrates training a Quantum Neural Network on a simple dataset
and visualizes the training progress with plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List
import pennylane as qml
from spectral_qnn.core.qnn_pennylane import QuantumNeuralNetwork


def generate_sine_dataset(n_samples: int = 100, noise_level: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a simple sine wave dataset for regression.
    
    Args:
        n_samples: Number of data points
        noise_level: Amount of noise to add
        
    Returns:
        (X, y) where X is input data and y is target values
    """
    X = np.linspace(-np.pi, np.pi, n_samples)
    y = np.sin(X) + noise_level * np.random.randn(n_samples)
    return X, y


def generate_binary_classification_dataset(n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a simple binary classification dataset.
    
    Args:
        n_samples: Number of data points
        
    Returns:
        (X, y) where X is input data and y is binary labels {-1, 1}
    """
    X = np.linspace(-2, 2, n_samples)
    # Simple decision boundary: positive if x > 0
    y = np.where(X > 0, 1, -1)
    # Add some noise around the boundary
    noise_mask = np.abs(X) < 0.5
    noise_indices = np.where(noise_mask)[0]
    for idx in noise_indices[::3]:  # Flip every 3rd point near boundary
        y[idx] = -y[idx]
    
    return X, y


def compute_loss(predictions: np.ndarray, targets: np.ndarray, loss_type: str = "mse") -> float:
    """
    Compute loss between predictions and targets.
    
    Args:
        predictions: Model predictions
        targets: Target values
        loss_type: "mse" for regression or "binary_crossentropy" for classification
        
    Returns:
        Loss value
    """
    if loss_type == "mse":
        return np.mean((predictions - targets) ** 2)
    elif loss_type == "binary_crossentropy":
        # For binary classification with outputs in [-1, 1]
        # Convert to probabilities and use log loss
        probs = (predictions + 1) / 2  # Map [-1,1] to [0,1]
        targets_prob = (targets + 1) / 2
        epsilon = 1e-15  # Prevent log(0)
        probs = np.clip(probs, epsilon, 1 - epsilon)
        return -np.mean(targets_prob * np.log(probs) + (1 - targets_prob) * np.log(1 - probs))
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")


def train_qnn(qnn: QuantumNeuralNetwork, X: np.ndarray, y: np.ndarray, 
              n_epochs: int = 50, learning_rate: float = 0.1, 
              loss_type: str = "mse") -> Tuple[List[float], List[np.ndarray]]:
    """
    Train the QNN using gradient descent.
    
    Args:
        qnn: Quantum Neural Network instance
        X: Input data
        y: Target values
        n_epochs: Number of training epochs
        learning_rate: Learning rate for optimization
        loss_type: Type of loss function
        
    Returns:
        (loss_history, predictions_history)
    """
    loss_history = []
    predictions_history = []
    
    # Convert parameters to PennyLane tensor with requires_grad=True
    params = qml.numpy.array(qnn.params, requires_grad=True)
    
    # Create a simplified QNode for training
    @qml.qnode(qnn.device, diff_method="parameter-shift")
    def qnode(x, params):
        # Simple trainable circuit
        for i in range(qnn.n_qubits):
            qml.RY(params[i], wires=i)
        for i in range(qnn.n_qubits):
            qml.RZ(x * params[qnn.n_qubits + i], wires=i)
        for i in range(qnn.n_qubits - 1):
            qml.CNOT(wires=[i, i + 1])
        for i in range(qnn.n_qubits):
            qml.RY(params[2 * qnn.n_qubits + i], wires=i)
        return qml.expval(qml.PauliZ(0))
    
    # Adjust parameter size for simplified circuit
    n_simple_params = 3 * qnn.n_qubits
    params = params[:n_simple_params] if len(params) >= n_simple_params else qml.numpy.random.normal(0, 0.1, n_simple_params, requires_grad=True)
    
    def cost_function(params):
        """Cost function for optimization."""
        predictions = qml.numpy.array([qnode(x, params) for x in X])
        if loss_type == "mse":
            return qml.numpy.mean((predictions - y) ** 2)
        else:
            # Simplified binary cross-entropy
            return qml.numpy.mean((predictions - y) ** 2)  # Use MSE for simplicity
    
    # Use PennyLane's optimizer
    opt = qml.GradientDescentOptimizer(stepsize=learning_rate)
    
    print("Starting QNN training...")
    print(f"Parameters shape: {params.shape}")
    print(f"Dataset size: {len(X)} samples")
    print(f"Loss type: {loss_type}")
    
    for epoch in range(n_epochs):
        # Compute predictions for visualization
        predictions = np.array([qnode(x, params) for x in X])
        loss = float(compute_loss(predictions, y, loss_type))
        
        loss_history.append(loss)
        predictions_history.append(predictions.copy())
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch:3d}: Loss = {loss:.6f}")
        
        # Update parameters using gradient descent
        params = opt.step(cost_function, params)
    
    final_loss = loss_history[-1]
    print(f"Training completed! Final loss: {final_loss:.6f}")
    
    return loss_history, predictions_history


def plot_training_results(X: np.ndarray, y: np.ndarray, loss_history: List[float], 
                         predictions_history: List[np.ndarray], task_type: str = "regression"):
    """
    Create comprehensive training visualization plots.
    
    Args:
        X: Input data
        y: Target values
        loss_history: Training loss over epochs
        predictions_history: Model predictions over epochs
        task_type: "regression" or "classification"
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('QNN Training Results', fontsize=16)
    
    # Plot 1: Training loss curve
    axes[0, 0].plot(loss_history, 'b-', linewidth=2, label='Training Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training Loss Curve')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    # Plot 2: Final predictions vs targets
    final_predictions = predictions_history[-1]
    axes[0, 1].scatter(X, y, alpha=0.6, label='Target', color='red', s=30)
    axes[0, 1].plot(X, final_predictions, 'b-', linewidth=2, label='QNN Prediction')
    axes[0, 1].set_xlabel('Input (x)')
    axes[0, 1].set_ylabel('Output')
    axes[0, 1].set_title('Final Predictions vs Targets')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Training evolution (every 10th epoch)
    epochs_to_show = list(range(0, len(predictions_history), max(1, len(predictions_history) // 5)))
    colors = plt.cm.viridis(np.linspace(0, 1, len(epochs_to_show)))
    
    for i, epoch in enumerate(epochs_to_show):
        alpha = 0.3 + 0.7 * (i / len(epochs_to_show))  # Increase opacity over time
        axes[1, 0].plot(X, predictions_history[epoch], color=colors[i], 
                       alpha=alpha, linewidth=1.5, label=f'Epoch {epoch}')
    
    axes[1, 0].scatter(X, y, alpha=0.6, color='red', s=20, label='Target', zorder=10)
    axes[1, 0].set_xlabel('Input (x)')
    axes[1, 0].set_ylabel('Output')
    axes[1, 0].set_title('Training Evolution')
    axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Loss improvement and prediction accuracy
    if task_type == "regression":
        # For regression: show R² score evolution
        r2_scores = []
        for preds in predictions_history:
            ss_res = np.sum((y - preds) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            r2_scores.append(r2)
        
        axes[1, 1].plot(r2_scores, 'g-', linewidth=2, label='R² Score')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('R² Score')
        axes[1, 1].set_title('Model Performance (R² Score)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
        
    else:  # classification
        # For classification: show accuracy evolution
        accuracies = []
        for preds in predictions_history:
            pred_labels = np.sign(preds)
            accuracy = np.mean(pred_labels == y)
            accuracies.append(accuracy)
        
        axes[1, 1].plot(accuracies, 'g-', linewidth=2, label='Accuracy')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Accuracy')
        axes[1, 1].set_title('Classification Accuracy')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
    
    plt.tight_layout()
    return fig


def main():
    """Main training demonstration."""
    print("=== QNN Training Demonstration ===\n")
    
    # Create QNN
    qnn = QuantumNeuralNetwork(n_qubits=2, n_layers=3)
    print(f"Created QNN with shape: {qnn.get_shape()}")
    print(f"Number of parameters: {qnn.n_params}\n")
    
    # Demonstrate both regression and classification
    tasks = [
        ("regression", generate_sine_dataset, "mse"),
        ("classification", generate_binary_classification_dataset, "binary_crossentropy")
    ]
    
    for task_name, dataset_generator, loss_type in tasks:
        print(f"\n{'='*50}")
        print(f"Training QNN for {task_name.upper()} task")
        print(f"{'='*50}")
        
        # Generate dataset (smaller for demo)
        X, y = dataset_generator(n_samples=30)
        print(f"Generated dataset: {len(X)} samples")
        print(f"Input range: [{X.min():.2f}, {X.max():.2f}]")
        print(f"Target range: [{y.min():.2f}, {y.max():.2f}]")
        
        # Train the model (reduced epochs for demo)
        loss_history, predictions_history = train_qnn(
            qnn, X, y, 
            n_epochs=50, 
            learning_rate=0.1, 
            loss_type=loss_type
        )
        
        # Create visualization
        fig = plot_training_results(X, y, loss_history, predictions_history, task_name)
        plt.savefig(f'training_results_{task_name}.png', dpi=150, bbox_inches='tight')
        print(f"Training plots saved as 'training_results_{task_name}.png'")
        
        # Print final results
        final_predictions = predictions_history[-1]
        final_loss = loss_history[-1]
        
        if task_name == "regression":
            # Calculate R² score
            ss_res = np.sum((y - final_predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_score = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            print(f"Final R² score: {r2_score:.4f}")
        else:
            # Calculate accuracy
            pred_labels = np.sign(final_predictions)
            accuracy = np.mean(pred_labels == y)
            print(f"Final accuracy: {accuracy:.4f}")
        
        print(f"Final loss: {final_loss:.6f}")
        
        # Reset QNN parameters for next task
        qnn.params = np.random.normal(0, 0.1, qnn.n_params)


if __name__ == "__main__":
    main()