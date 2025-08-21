"""
DINO Training Loop and Logic

This module implements the complete training infrastructure for DINO
self-supervised learning. The training process orchestrates:

1. Forward pass through teacher-student networks
2. Loss computation with centering and temperature scaling  
3. Backward pass and parameter updates
4. Teacher momentum updates (EMA)
5. Learning rate scheduling
6. Logging and checkpointing

Key Training Principles:
- Student network learns from teacher's predictions
- Teacher updated via exponential moving average
- Multi-crop augmentation provides different views
- Centering prevents mode collapse
- Progressive teacher momentum scheduling
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import time
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

from ..models.dino import DINO
from ..data.dataset import DINODataset


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Setup logger for training."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class CosineScheduler:
    """
    Cosine learning rate scheduler with warmup.
    
    This scheduler is crucial for DINO training:
    1. Warmup phase: Gradual increase to base learning rate
    2. Cosine decay: Smooth decrease following cosine curve
    3. Final learning rate: Small non-zero value for stability
    """
    
    def __init__(
        self,
        base_lr: float,
        final_lr: float,
        total_epochs: int,
        warmup_epochs: int = 10,
        start_warmup_value: float = 0.0
    ):
        self.base_lr = base_lr
        self.final_lr = final_lr
        self.total_epochs = total_epochs
        self.warmup_epochs = warmup_epochs
        self.start_warmup_value = start_warmup_value
    
    def get_lr(self, epoch: int) -> float:
        """Get learning rate for given epoch."""
        if epoch < self.warmup_epochs:
            # Linear warmup
            return self.start_warmup_value + (self.base_lr - self.start_warmup_value) * epoch / self.warmup_epochs
        else:
            # Cosine decay
            progress = (epoch - self.warmup_epochs) / (self.total_epochs - self.warmup_epochs)
            return self.final_lr + 0.5 * (self.base_lr - self.final_lr) * (1 + np.cos(np.pi * progress))


class TeacherMomentumScheduler:
    """
    Teacher momentum scheduler for DINO.
    
    Gradually increases teacher momentum from base value to 1.0
    following a cosine schedule. This helps stabilize training.
    """
    
    def __init__(self, base_momentum: float = 0.996, total_epochs: int = 100):
        self.base_momentum = base_momentum
        self.total_epochs = total_epochs
    
    def get_momentum(self, epoch: int) -> float:
        """Get teacher momentum for given epoch."""
        progress = epoch / self.total_epochs
        return 1.0 - (1.0 - self.base_momentum) * 0.5 * (1 + np.cos(np.pi * progress))


class DINOTrainer:
    """
    Complete DINO training system.
    
    This class orchestrates the entire training process, handling:
    - Model setup and initialization
    - Optimizer and scheduler configuration
    - Training loop with loss computation
    - Teacher momentum updates
    - Logging and checkpointing
    - Evaluation and analysis
    """
    
    def __init__(
        self,
        model: DINO,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        lr: float = 0.0005,
        weight_decay: float = 0.04,
        batch_size: int = 32,
        epochs: int = 100,
        warmup_epochs: int = 10,
        output_dir: str = './outputs',
        device: str = 'auto',
        log_interval: int = 50,
        save_interval: int = 10
    ):
        """
        Initialize DINO trainer.
        
        Args:
            model: DINO model to train
            train_loader: Training data loader
            val_loader: Optional validation data loader
            lr: Base learning rate
            weight_decay: Weight decay for optimizer
            batch_size: Training batch size
            epochs: Total training epochs
            warmup_epochs: Warmup epochs for learning rate
            output_dir: Directory to save outputs
            device: Device to train on ('auto', 'cuda', or 'cpu')
            log_interval: Steps between logging
            save_interval: Epochs between checkpoints
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.epochs = epochs
        self.output_dir = Path(output_dir)
        self.log_interval = log_interval
        self.save_interval = save_interval
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model = self.model.to(self.device)
        
        # Setup optimizer (only student parameters are trained)
        self.optimizer = optim.AdamW(
            self.model.student.parameters(),
            lr=lr,
            weight_decay=weight_decay,
            betas=(0.9, 0.95)
        )
        
        # Setup schedulers
        self.lr_scheduler = CosineScheduler(
            base_lr=lr,
            final_lr=1e-6,
            total_epochs=epochs,
            warmup_epochs=warmup_epochs
        )
        
        self.momentum_scheduler = TeacherMomentumScheduler(
            base_momentum=0.996,
            total_epochs=epochs
        )
        
        # Setup logger
        self.logger = setup_logger(
            'dino_trainer',
            log_file=str(self.output_dir / 'training.log')
        )
        
        # Training state
        self.current_epoch = 0
        self.global_step = 0
        self.best_loss = float('inf')
        self.training_history = {
            'epoch': [],
            'loss': [],
            'lr': [],
            'teacher_momentum': []
        }
        
        self.logger.info(f"Trainer initialized:")
        self.logger.info(f"  Device: {self.device}")
        self.logger.info(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        self.logger.info(f"  Training samples: {len(train_loader.dataset)}")
        self.logger.info(f"  Batch size: {batch_size}")
        self.logger.info(f"  Total epochs: {epochs}")
    
    def train_epoch(self) -> Dict[str, float]:
        """
        Train for one epoch.
        
        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        total_loss = 0.0
        num_batches = len(self.train_loader)
        
        # Update learning rate for this epoch
        current_lr = self.lr_scheduler.get_lr(self.current_epoch)
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = current_lr
        
        # Update teacher momentum for this epoch
        teacher_momentum = self.momentum_scheduler.get_momentum(self.current_epoch)
        self.model.teacher_momentum = teacher_momentum
        
        start_time = time.time()
        
        for batch_idx, (crops_batch, _) in enumerate(self.train_loader):
            # Move crops to device
            crops_batch = [crops.to(self.device, non_blocking=True) for crops in crops_batch]
            
            # Forward pass
            loss, info = self.model(crops_batch)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(self.model.student.parameters(), max_norm=3.0)
            
            self.optimizer.step()
            
            # Update teacher parameters with EMA
            self.model.update_teacher()
            
            # Accumulate loss
            total_loss += loss.item()
            self.global_step += 1
            
            # Log progress
            if (batch_idx + 1) % self.log_interval == 0:
                elapsed = time.time() - start_time
                batches_done = batch_idx + 1
                eta = elapsed / batches_done * (num_batches - batches_done)
                
                self.logger.info(
                    f"Epoch {self.current_epoch:3d} [{batches_done:4d}/{num_batches:4d}] "
                    f"Loss: {loss.item():.4f} "
                    f"LR: {current_lr:.2e} "
                    f"Momentum: {teacher_momentum:.4f} "
                    f"ETA: {eta:.1f}s"
                )
        
        avg_loss = total_loss / num_batches
        epoch_time = time.time() - start_time
        
        return {
            'loss': avg_loss,
            'lr': current_lr,
            'teacher_momentum': teacher_momentum,
            'epoch_time': epoch_time
        }
    
    def validate(self) -> Dict[str, float]:
        """
        Validate model (if validation loader provided).
        
        Returns:
            Dictionary with validation metrics
        """
        if self.val_loader is None:
            return {}
        
        self.model.eval()
        total_loss = 0.0
        num_batches = len(self.val_loader)
        
        with torch.no_grad():
            for crops_batch, _ in self.val_loader:
                crops_batch = [crops.to(self.device, non_blocking=True) for crops in crops_batch]
                
                loss, info = self.model(crops_batch)
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        return {'val_loss': avg_loss}
    
    def save_checkpoint(self, filename: Optional[str] = None, is_best: bool = False):
        """
        Save training checkpoint.
        
        Args:
            filename: Optional custom filename
            is_best: Whether this is the best checkpoint
        """
        if filename is None:
            filename = f'checkpoint_epoch_{self.current_epoch:03d}.pth'
        
        checkpoint = {
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_loss': self.best_loss,
            'training_history': self.training_history
        }
        
        # Save regular checkpoint
        torch.save(checkpoint, self.output_dir / filename)
        
        # Save best checkpoint
        if is_best:
            torch.save(checkpoint, self.output_dir / 'best_model.pth')
            self.logger.info(f"New best model saved with loss: {self.best_loss:.4f}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """
        Load training checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.current_epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        self.best_loss = checkpoint['best_loss']
        self.training_history = checkpoint['training_history']
        
        self.logger.info(f"Checkpoint loaded from epoch {self.current_epoch}")
    
    def train(self, resume_from: Optional[str] = None):
        """
        Full training loop.
        
        Args:
            resume_from: Optional checkpoint path to resume from
        """
        if resume_from:
            self.load_checkpoint(resume_from)
            start_epoch = self.current_epoch + 1
        else:
            start_epoch = 0
        
        self.logger.info("Starting training...")
        self.logger.info(f"Training from epoch {start_epoch} to {self.epochs}")
        
        # Save initial model
        if start_epoch == 0:
            self.save_checkpoint('initial_model.pth')
        
        try:
            for epoch in range(start_epoch, self.epochs):
                self.current_epoch = epoch
                
                # Train for one epoch
                train_metrics = self.train_epoch()
                
                # Validate
                val_metrics = self.validate()
                
                # Update history
                self.training_history['epoch'].append(epoch)
                self.training_history['loss'].append(train_metrics['loss'])
                self.training_history['lr'].append(train_metrics['lr'])
                self.training_history['teacher_momentum'].append(train_metrics['teacher_momentum'])
                
                # Check if best model
                is_best = train_metrics['loss'] < self.best_loss
                if is_best:
                    self.best_loss = train_metrics['loss']
                
                # Log epoch results
                log_msg = (
                    f"Epoch {epoch:3d} completed - "
                    f"Loss: {train_metrics['loss']:.4f} "
                    f"Time: {train_metrics['epoch_time']:.1f}s"
                )
                if val_metrics:
                    log_msg += f" Val Loss: {val_metrics['val_loss']:.4f}"
                
                self.logger.info(log_msg)
                
                # Save checkpoint
                if (epoch + 1) % self.save_interval == 0 or is_best:
                    self.save_checkpoint(is_best=is_best)
                
                # Save training history
                self.save_training_history()
        
        except KeyboardInterrupt:
            self.logger.info("Training interrupted by user")
            self.save_checkpoint('interrupted_model.pth')
        
        except Exception as e:
            self.logger.error(f"Training failed with error: {e}")
            self.save_checkpoint('failed_model.pth')
            raise
        
        finally:
            self.logger.info("Training completed")
            self.save_checkpoint('final_model.pth')
    
    def save_training_history(self):
        """Save training history to JSON file."""
        history_path = self.output_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def get_model_features(
        self, 
        dataloader: DataLoader, 
        max_samples: Optional[int] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract features using trained model.
        
        Args:
            dataloader: DataLoader to extract features from
            max_samples: Maximum number of samples to process
            
        Returns:
            features: Extracted features [N, embed_dim]
            targets: Corresponding targets [N]
        """
        self.model.eval()
        all_features = []
        all_targets = []
        
        with torch.no_grad():
            for i, (crops_batch, targets) in enumerate(dataloader):
                if max_samples and i * dataloader.batch_size >= max_samples:
                    break
                
                # Use first crop (global crop) for feature extraction
                images = crops_batch[0].to(self.device)
                
                # Extract features using student backbone
                features = self.model.student_backbone.forward_features(images)
                cls_features = features[:, 0]  # [CLS] token
                
                all_features.append(cls_features.cpu())
                all_targets.append(targets)
        
        features = torch.cat(all_features, dim=0)
        targets = torch.cat(all_targets, dim=0)
        
        return features, targets
    
    def evaluate_knn(
        self, 
        train_loader: DataLoader, 
        test_loader: DataLoader,
        k: int = 20,
        max_train_samples: int = 5000
    ) -> float:
        """
        Evaluate learned features using k-NN classification.
        
        This is a standard evaluation method for self-supervised learning.
        
        Args:
            train_loader: Training data for k-NN
            test_loader: Test data for k-NN  
            k: Number of neighbors
            max_train_samples: Maximum training samples to use
            
        Returns:
            k-NN accuracy
        """
        # Extract features
        train_features, train_targets = self.get_model_features(train_loader, max_train_samples)
        test_features, test_targets = self.get_model_features(test_loader)
        
        # L2 normalize features
        train_features = F.normalize(train_features, dim=1)
        test_features = F.normalize(test_features, dim=1)
        
        # Compute similarities (cosine similarity due to L2 normalization)
        similarities = torch.mm(test_features, train_features.t())
        
        # Get top-k neighbors
        _, top_k_indices = similarities.topk(k, dim=1)
        top_k_targets = train_targets[top_k_indices]
        
        # Majority vote
        predictions = torch.mode(top_k_targets, dim=1)[0]
        
        # Compute accuracy
        accuracy = (predictions == test_targets).float().mean().item()
        
        return accuracy


def create_trainer(
    model: DINO,
    train_dataset: DINODataset,
    val_dataset: Optional[DINODataset] = None,
    batch_size: int = 32,
    num_workers: int = 4,
    **trainer_kwargs
) -> DINOTrainer:
    """
    Create DINO trainer with proper data loaders.
    
    Args:
        model: DINO model to train
        train_dataset: Training dataset
        val_dataset: Optional validation dataset
        batch_size: Batch size for training
        num_workers: Number of data loading workers
        **trainer_kwargs: Additional trainer arguments
        
    Returns:
        Configured DINOTrainer
    """
    from ..data.dataset import create_dino_dataloader
    
    # Create data loaders
    train_loader = create_dino_dataloader(
        train_dataset, 
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    val_loader = None
    if val_dataset:
        val_loader = create_dino_dataloader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
    
    # Create trainer
    trainer = DINOTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        batch_size=batch_size,
        **trainer_kwargs
    )
    
    return trainer


if __name__ == "__main__":
    # Test the training system
    import torch.nn.functional as F
    from ..models.dino import create_dino_model
    from ..data.dataset import create_synthetic_dataset
    
    print("Testing DINO training system...")
    
    # Create model and dataset
    model = create_dino_model(img_size=64, embed_dim=96, depth=2, out_dim=512)
    train_dataset = create_synthetic_dataset(num_samples=200, image_size=64)
    val_dataset = create_synthetic_dataset(num_samples=50, image_size=64)
    
    # Create trainer
    trainer = create_trainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        batch_size=8,
        epochs=5,
        lr=0.001,
        output_dir='./test_outputs'
    )
    
    # Test one epoch
    trainer.current_epoch = 0
    metrics = trainer.train_epoch()
    print(f"Test epoch metrics: {metrics}")
    
    # Test feature extraction
    features, targets = trainer.get_model_features(trainer.train_loader, max_samples=32)
    print(f"Extracted features shape: {features.shape}")
    print(f"Targets shape: {targets.shape}")
    
    print("Training system test completed!")