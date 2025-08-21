"""
Feature Analysis Demo for Trained DINOv3 Models

This script demonstrates how to analyze and visualize the features learned
by a trained DINO model. It provides various tools to understand what the
model has learned through self-supervised training.

Usage Examples:

# Analyze a trained model on test data
python analyze_features.py --model-path outputs/best_model.pth --dataset cifar10

# Extract and visualize attention maps
python analyze_features.py --model-path outputs/best_model.pth --attention-analysis

# Find similar images using learned features
python analyze_features.py --model-path outputs/best_model.pth --similarity-analysis

# Create comprehensive analysis report
python analyze_features.py --model-path outputs/best_model.pth --full-analysis

Key Insights Demonstrated:
1. Self-supervised features capture semantic similarity
2. Attention maps reveal what the model focuses on
3. Features cluster by visual similarity, not just class
4. Different attention heads capture different aspects
5. Learned representations are useful for various tasks
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json

from dinov3.models.dino import create_dino_model
from dinov3.data.dataset import (
    create_cifar10_dino_dataset,
    create_synthetic_dataset, 
    create_dino_dataloader
)
from dinov3.utils.visualization import (
    AttentionVisualizer,
    FeatureVisualizer, 
    create_comprehensive_analysis
)


def get_args_parser():
    """Create argument parser for analysis configuration."""
    parser = argparse.ArgumentParser(
        'DINOv3 Feature Analysis',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Model and data
    parser.add_argument('--model-path', required=True, type=str,
                       help='Path to trained model checkpoint')
    parser.add_argument('--dataset', default='cifar10', type=str,
                       choices=['cifar10', 'synthetic'],
                       help='Dataset to analyze')
    parser.add_argument('--data-path', default='./data', type=str,
                       help='Path to dataset')
    parser.add_argument('--output-dir', default='./analysis', type=str,
                       help='Output directory for analysis')
    
    # Analysis options
    parser.add_argument('--attention-analysis', action='store_true',
                       help='Run attention analysis')
    parser.add_argument('--feature-analysis', action='store_true',
                       help='Run feature analysis with t-SNE/PCA')
    parser.add_argument('--similarity-analysis', action='store_true',
                       help='Run similarity analysis')
    parser.add_argument('--full-analysis', action='store_true',
                       help='Run comprehensive analysis (all above)')
    
    # Parameters
    parser.add_argument('--num-samples', default=500, type=int,
                       help='Number of samples to analyze')
    parser.add_argument('--batch-size', default=32, type=int,
                       help='Batch size for analysis')
    parser.add_argument('--device', default='auto', type=str,
                       help='Device to use (auto, cuda, cpu)')
    parser.add_argument('--seed', default=42, type=int,
                       help='Random seed')
    
    # Specific analysis parameters
    parser.add_argument('--attention-layers', nargs='+', type=int, default=[-1],
                       help='Which attention layers to visualize')
    parser.add_argument('--tsne-perplexity', default=30, type=float,
                       help='t-SNE perplexity parameter')
    parser.add_argument('--num-neighbors', default=5, type=int,
                       help='Number of neighbors for similarity analysis')
    
    parser.add_argument('--help', '-h', action='help',
                       help='Show this help message and exit')
    
    return parser


def load_model_from_checkpoint(checkpoint_path: str, device: str = 'auto'):
    """
    Load trained DINO model from checkpoint.
    
    Args:
        checkpoint_path: Path to checkpoint file
        device: Device to load model on
        
    Returns:
        Loaded DINO model
    """
    if device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device)
    
    print(f"Loading model from {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Extract model configuration from state dict structure
    # This is a simplified approach - in practice you'd save config with model
    state_dict = checkpoint['model_state_dict']
    
    # Infer model parameters from state dict (basic approach)
    # In real implementation, save these with the checkpoint
    embed_dim = state_dict['student.backbone.patch_embed.projection.weight'].shape[0]
    
    # Count transformer blocks
    depth = len([k for k in state_dict.keys() if 'student.backbone.blocks' in k and 'norm1.weight' in k])
    
    # Count attention heads
    first_attn_weight = None
    for k, v in state_dict.items():
        if 'student.backbone.blocks.0.attn.qkv.weight' in k:
            first_attn_weight = v
            break
    
    if first_attn_weight is not None:
        num_heads = first_attn_weight.shape[0] // (3 * embed_dim)
    else:
        num_heads = 3  # Default
    
    # Get output dimension
    out_dim = state_dict['student.head.mlp.3.weight'].shape[0]
    
    print(f"Inferred model config:")
    print(f"  Embed dim: {embed_dim}")
    print(f"  Depth: {depth}")  
    print(f"  Num heads: {num_heads}")
    print(f"  Output dim: {out_dim}")
    
    # Create model with inferred config
    model = create_dino_model(
        img_size=224,  # Standard
        embed_dim=embed_dim,
        depth=depth,
        num_heads=num_heads,
        out_dim=out_dim
    )
    
    # Load state dict
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    
    print("Model loaded successfully!")
    return model


def run_attention_analysis(model, dataloader, output_dir: Path, attention_layers: List[int]):
    """
    Analyze and visualize attention patterns.
    
    Args:
        model: Trained DINO model
        dataloader: DataLoader with test images
        output_dir: Output directory
        attention_layers: Which layers to analyze
    """
    print("Running attention analysis...")
    
    attention_dir = output_dir / 'attention'
    attention_dir.mkdir(parents=True, exist_ok=True)
    
    visualizer = AttentionVisualizer(model)
    
    # Get some sample images
    crops_batch, labels_batch = next(iter(dataloader))
    
    # Analyze first few images
    num_samples = min(5, len(crops_batch[0]))
    
    for sample_idx in range(num_samples):
        print(f"Analyzing attention for sample {sample_idx}...")
        
        # Use first crop (global crop)
        image = crops_batch[0][sample_idx:sample_idx+1]
        label = labels_batch[sample_idx].item()
        
        for layer_idx in attention_layers:
            # Visualize attention for this layer
            save_path = attention_dir / f'sample_{sample_idx}_label_{label}_layer_{layer_idx}.png'
            visualizer.visualize_attention(
                image, 
                layer_idx=layer_idx,
                save_path=str(save_path)
            )
            
            # Compare attention heads
            save_path_heads = attention_dir / f'sample_{sample_idx}_label_{label}_layer_{layer_idx}_heads.png'
            visualizer.compare_attention_heads(
                image,
                layer_idx=layer_idx,
                save_path=str(save_path_heads)
            )
    
    print(f"Attention analysis saved to {attention_dir}")


def run_feature_analysis(model, dataloader, output_dir: Path, tsne_perplexity: float, max_samples: int):
    """
    Analyze learned feature representations.
    
    Args:
        model: Trained DINO model
        dataloader: DataLoader with test images
        output_dir: Output directory
        tsne_perplexity: t-SNE perplexity parameter
        max_samples: Maximum samples to analyze
    """
    print("Running feature analysis...")
    
    feature_dir = output_dir / 'features'
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    visualizer = FeatureVisualizer()
    
    # Extract features
    print("Extracting features...")
    features, labels = visualizer.extract_features(
        model, dataloader, max_samples=max_samples
    )
    
    print(f"Extracted {features.shape[0]} features of dimension {features.shape[1]}")
    
    # Compute and plot t-SNE
    try:
        print("Computing t-SNE...")
        tsne_embeddings = visualizer.compute_tsne(
            features, perplexity=tsne_perplexity
        )
        
        # Get class names if CIFAR-10
        class_names = None
        if hasattr(dataloader.dataset, 'base_dataset') and hasattr(dataloader.dataset.base_dataset, 'classes'):
            class_names = dataloader.dataset.base_dataset.classes
        
        visualizer.plot_feature_embedding(
            tsne_embeddings, labels, class_names,
            title="t-SNE of Learned Features",
            save_path=str(feature_dir / 'tsne_features.png')
        )
        
        print("Computing PCA...")
        pca_embeddings = visualizer.compute_pca(features)
        visualizer.plot_feature_embedding(
            pca_embeddings, labels, class_names,
            title="PCA of Learned Features", 
            save_path=str(feature_dir / 'pca_features.png')
        )
        
    except ImportError as e:
        print(f"Skipping dimensionality reduction: {e}")
    
    # Feature statistics
    feature_stats = {
        'num_samples': int(features.shape[0]),
        'feature_dim': int(features.shape[1]),
        'feature_mean': float(features.mean()),
        'feature_std': float(features.std()),
        'unique_labels': int(len(np.unique(labels)))
    }
    
    with open(feature_dir / 'feature_stats.json', 'w') as f:
        json.dump(feature_stats, f, indent=2)
    
    print(f"Feature analysis saved to {feature_dir}")
    return features, labels


def run_similarity_analysis(
    model, 
    dataloader, 
    features: np.ndarray,
    labels: np.ndarray,
    output_dir: Path,
    num_neighbors: int
):
    """
    Analyze feature similarities and find nearest neighbors.
    
    Args:
        model: Trained DINO model
        dataloader: DataLoader with test images  
        features: Extracted features
        labels: Corresponding labels
        output_dir: Output directory
        num_neighbors: Number of neighbors to find
    """
    print("Running similarity analysis...")
    
    similarity_dir = output_dir / 'similarity'
    similarity_dir.mkdir(parents=True, exist_ok=True)
    
    visualizer = FeatureVisualizer()
    visualizer.features = features
    visualizer.labels = labels
    
    # Get original images for visualization
    crops_batch, labels_batch = next(iter(dataloader))
    images = crops_batch[0]  # First crop
    
    # Analyze several query samples
    num_queries = min(5, len(images))
    
    for query_idx in range(num_queries):
        print(f"Finding neighbors for sample {query_idx}...")
        
        # Find nearest neighbors
        neighbor_indices = visualizer.find_nearest_neighbors(
            query_idx, k=num_neighbors
        )
        
        # Create visualization
        fig, axes = plt.subplots(2, num_neighbors + 1, figsize=(3*(num_neighbors+1), 6))
        
        # Denormalization for display
        mean = torch.tensor([0.485, 0.456, 0.406]).reshape(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).reshape(3, 1, 1)
        
        def denormalize_image(img_tensor):
            img = img_tensor * std + mean
            img = torch.clamp(img, 0, 1)
            return img.permute(1, 2, 0).numpy()
        
        # Query image
        query_img = denormalize_image(images[query_idx])
        axes[0, 0].imshow(query_img)
        axes[0, 0].set_title(f'Query\nLabel: {labels[query_idx]}')
        axes[0, 0].axis('off')
        
        # Show similarity score as bar
        axes[1, 0].bar([0], [1.0], color='blue')
        axes[1, 0].set_ylim(0, 1)
        axes[1, 0].set_title('Self\n(1.0)')
        axes[1, 0].set_xticks([])
        
        # Neighbor images
        for i, neighbor_idx in enumerate(neighbor_indices):
            if neighbor_idx < len(images):
                neighbor_img = denormalize_image(images[neighbor_idx])
                axes[0, i+1].imshow(neighbor_img)
                axes[0, i+1].set_title(f'Neighbor {i+1}\nLabel: {labels[neighbor_idx]}')
                axes[0, i+1].axis('off')
                
                # Compute similarity
                query_feat = features[query_idx:query_idx+1] 
                neighbor_feat = features[neighbor_idx:neighbor_idx+1]
                
                # Cosine similarity
                similarity = np.dot(query_feat, neighbor_feat.T) / (
                    np.linalg.norm(query_feat) * np.linalg.norm(neighbor_feat)
                )
                similarity = similarity[0, 0]
                
                # Show similarity as bar
                color = 'green' if labels[neighbor_idx] == labels[query_idx] else 'red'
                axes[1, i+1].bar([0], [similarity], color=color)
                axes[1, i+1].set_ylim(0, 1)
                axes[1, i+1].set_title(f'Sim: {similarity:.3f}')
                axes[1, i+1].set_xticks([])
        
        plt.tight_layout()
        plt.suptitle(f'Nearest Neighbors for Sample {query_idx}', y=1.02, fontsize=16)
        
        save_path = similarity_dir / f'neighbors_sample_{query_idx}.png'
        plt.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
    
    print(f"Similarity analysis saved to {similarity_dir}")


def analyze_feature_quality(features: np.ndarray, labels: np.ndarray) -> Dict:
    """
    Analyze the quality of learned features.
    
    Args:
        features: Extracted features
        labels: Ground truth labels
        
    Returns:
        Dictionary with quality metrics
    """
    print("Analyzing feature quality...")
    
    # Normalize features
    features_norm = features / np.linalg.norm(features, axis=1, keepdims=True)
    
    # Compute intra-class and inter-class similarities
    unique_labels = np.unique(labels)
    
    intra_class_sims = []
    inter_class_sims = []
    
    for label in unique_labels:
        label_mask = labels == label
        label_features = features_norm[label_mask]
        
        # Intra-class similarities (within same class)
        if len(label_features) > 1:
            similarities = np.dot(label_features, label_features.T)
            # Remove diagonal (self-similarities)
            similarities = similarities[~np.eye(len(similarities), dtype=bool)]
            intra_class_sims.extend(similarities)
        
        # Inter-class similarities (with other classes)
        other_mask = labels != label
        if np.any(other_mask):
            other_features = features_norm[other_mask]
            similarities = np.dot(label_features, other_features.T)
            inter_class_sims.extend(similarities.flatten())
    
    # Compute metrics
    intra_class_mean = np.mean(intra_class_sims) if intra_class_sims else 0
    inter_class_mean = np.mean(inter_class_sims) if inter_class_sims else 0
    
    # Silhouette-like score (higher is better)
    separation_score = intra_class_mean - inter_class_mean
    
    quality_metrics = {
        'intra_class_similarity': float(intra_class_mean),
        'inter_class_similarity': float(inter_class_mean), 
        'separation_score': float(separation_score),
        'num_classes': int(len(unique_labels)),
        'num_samples': int(len(features))
    }
    
    print(f"Feature Quality Metrics:")
    print(f"  Intra-class similarity: {intra_class_mean:.4f}")
    print(f"  Inter-class similarity: {inter_class_mean:.4f}")
    print(f"  Separation score: {separation_score:.4f}")
    
    return quality_metrics


def main():
    """Main analysis function."""
    parser = get_args_parser()
    args = parser.parse_args()
    
    # Set seed
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*50)
    print("DINOv3 Feature Analysis")
    print("="*50)
    print(f"Model: {args.model_path}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {output_dir}")
    
    # Load model
    model = load_model_from_checkpoint(args.model_path, args.device)
    
    # Setup dataset
    if args.dataset == 'cifar10':
        dataset = create_cifar10_dino_dataset(
            data_dir=args.data_path, train=False, download=True
        )
        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                      'dog', 'frog', 'horse', 'ship', 'truck']
    else:
        dataset = create_synthetic_dataset(num_samples=args.num_samples)
        class_names = None
    
    dataloader = create_dino_dataloader(
        dataset, batch_size=args.batch_size, shuffle=False, num_workers=2
    )
    
    # Determine which analyses to run
    run_attention = args.attention_analysis or args.full_analysis
    run_features = args.feature_analysis or args.full_analysis
    run_similarity = args.similarity_analysis or args.full_analysis
    
    features = None
    labels = None
    
    # Run analyses
    if run_attention:
        run_attention_analysis(model, dataloader, output_dir, args.attention_layers)
    
    if run_features or run_similarity:
        features, labels = run_feature_analysis(
            model, dataloader, output_dir, args.tsne_perplexity, args.num_samples
        )
        
        # Analyze feature quality
        quality_metrics = analyze_feature_quality(features, labels)
        
        with open(output_dir / 'quality_metrics.json', 'w') as f:
            json.dump(quality_metrics, f, indent=2)
    
    if run_similarity and features is not None:
        run_similarity_analysis(
            model, dataloader, features, labels, output_dir, args.num_neighbors
        )
    
    # Create summary report
    print("\n" + "="*50)
    print("Analysis Summary")
    print("="*50)
    
    if run_attention:
        print("✓ Attention analysis completed")
        print(f"  - Analyzed {len(args.attention_layers)} layer(s): {args.attention_layers}")
        print(f"  - Visualized attention patterns and head comparisons")
    
    if features is not None:
        print("✓ Feature analysis completed") 
        print(f"  - Extracted {features.shape[0]} features of dimension {features.shape[1]}")
        print(f"  - Created t-SNE and PCA visualizations")
        
        if 'quality_metrics' in locals():
            print(f"  - Separation score: {quality_metrics['separation_score']:.4f}")
    
    if run_similarity:
        print("✓ Similarity analysis completed")
        print(f"  - Found {args.num_neighbors} nearest neighbors for sample images")
        print(f"  - Created neighbor visualizations with similarity scores")
    
    print(f"\nAll results saved to: {output_dir}")
    print("\nKey insights:")
    print("- Attention maps show what the model focuses on")
    print("- Feature clustering reveals semantic understanding")
    print("- Similarity analysis demonstrates learned representations")
    print("- Self-supervised learning captures meaningful patterns!")


if __name__ == '__main__':
    main()