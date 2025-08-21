"""
Visualization and Analysis Tools for DINOv3

This module provides comprehensive visualization utilities to understand
how DINO learns visual representations. These tools are essential for
educational purposes and help interpret the self-supervised learning process.

Key Visualizations:
1. Attention maps: What the model focuses on in images
2. Feature t-SNE: How learned features cluster in 2D space
3. Training progress: Loss curves and learning dynamics  
4. Multi-crop views: Different augmented perspectives
5. Feature similarity: Nearest neighbors in feature space
6. Model architecture: Network structure visualization
"""

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import seaborn as sns
from typing import List, Tuple, Optional, Dict, Any, Union
from pathlib import Path
import json

# Try to import optional dependencies
try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: sklearn not available. Some visualizations may not work.")

try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False


class AttentionVisualizer:
    """
    Visualize attention maps from Vision Transformer.
    
    Attention maps reveal what parts of the image the model considers
    important for building representations.
    """
    
    def __init__(self, model, device: str = 'auto'):
        """
        Args:
            model: ViT model or DINO model with ViT backbone
            device: Device to run computations on
        """
        self.model = model
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model.to(self.device)
        self.model.eval()
    
    def get_attention_maps(
        self, 
        image: torch.Tensor, 
        layer_idx: int = -1,
        head_idx: Optional[int] = None
    ) -> torch.Tensor:
        """
        Extract attention maps from the model.
        
        Args:
            image: Input image [1, 3, H, W]
            layer_idx: Which transformer layer (-1 for last)
            head_idx: Which attention head (None for all heads)
            
        Returns:
            Attention maps [1, num_heads, num_patches+1, num_patches+1]
        """
        with torch.no_grad():
            image = image.to(self.device)
            
            # Get attention maps from ViT
            if hasattr(self.model, 'student_backbone'):
                # DINO model
                attention_maps = self.model.student_backbone.get_attention_maps(image, layer_idx)
            elif hasattr(self.model, 'get_attention_maps'):
                # Direct ViT model
                attention_maps = self.model.get_attention_maps(image, layer_idx)
            else:
                raise ValueError("Model does not support attention map extraction")
            
            if head_idx is not None:
                attention_maps = attention_maps[:, head_idx:head_idx+1]
            
            return attention_maps
    
    def visualize_attention(
        self,
        image: torch.Tensor,
        layer_idx: int = -1,
        head_idx: Optional[int] = None,
        patch_size: int = 16,
        save_path: Optional[str] = None,
        threshold: float = 0.6
    ):
        """
        Visualize attention maps overlaid on the original image.
        
        Args:
            image: Input image [1, 3, H, W]
            layer_idx: Which transformer layer to visualize
            head_idx: Which attention head (None for average)
            patch_size: Size of patches in ViT
            save_path: Optional path to save visualization
            threshold: Attention threshold for highlighting
        """
        # Get attention maps
        attention_maps = self.get_attention_maps(image, layer_idx, head_idx)
        
        # Extract attention from [CLS] token to patches
        cls_attention = attention_maps[0, :, 0, 1:]  # [num_heads, num_patches]
        
        if head_idx is None:
            # Average across heads
            cls_attention = cls_attention.mean(dim=0)  # [num_patches]
            title_suffix = "Average Heads"
        else:
            cls_attention = cls_attention[0]  # [num_patches]
            title_suffix = f"Head {head_idx}"
        
        # Reshape to spatial grid
        img_size = image.shape[-1]
        grid_size = img_size // patch_size
        attention_grid = cls_attention.reshape(grid_size, grid_size)
        
        # Create visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Original image
        img_display = self._prepare_image_for_display(image[0])
        axes[0].imshow(img_display)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Attention heatmap
        im = axes[1].imshow(attention_grid.cpu().numpy(), cmap='viridis')
        axes[1].set_title(f'Attention Map - Layer {layer_idx} ({title_suffix})')
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1])
        
        # Overlay
        axes[2].imshow(img_display)
        
        # Create attention overlay
        attention_resized = F.interpolate(
            attention_grid.unsqueeze(0).unsqueeze(0),
            size=(img_size, img_size),
            mode='bilinear'
        )[0, 0]
        
        # Apply threshold and create mask
        attention_mask = attention_resized > threshold
        overlay = axes[2].imshow(
            attention_resized.cpu().numpy(),
            cmap='Reds',
            alpha=0.6,
            vmin=0,
            vmax=1
        )
        
        axes[2].set_title(f'Attention Overlay (threshold={threshold})')
        axes[2].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            plt.close()
        else:
            plt.show()
    
    def compare_attention_heads(
        self,
        image: torch.Tensor,
        layer_idx: int = -1,
        save_path: Optional[str] = None
    ):
        """
        Compare attention patterns across different heads.
        
        Args:
            image: Input image [1, 3, H, W]
            layer_idx: Which transformer layer to visualize
            save_path: Optional path to save visualization
        """
        # Get attention maps
        attention_maps = self.get_attention_maps(image, layer_idx)
        num_heads = attention_maps.shape[1]
        
        # Extract [CLS] token attention to patches
        cls_attention = attention_maps[0, :, 0, 1:]  # [num_heads, num_patches]
        
        # Reshape to spatial grids
        img_size = image.shape[-1]
        patch_size = 16  # Assuming standard patch size
        grid_size = img_size // patch_size
        
        # Create subplots
        cols = min(4, num_heads)
        rows = (num_heads + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
        
        if rows == 1:
            axes = axes.reshape(1, -1)
        
        for head in range(num_heads):
            row, col = head // cols, head % cols
            
            attention_grid = cls_attention[head].reshape(grid_size, grid_size)
            
            im = axes[row, col].imshow(attention_grid.cpu().numpy(), cmap='viridis')
            axes[row, col].set_title(f'Head {head}')
            axes[row, col].axis('off')
            plt.colorbar(im, ax=axes[row, col])
        
        # Hide unused subplots
        for head in range(num_heads, rows * cols):
            row, col = head // cols, head % cols
            axes[row, col].axis('off')
        
        plt.tight_layout()
        plt.suptitle(f'Attention Heads Comparison - Layer {layer_idx}', y=1.02, fontsize=16)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            plt.close()
        else:
            plt.show()
    
    def _prepare_image_for_display(self, image_tensor: torch.Tensor) -> np.ndarray:
        """Convert tensor to displayable numpy array."""
        # Denormalize (assuming ImageNet normalization)
        mean = torch.tensor([0.485, 0.456, 0.406]).reshape(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).reshape(3, 1, 1)
        
        img = image_tensor.cpu() * std + mean
        img = torch.clamp(img, 0, 1)
        img = img.permute(1, 2, 0).numpy()
        
        return img


class FeatureVisualizer:
    """
    Visualize learned feature representations.
    
    This helps understand how the model clusters similar images
    and separates different categories in the feature space.
    """
    
    def __init__(self):
        self.embeddings_2d = None
        self.labels = None
        self.features = None
    
    def extract_features(
        self,
        model,
        dataloader,
        device: str = 'auto',
        max_samples: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract features from model for visualization.
        
        Args:
            model: Trained model
            dataloader: DataLoader with images
            device: Device to run on
            max_samples: Maximum samples to process
            
        Returns:
            features: Extracted features [N, D]
            labels: Corresponding labels [N]
        """
        if device == 'auto':
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            device = torch.device(device)
        
        model = model.to(device)
        model.eval()
        
        all_features = []
        all_labels = []
        
        with torch.no_grad():
            for i, (crops_batch, labels) in enumerate(dataloader):
                if max_samples and i * dataloader.batch_size >= max_samples:
                    break
                
                # Use first crop (global crop) for feature extraction
                images = crops_batch[0].to(device)
                
                # Extract features
                if hasattr(model, 'student_backbone'):
                    # DINO model
                    features = model.student_backbone.forward_features(images)
                    features = features[:, 0]  # [CLS] token
                elif hasattr(model, 'forward_features'):
                    # Direct ViT
                    features = model.forward_features(images)
                    features = features[:, 0]  # [CLS] token
                else:
                    # General model
                    features = model(images)
                
                all_features.append(features.cpu().numpy())
                all_labels.append(labels.numpy())
        
        features = np.concatenate(all_features, axis=0)
        labels = np.concatenate(all_labels, axis=0)
        
        self.features = features
        self.labels = labels
        
        return features, labels
    
    def compute_tsne(
        self,
        features: Optional[np.ndarray] = None,
        perplexity: float = 30,
        n_iter: int = 1000,
        random_state: int = 42
    ) -> np.ndarray:
        """
        Compute t-SNE embedding of features.
        
        Args:
            features: Feature vectors [N, D]
            perplexity: t-SNE perplexity parameter
            n_iter: Number of iterations
            random_state: Random seed
            
        Returns:
            2D embeddings [N, 2]
        """
        if not HAS_SKLEARN:
            raise ImportError("sklearn required for t-SNE")
        
        if features is None:
            features = self.features
        
        tsne = TSNE(
            n_components=2,
            perplexity=perplexity,
            n_iter=n_iter,
            random_state=random_state
        )
        
        embeddings_2d = tsne.fit_transform(features)
        self.embeddings_2d = embeddings_2d
        
        return embeddings_2d
    
    def compute_pca(
        self,
        features: Optional[np.ndarray] = None,
        n_components: int = 2
    ) -> np.ndarray:
        """
        Compute PCA embedding of features.
        
        Args:
            features: Feature vectors [N, D]
            n_components: Number of PCA components
            
        Returns:
            2D embeddings [N, 2]
        """
        if not HAS_SKLEARN:
            raise ImportError("sklearn required for PCA")
        
        if features is None:
            features = self.features
        
        pca = PCA(n_components=n_components)
        embeddings_2d = pca.fit_transform(features)
        self.embeddings_2d = embeddings_2d
        
        return embeddings_2d
    
    def plot_feature_embedding(
        self,
        embeddings_2d: Optional[np.ndarray] = None,
        labels: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None,
        title: str = "Feature Embedding",
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 8)
    ):
        """
        Plot 2D feature embedding with color-coded classes.
        
        Args:
            embeddings_2d: 2D embeddings [N, 2]
            labels: Class labels [N]
            class_names: Names for classes
            title: Plot title
            save_path: Optional save path
            figsize: Figure size
        """
        if embeddings_2d is None:
            embeddings_2d = self.embeddings_2d
        if labels is None:
            labels = self.labels
        
        plt.figure(figsize=figsize)
        
        # Create scatter plot
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        
        for i, label in enumerate(unique_labels):
            mask = labels == label
            label_name = class_names[label] if class_names else f'Class {label}'
            
            plt.scatter(
                embeddings_2d[mask, 0],
                embeddings_2d[mask, 1],
                c=[colors[i]],
                label=label_name,
                alpha=0.7,
                s=20
            )
        
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.title(title)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            plt.close()
        else:
            plt.show()
    
    def find_nearest_neighbors(
        self,
        query_idx: int,
        k: int = 5,
        features: Optional[np.ndarray] = None
    ) -> List[int]:
        """
        Find k nearest neighbors to a query sample.
        
        Args:
            query_idx: Index of query sample
            k: Number of neighbors to find
            features: Feature vectors [N, D]
            
        Returns:
            List of neighbor indices
        """
        if features is None:
            features = self.features
        
        # Compute cosine similarities
        query_feature = features[query_idx:query_idx+1]
        query_norm = np.linalg.norm(query_feature, axis=1, keepdims=True)
        features_norm = np.linalg.norm(features, axis=1, keepdims=True)
        
        similarities = np.dot(query_feature, features.T) / (query_norm * features_norm.T)
        
        # Get top-k (excluding query itself)
        neighbor_indices = np.argsort(similarities[0])[::-1][1:k+1]
        
        return neighbor_indices.tolist()


class TrainingVisualizer:
    """
    Visualize training progress and learning dynamics.
    """
    
    def __init__(self):
        pass
    
    def plot_training_curves(
        self,
        history: Dict[str, List],
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (15, 5)
    ):
        """
        Plot training curves (loss, learning rate, momentum).
        
        Args:
            history: Training history dictionary
            save_path: Optional save path
            figsize: Figure size
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        epochs = history['epoch']
        
        # Loss curve
        axes[0].plot(epochs, history['loss'], 'b-', linewidth=2)
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Training Loss')
        axes[0].grid(True, alpha=0.3)
        
        # Learning rate curve
        axes[1].plot(epochs, history['lr'], 'r-', linewidth=2)
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Learning Rate')
        axes[1].set_title('Learning Rate Schedule')
        axes[1].set_yscale('log')
        axes[1].grid(True, alpha=0.3)
        
        # Teacher momentum curve
        axes[2].plot(epochs, history['teacher_momentum'], 'g-', linewidth=2)
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('Teacher Momentum')
        axes[2].set_title('Teacher Momentum Schedule')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            plt.close()
        else:
            plt.show()
    
    def load_and_plot_history(
        self,
        history_path: str,
        save_path: Optional[str] = None
    ):
        """
        Load training history from JSON and plot.
        
        Args:
            history_path: Path to training history JSON
            save_path: Optional save path
        """
        with open(history_path, 'r') as f:
            history = json.load(f)
        
        self.plot_training_curves(history, save_path)


def create_comprehensive_analysis(
    model,
    test_dataloader,
    output_dir: str,
    max_samples: int = 1000,
    class_names: Optional[List[str]] = None
):
    """
    Create comprehensive analysis report with all visualizations.
    
    Args:
        model: Trained DINO model
        test_dataloader: Test data loader
        output_dir: Directory to save visualizations
        max_samples: Maximum samples to analyze
        class_names: Names for classes
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Creating comprehensive analysis...")
    
    # 1. Feature analysis
    print("Extracting and analyzing features...")
    feature_viz = FeatureVisualizer()
    features, labels = feature_viz.extract_features(
        model, test_dataloader, max_samples=max_samples
    )
    
    # t-SNE visualization
    if HAS_SKLEARN:
        print("Computing t-SNE...")
        tsne_embeddings = feature_viz.compute_tsne(features)
        feature_viz.plot_feature_embedding(
            tsne_embeddings, labels, class_names,
            title="t-SNE of Learned Features",
            save_path=str(output_path / "tsne_features.png")
        )
        
        # PCA visualization
        print("Computing PCA...")
        pca_embeddings = feature_viz.compute_pca(features)
        feature_viz.plot_feature_embedding(
            pca_embeddings, labels, class_names,
            title="PCA of Learned Features",
            save_path=str(output_path / "pca_features.png")
        )
    
    # 2. Attention visualization (sample images)
    print("Creating attention visualizations...")
    attention_viz = AttentionVisualizer(model)
    
    # Get a few sample images
    sample_crops, sample_labels = next(iter(test_dataloader))
    
    for i in range(min(3, len(sample_crops[0]))):
        image = sample_crops[0][i:i+1]  # First crop, single image
        
        # Visualize attention
        attention_viz.visualize_attention(
            image,
            save_path=str(output_path / f"attention_sample_{i}.png")
        )
        
        # Compare attention heads
        attention_viz.compare_attention_heads(
            image,
            save_path=str(output_path / f"attention_heads_sample_{i}.png")
        )
    
    print(f"Analysis complete! Results saved to {output_dir}")


if __name__ == "__main__":
    # Test visualization utilities
    print("Testing visualization utilities...")
    
    # Create dummy data for testing
    dummy_features = np.random.randn(100, 50)
    dummy_labels = np.random.randint(0, 5, 100)
    
    # Test feature visualization
    if HAS_SKLEARN:
        feature_viz = FeatureVisualizer()
        feature_viz.features = dummy_features
        feature_viz.labels = dummy_labels
        
        tsne_emb = feature_viz.compute_tsne(dummy_features)
        print(f"t-SNE embedding shape: {tsne_emb.shape}")
        
        # Test plotting (don't show, just create)
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        feature_viz.plot_feature_embedding(
            tsne_emb, dummy_labels,
            save_path="/tmp/test_tsne.png"
        )
        print("Feature visualization test completed")
    
    # Test training visualization
    dummy_history = {
        'epoch': list(range(10)),
        'loss': [1.0 - 0.1*i + 0.02*np.random.randn() for i in range(10)],
        'lr': [0.001 * (0.5 ** (i//3)) for i in range(10)],
        'teacher_momentum': [0.996 + 0.004*i/10 for i in range(10)]
    }
    
    training_viz = TrainingVisualizer()
    training_viz.plot_training_curves(dummy_history, save_path="/tmp/test_training.png")
    print("Training visualization test completed")
    
    print("All visualization tests passed!")