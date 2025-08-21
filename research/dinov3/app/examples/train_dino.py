"""
Main Training Script for DINOv3 Self-Supervised Learning

This script provides a complete example of how to train a DINO model
from scratch. It demonstrates all the key concepts of self-supervised
learning with vision transformers.

Usage Examples:

# Quick test with synthetic data (for development/testing)
python train_dino.py --dataset synthetic --epochs 5 --batch-size 16

# Train on CIFAR-10 (good for educational purposes)  
python train_dino.py --dataset cifar10 --epochs 50 --batch-size 64

# Custom configuration with different model size
python train_dino.py --dataset cifar10 --embed-dim 256 --depth 6 --epochs 100

Key Learning Points:
1. Self-supervised learning requires no labels during training
2. Multi-crop augmentation is crucial for learning robust features
3. Teacher-student framework enables knowledge distillation
4. Exponential moving average updates create stable teacher
5. Feature quality can be evaluated via k-NN classification
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Add project root to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

import torch
import torch.nn.functional as F
import numpy as np

from dinov3.models.dino import create_dino_model
from dinov3.data.dataset import (
    create_cifar10_dino_dataset, 
    create_synthetic_dataset,
    create_dino_dataloader
)
from dinov3.training.trainer import create_trainer
from dinov3.utils.visualization import create_comprehensive_analysis


def get_args_parser():
    """Create argument parser for training configuration."""
    parser = argparse.ArgumentParser(
        'DINOv3 Training', 
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Model parameters
    model_group = parser.add_argument_group('Model parameters')
    model_group.add_argument('--img-size', default=224, type=int,
                           help='Input image size')
    model_group.add_argument('--patch-size', default=16, type=int,
                           help='Patch size for Vision Transformer')
    model_group.add_argument('--embed-dim', default=192, type=int,
                           help='Embedding dimension')
    model_group.add_argument('--depth', default=3, type=int,
                           help='Number of transformer layers')
    model_group.add_argument('--num-heads', default=3, type=int,
                           help='Number of attention heads')
    model_group.add_argument('--out-dim', default=8192, type=int,
                           help='Output dimension of projection head')
    
    # Training parameters
    train_group = parser.add_argument_group('Training parameters')
    train_group.add_argument('--epochs', default=100, type=int,
                           help='Number of training epochs')
    train_group.add_argument('--batch-size', default=32, type=int,
                           help='Batch size per GPU')
    train_group.add_argument('--lr', default=0.0005, type=float,
                           help='Base learning rate')
    train_group.add_argument('--weight-decay', default=0.04, type=float,
                           help='Weight decay')
    train_group.add_argument('--warmup-epochs', default=10, type=int,
                           help='Number of warmup epochs')
    
    # DINO specific parameters
    dino_group = parser.add_argument_group('DINO parameters')
    dino_group.add_argument('--teacher-temp', default=0.04, type=float,
                          help='Teacher temperature')
    dino_group.add_argument('--student-temp', default=0.1, type=float,
                          help='Student temperature')
    dino_group.add_argument('--teacher-momentum', default=0.996, type=float,
                          help='Base teacher momentum')
    dino_group.add_argument('--center-momentum', default=0.9, type=float,
                          help='Center momentum')
    
    # Data parameters
    data_group = parser.add_argument_group('Data parameters')
    data_group.add_argument('--dataset', default='cifar10', type=str,
                          choices=['cifar10', 'synthetic'],
                          help='Dataset to use')
    data_group.add_argument('--data-path', default='./data', type=str,
                          help='Path to dataset')
    data_group.add_argument('--num-workers', default=4, type=int,
                          help='Number of data loading workers')
    
    # Multi-crop parameters  
    crop_group = parser.add_argument_group('Multi-crop parameters')
    crop_group.add_argument('--global-crops-number', default=2, type=int,
                          help='Number of global crops')
    crop_group.add_argument('--local-crops-number', default=6, type=int,
                          help='Number of local crops')
    crop_group.add_argument('--global-crop-size', default=224, type=int,
                          help='Size of global crops')
    crop_group.add_argument('--local-crop-size', default=96, type=int,
                          help='Size of local crops')
    
    # Output and logging
    output_group = parser.add_argument_group('Output parameters')
    output_group.add_argument('--output-dir', default='./outputs', type=str,
                            help='Output directory')
    output_group.add_argument('--log-interval', default=50, type=int,
                            help='Steps between logging')
    output_group.add_argument('--save-interval', default=10, type=int,
                            help='Epochs between checkpoints')
    output_group.add_argument('--evaluate', action='store_true',
                            help='Run evaluation after training')
    output_group.add_argument('--analysis', action='store_true',
                            help='Create comprehensive analysis')
    
    # Miscellaneous
    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('--seed', default=42, type=int,
                          help='Random seed')
    misc_group.add_argument('--device', default='auto', type=str,
                          help='Device to use (auto, cuda, cpu)')
    misc_group.add_argument('--resume', default='', type=str,
                          help='Resume from checkpoint')
    misc_group.add_argument('--help', '-h', action='help',
                          help='Show this help message and exit')
    
    return parser


def setup_datasets(args):
    """
    Setup training and validation datasets.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        train_dataset, val_dataset: Dataset objects
    """
    print(f"Setting up {args.dataset} dataset...")
    
    if args.dataset == 'cifar10':
        # CIFAR-10 specific parameters (adjust for small 32x32 images)
        multicrop_kwargs = {
            'global_crop_size': 32,
            'local_crop_size': 16,
            'global_crops_number': args.global_crops_number,
            'local_crops_number': args.local_crops_number,
            'global_crops_scale': (0.6, 1.0),  # Less aggressive for small images
            'local_crops_scale': (0.2, 0.6)
        }
        
        train_dataset = create_cifar10_dino_dataset(
            data_dir=args.data_path,
            train=True,
            download=True,
            **multicrop_kwargs
        )
        
        val_dataset = create_cifar10_dino_dataset(
            data_dir=args.data_path,
            train=False,
            download=True,
            **multicrop_kwargs
        )
        
    elif args.dataset == 'synthetic':
        # Synthetic dataset for quick testing
        multicrop_kwargs = {
            'global_crop_size': args.global_crop_size,
            'local_crop_size': args.local_crop_size,
            'global_crops_number': args.global_crops_number,
            'local_crops_number': args.local_crops_number
        }
        
        train_dataset = create_synthetic_dataset(
            num_samples=1000,
            image_size=args.img_size,
            num_classes=10,
            **multicrop_kwargs
        )
        
        val_dataset = create_synthetic_dataset(
            num_samples=200,
            image_size=args.img_size,
            num_classes=10,
            **multicrop_kwargs
        )
    
    else:
        raise ValueError(f"Unknown dataset: {args.dataset}")
    
    print(f"Train dataset size: {len(train_dataset)}")
    print(f"Val dataset size: {len(val_dataset)}")
    
    return train_dataset, val_dataset


def main():
    """Main training function."""
    # Parse arguments
    parser = get_args_parser()
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config_path = output_dir / 'config.txt'
    with open(config_path, 'w') as f:
        for arg, value in sorted(vars(args).items()):
            f.write(f"{arg}: {value}\n")
    
    print("="*50)
    print("DINOv3 Self-Supervised Learning Training")
    print("="*50)
    print(f"Output directory: {output_dir}")
    print(f"Configuration saved to: {config_path}")
    
    # Setup device
    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)
    print(f"Using device: {device}")
    
    # Setup datasets
    train_dataset, val_dataset = setup_datasets(args)
    
    # Create model
    print("\nCreating DINO model...")
    model = create_dino_model(
        img_size=args.img_size,
        patch_size=args.patch_size,
        embed_dim=args.embed_dim,
        depth=args.depth,
        num_heads=args.num_heads,
        out_dim=args.out_dim,
        teacher_temp=args.teacher_temp,
        student_temp=args.student_temp,
        center_momentum=args.center_momentum,
        teacher_momentum=args.teacher_momentum
    )
    
    # Print model information
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Model size: {total_params * 4 / 1024 / 1024:.2f} MB (fp32)")
    
    # Create trainer
    print("\nSetting up trainer...")
    trainer = create_trainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        lr=args.lr,
        weight_decay=args.weight_decay,
        epochs=args.epochs,
        warmup_epochs=args.warmup_epochs,
        output_dir=str(output_dir),
        device=str(device),
        log_interval=args.log_interval,
        save_interval=args.save_interval
    )
    
    # Training
    print("\n" + "="*50)
    print("Starting Training")
    print("="*50)
    
    start_time = time.time()
    
    try:
        trainer.train(resume_from=args.resume if args.resume else None)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    except Exception as e:
        print(f"\nTraining failed: {e}")
        raise
    
    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    
    # Evaluation
    if args.evaluate:
        print("\n" + "="*50)
        print("Running Evaluation")
        print("="*50)
        
        # k-NN evaluation
        print("Evaluating with k-NN classifier...")
        train_loader = create_dino_dataloader(
            train_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers
        )
        val_loader = create_dino_dataloader(
            val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers
        )
        
        knn_accuracy = trainer.evaluate_knn(
            train_loader, val_loader, k=20, max_train_samples=2000
        )
        print(f"k-NN accuracy: {knn_accuracy:.4f}")
        
        # Save evaluation results
        eval_results = {
            'knn_accuracy': knn_accuracy,
            'training_time': total_time,
            'final_loss': trainer.training_history['loss'][-1] if trainer.training_history['loss'] else None
        }
        
        import json
        with open(output_dir / 'evaluation_results.json', 'w') as f:
            json.dump(eval_results, f, indent=2)
    
    # Comprehensive analysis
    if args.analysis:
        print("\n" + "="*50)
        print("Creating Comprehensive Analysis")
        print("="*50)
        
        analysis_dir = output_dir / 'analysis'
        
        # Get class names
        class_names = None
        if args.dataset == 'cifar10':
            class_names = [
                'airplane', 'automobile', 'bird', 'cat', 'deer',
                'dog', 'frog', 'horse', 'ship', 'truck'
            ]
        
        # Create analysis
        val_loader = create_dino_dataloader(
            val_dataset, batch_size=16, shuffle=False, num_workers=args.num_workers
        )
        
        create_comprehensive_analysis(
            model=model,
            test_dataloader=val_loader,
            output_dir=str(analysis_dir),
            max_samples=500,
            class_names=class_names
        )
    
    print(f"\nAll outputs saved to: {output_dir}")
    print("Training complete! 🎉")
    
    # Print some educational insights
    print("\n" + "="*50)
    print("Educational Insights")
    print("="*50)
    print("Key concepts demonstrated:")
    print("1. Self-supervised learning: No labels were used during training")
    print("2. Multi-crop augmentation: Model learned from different views")
    print("3. Teacher-student distillation: Knowledge transfer without supervision")
    print("4. Feature quality: Can be evaluated via k-NN classification")
    print("5. Attention patterns: Model learns to focus on relevant regions")
    print("\nNext steps:")
    print("- Examine attention maps to see what the model focuses on")
    print("- Analyze feature clustering with t-SNE visualizations")
    print("- Try different architectures or datasets")
    print("- Use learned features for downstream tasks")


if __name__ == '__main__':
    main()