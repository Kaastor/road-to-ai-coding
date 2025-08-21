"""
Data Loading and Augmentation for DINO Self-Supervised Learning

This module implements the multi-crop augmentation strategy crucial for DINO's
success. The key insight is that by training the model to produce consistent
representations for different augmented views of the same image, we learn
meaningful visual features without labels.

Multi-Crop Strategy:
- Global crops: Large, high-resolution crops (typically 2 crops at 224x224)
- Local crops: Smaller crops that focus on local details (typically 6+ crops at 96x96)
- This encourages learning both global structure and local features

Data Augmentations:
- Random resized crops with different scales
- Color jittering (brightness, contrast, saturation, hue)
- Random horizontal flips
- Gaussian blur (occasionally)
- Grayscale conversion (occasionally)
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from typing import List, Tuple, Optional, Callable, Any
import numpy as np
from PIL import Image, ImageFilter
import random


class GaussianBlur:
    """
    Apply Gaussian Blur to PIL Image.
    
    This augmentation helps the model learn more robust features by
    introducing controlled noise.
    """
    
    def __init__(self, sigma_min: float = 0.1, sigma_max: float = 2.0):
        self.sigma_min = sigma_min
        self.sigma_max = sigma_max
    
    def __call__(self, image: Image.Image) -> Image.Image:
        sigma = random.uniform(self.sigma_min, self.sigma_max)
        return image.filter(ImageFilter.GaussianBlur(radius=sigma))


class MultiCropDataAugmentation:
    """
    Multi-crop data augmentation for DINO.
    
    This creates multiple augmented views of each image:
    - Global crops: Capture overall structure and context
    - Local crops: Focus on local patterns and details
    
    The model learns to produce consistent features across these different views,
    leading to robust visual representations.
    """
    
    def __init__(
        self,
        global_crops_scale: Tuple[float, float] = (0.4, 1.0),
        local_crops_scale: Tuple[float, float] = (0.05, 0.4),
        global_crops_number: int = 2,
        local_crops_number: int = 6,
        global_crop_size: int = 224,
        local_crop_size: int = 96,
        color_jitter_strength: float = 1.0,
        gaussian_blur_prob: float = 0.5,
        grayscale_prob: float = 0.2
    ):
        """
        Args:
            global_crops_scale: Scale range for global crops (min, max)
            local_crops_scale: Scale range for local crops (min, max)
            global_crops_number: Number of global crops to generate
            local_crops_number: Number of local crops to generate
            global_crop_size: Size of global crops
            local_crop_size: Size of local crops
            color_jitter_strength: Strength of color jittering
            gaussian_blur_prob: Probability of applying Gaussian blur
            grayscale_prob: Probability of converting to grayscale
        """
        self.global_crops_number = global_crops_number
        self.local_crops_number = local_crops_number
        
        # Normalization (ImageNet stats - commonly used even for other datasets)
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
        
        # Color jittering
        color_jitter = transforms.ColorJitter(
            brightness=0.4 * color_jitter_strength,
            contrast=0.4 * color_jitter_strength,
            saturation=0.2 * color_jitter_strength,
            hue=0.1 * color_jitter_strength
        )
        
        # Global crop augmentation pipeline
        self.global_transform = transforms.Compose([
            transforms.RandomResizedCrop(
                global_crop_size, 
                scale=global_crops_scale,
                interpolation=Image.BICUBIC
            ),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomApply([color_jitter], p=0.8),
            transforms.RandomApply([transforms.RandomGrayscale(p=1.0)], p=grayscale_prob),
            transforms.RandomApply([GaussianBlur()], p=gaussian_blur_prob),
            transforms.ToTensor(),
            normalize
        ])
        
        # Local crop augmentation pipeline (more aggressive cropping)
        self.local_transform = transforms.Compose([
            transforms.RandomResizedCrop(
                local_crop_size,
                scale=local_crops_scale,
                interpolation=Image.BICUBIC
            ),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomApply([color_jitter], p=0.8),
            transforms.RandomApply([transforms.RandomGrayscale(p=1.0)], p=grayscale_prob),
            transforms.RandomApply([GaussianBlur()], p=gaussian_blur_prob),
            transforms.ToTensor(),
            normalize
        ])
    
    def __call__(self, image: Image.Image) -> List[torch.Tensor]:
        """
        Apply multi-crop augmentation to an image.
        
        Args:
            image: PIL Image to augment
            
        Returns:
            List of augmented crops [global_crops + local_crops]
        """
        crops = []
        
        # Generate global crops
        for _ in range(self.global_crops_number):
            crops.append(self.global_transform(image))
        
        # Generate local crops
        for _ in range(self.local_crops_number):
            crops.append(self.local_transform(image))
        
        return crops


class DINODataset(Dataset):
    """
    Dataset wrapper for DINO training.
    
    Wraps any image dataset and applies multi-crop augmentation.
    This is the bridge between standard datasets and DINO's multi-crop requirements.
    """
    
    def __init__(
        self, 
        base_dataset: Dataset,
        transform: Optional[Callable] = None
    ):
        """
        Args:
            base_dataset: Base dataset (e.g., CIFAR-10, ImageNet)
            transform: Multi-crop transform to apply
        """
        self.base_dataset = base_dataset
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.base_dataset)
    
    def __getitem__(self, idx: int) -> Tuple[List[torch.Tensor], Any]:
        """
        Get item with multi-crop augmentation.
        
        Args:
            idx: Dataset index
            
        Returns:
            crops: List of augmented crops
            target: Original target (not used in self-supervised learning)
        """
        image, target = self.base_dataset[idx]
        
        # Convert to PIL Image if necessary
        if not isinstance(image, Image.Image):
            if isinstance(image, torch.Tensor):
                # Convert tensor to PIL Image
                image = transforms.ToPILImage()(image)
            else:
                # Assume numpy array
                image = Image.fromarray(image)
        
        # Apply multi-crop augmentation
        if self.transform:
            crops = self.transform(image)
        else:
            # Default: just convert to tensor
            crops = [transforms.ToTensor()(image)]
        
        return crops, target


def create_cifar10_dino_dataset(
    data_dir: str = './data',
    train: bool = True,
    download: bool = True,
    **multicrop_kwargs
) -> DINODataset:
    """
    Create CIFAR-10 dataset with DINO augmentations.
    
    CIFAR-10 is perfect for educational purposes:
    - Small images (32x32) 
    - Quick to download and process
    - 10 simple classes
    - Good for demonstrating self-supervised learning
    
    Args:
        data_dir: Directory to store data
        train: Whether to use training or test set
        download: Whether to download if not present
        **multicrop_kwargs: Arguments for MultiCropDataAugmentation
    
    Returns:
        DINODataset ready for training
    """
    # CIFAR-10 specific settings (smaller crops due to 32x32 images)
    default_kwargs = {
        'global_crop_size': 32,
        'local_crop_size': 16,
        'global_crops_number': 2,
        'local_crops_number': 6,
        'global_crops_scale': (0.6, 1.0),  # Less aggressive for small images
        'local_crops_scale': (0.2, 0.6)
    }
    default_kwargs.update(multicrop_kwargs)
    
    # Create base CIFAR-10 dataset
    base_dataset = datasets.CIFAR10(
        root=data_dir,
        train=train,
        download=download,
        transform=None  # We'll apply transforms in DINODataset
    )
    
    # Create multi-crop transform
    multicrop_transform = MultiCropDataAugmentation(**default_kwargs)
    
    # Create DINO dataset
    dino_dataset = DINODataset(
        base_dataset=base_dataset,
        transform=multicrop_transform
    )
    
    return dino_dataset


def create_synthetic_dataset(
    num_samples: int = 1000,
    image_size: int = 224,
    num_classes: int = 10,
    **multicrop_kwargs
) -> DINODataset:
    """
    Create synthetic dataset for quick testing and debugging.
    
    This is useful for:
    - Testing the implementation without downloading data
    - Quick iteration during development
    - Understanding the data flow
    
    Args:
        num_samples: Number of synthetic samples
        image_size: Size of synthetic images
        num_classes: Number of synthetic classes
        **multicrop_kwargs: Arguments for MultiCropDataAugmentation
        
    Returns:
        DINODataset with synthetic data
    """
    
    class SyntheticDataset(Dataset):
        def __init__(self, num_samples: int, image_size: int, num_classes: int):
            self.num_samples = num_samples
            self.image_size = image_size
            self.num_classes = num_classes
        
        def __len__(self):
            return self.num_samples
        
        def __getitem__(self, idx):
            # Generate random RGB image
            image = np.random.randint(0, 255, (self.image_size, self.image_size, 3), dtype=np.uint8)
            image = Image.fromarray(image)
            
            # Random class label
            label = random.randint(0, self.num_classes - 1)
            
            return image, label
    
    # Create synthetic base dataset
    base_dataset = SyntheticDataset(num_samples, image_size, num_classes)
    
    # Create multi-crop transform
    default_kwargs = {
        'global_crop_size': image_size,
        'local_crop_size': image_size // 2
    }
    default_kwargs.update(multicrop_kwargs)
    multicrop_transform = MultiCropDataAugmentation(**default_kwargs)
    
    # Create DINO dataset
    dino_dataset = DINODataset(
        base_dataset=base_dataset,
        transform=multicrop_transform
    )
    
    return dino_dataset


def create_dino_dataloader(
    dataset: DINODataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    **kwargs
) -> DataLoader:
    """
    Create DataLoader for DINO dataset with proper collate function.
    
    The collate function handles the multi-crop structure where each
    sample returns a list of crops instead of a single tensor.
    
    Args:
        dataset: DINO dataset
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of workers for data loading
        pin_memory: Whether to pin memory for GPU transfer
        **kwargs: Additional DataLoader arguments
    
    Returns:
        DataLoader ready for DINO training
    """
    
    def collate_fn(batch):
        """
        Collate function for multi-crop data.
        
        Args:
            batch: List of (crops, target) tuples
            
        Returns:
            Tuple of (list_of_crop_batches, targets)
        """
        crops_batch = []
        targets_batch = []
        
        # Determine number of crops from first sample
        num_crops = len(batch[0][0])
        
        # Group crops by crop index
        for crop_idx in range(num_crops):
            crop_batch = torch.stack([item[0][crop_idx] for item in batch])
            crops_batch.append(crop_batch)
        
        # Collect targets
        targets_batch = torch.tensor([item[1] for item in batch])
        
        return crops_batch, targets_batch
    
    return DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=collate_fn,
        **kwargs
    )


class SimpleAugmentation:
    """
    Simple augmentation for comparison with DINO's multi-crop strategy.
    
    This is useful for:
    - Understanding the benefit of multi-crop
    - Baseline comparisons
    - Simpler debugging
    """
    
    def __init__(self, size: int = 224):
        self.transform = transforms.Compose([
            transforms.RandomResizedCrop(size, scale=(0.2, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def __call__(self, image: Image.Image) -> List[torch.Tensor]:
        """Return single augmented view as list for consistency."""
        return [self.transform(image)]


def visualize_multicrop_augmentation(
    dataset: DINODataset,
    idx: int = 0,
    save_path: Optional[str] = None
):
    """
    Visualize the multi-crop augmentation strategy.
    
    This is educational - shows how DINO sees the same image
    through different augmented views.
    
    Args:
        dataset: DINO dataset
        idx: Index of image to visualize
        save_path: Optional path to save visualization
    """
    import matplotlib.pyplot as plt
    
    crops, _ = dataset[idx]
    num_crops = len(crops)
    
    # Create subplot grid
    cols = min(4, num_crops)
    rows = (num_crops + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(3*cols, 3*rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    # Denormalize for visualization
    mean = torch.tensor([0.485, 0.456, 0.406]).reshape(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).reshape(3, 1, 1)
    
    for i, crop in enumerate(crops):
        row, col = i // cols, i % cols
        
        # Denormalize
        crop_denorm = crop * std + mean
        crop_denorm = torch.clamp(crop_denorm, 0, 1)
        
        # Convert to numpy and transpose
        crop_np = crop_denorm.permute(1, 2, 0).numpy()
        
        axes[row, col].imshow(crop_np)
        axes[row, col].set_title(f'Crop {i+1} ({crop.shape[-1]}x{crop.shape[-1]})')
        axes[row, col].axis('off')
    
    # Hide unused subplots
    for i in range(num_crops, rows * cols):
        row, col = i // cols, i % cols
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.suptitle('Multi-Crop Augmentation Views', y=1.02, fontsize=16)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    # Test the data loading system
    print("Testing DINO data loading system...")
    
    # Create synthetic dataset for quick testing
    print("\n1. Creating synthetic dataset...")
    dataset = create_synthetic_dataset(num_samples=100, image_size=64)
    print(f"Dataset size: {len(dataset)}")
    
    # Test single sample
    crops, label = dataset[0]
    print(f"Number of crops: {len(crops)}")
    print(f"Crop shapes: {[crop.shape for crop in crops]}")
    
    # Create dataloader
    print("\n2. Creating dataloader...")
    dataloader = create_dino_dataloader(dataset, batch_size=4)
    
    # Test batch loading
    crops_batch, targets_batch = next(iter(dataloader))
    print(f"Batch crops: {len(crops_batch)} crops")
    print(f"First crop batch shape: {crops_batch[0].shape}")
    print(f"Targets shape: {targets_batch.shape}")
    
    # Test CIFAR-10 (if available)
    print("\n3. Testing CIFAR-10 dataset...")
    try:
        cifar_dataset = create_cifar10_dino_dataset(download=False)
        print(f"CIFAR-10 dataset size: {len(cifar_dataset)}")
    except:
        print("CIFAR-10 not available (download=False)")
    
    print("\nData loading system test completed!")