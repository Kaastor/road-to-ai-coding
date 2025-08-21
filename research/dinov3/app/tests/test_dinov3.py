"""
Comprehensive Test Suite for DINOv3 Implementation

This test suite ensures that all components of the DINOv3 implementation
work correctly and integrates properly. It's designed to be educational,
showing how to test machine learning models systematically.

Test Categories:
1. Model Architecture Tests (ViT, DINO)
2. Data Loading Tests (Datasets, Augmentations)  
3. Training Component Tests (Loss, Schedulers)
4. Visualization Tests (Attention, Features)
5. Integration Tests (End-to-end workflows)
6. Edge Case Tests (Error handling)

Run tests with: poetry run python -m pytest app/tests/test_dinov3.py -v
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import tempfile
import shutil
from PIL import Image

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from dinov3.models.vit import SimpleViT, create_tiny_vit, PatchEmbedding, MultiHeadAttention, TransformerBlock
from dinov3.models.dino import DINO, create_dino_model, DINOHead, DINOLoss, MultiCropWrapper
from dinov3.data.dataset import (
    MultiCropDataAugmentation, DINODataset, create_synthetic_dataset,
    create_dino_dataloader, GaussianBlur
)
from dinov3.training.trainer import DINOTrainer, CosineScheduler, TeacherMomentumScheduler
from dinov3.utils.visualization import AttentionVisualizer, FeatureVisualizer


class TestViTComponents:
    """Test Vision Transformer components."""
    
    def test_patch_embedding_shapes(self):
        """Test patch embedding produces correct shapes."""
        patch_embed = PatchEmbedding(img_size=224, patch_size=16, embed_dim=192)
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        output = patch_embed(x)
        
        expected_patches = (224 // 16) ** 2  # 196 patches
        assert output.shape == (2, expected_patches, 192)
    
    def test_patch_embedding_invalid_size(self):
        """Test patch embedding with invalid image size."""
        patch_embed = PatchEmbedding(img_size=224, patch_size=16, embed_dim=192)
        
        # Wrong image size should raise assertion error
        x = torch.randn(2, 3, 256, 256)  # Wrong size
        with pytest.raises(AssertionError):
            patch_embed(x)
    
    def test_multi_head_attention_shapes(self):
        """Test multi-head attention shapes."""
        attn = MultiHeadAttention(embed_dim=192, num_heads=3)
        
        x = torch.randn(2, 197, 192)  # [batch, seq_len, embed_dim]
        output = attn(x)
        
        assert output.shape == x.shape
    
    def test_multi_head_attention_invalid_dims(self):
        """Test multi-head attention with invalid dimensions."""
        # embed_dim not divisible by num_heads
        with pytest.raises(AssertionError):
            MultiHeadAttention(embed_dim=192, num_heads=5)  # 192 not divisible by 5
    
    def test_transformer_block(self):
        """Test transformer block."""
        block = TransformerBlock(embed_dim=192, num_heads=3)
        
        x = torch.randn(2, 197, 192)
        output = block(x)
        
        assert output.shape == x.shape
    
    def test_simple_vit_forward(self):
        """Test complete ViT forward pass."""
        model = create_tiny_vit(img_size=224, num_classes=10)
        
        x = torch.randn(2, 3, 224, 224)
        
        # Test feature extraction
        features = model.forward_features(x)
        assert features.shape == (2, 197, 192)  # 196 patches + 1 cls token
        
        # Test full forward pass
        logits = model(x)
        assert logits.shape == (2, 10)
    
    def test_attention_map_extraction(self):
        """Test attention map extraction."""
        model = create_tiny_vit(img_size=224, num_classes=10)
        model.eval()
        
        x = torch.randn(1, 3, 224, 224)
        attn_maps = model.get_attention_maps(x, layer_idx=-1)
        
        # Should have shape [batch, num_heads, seq_len, seq_len]
        assert attn_maps.shape == (1, 3, 197, 197)
    
    def test_vit_parameter_count(self):
        """Test ViT has reasonable parameter count."""
        model = create_tiny_vit()
        
        total_params = sum(p.numel() for p in model.parameters())
        
        # Tiny ViT should have reasonable number of parameters (not too many)
        assert 50_000 < total_params < 2_000_000  # Between 50K and 2M parameters


class TestDINOComponents:
    """Test DINO framework components."""
    
    def test_dino_head(self):
        """Test DINO projection head."""
        head = DINOHead(in_dim=192, out_dim=1024, bottleneck_dim=256)
        
        x = torch.randn(8, 192)
        output = head(x)
        
        assert output.shape == (8, 1024)
    
    def test_dino_loss_computation(self):
        """Test DINO loss computation."""
        loss_fn = DINOLoss(out_dim=1024, teacher_temp=0.04, student_temp=0.1)
        
        # Create dummy outputs
        student_outputs = [torch.randn(8, 1024) for _ in range(4)]  # 4 crops
        teacher_outputs = [torch.randn(8, 1024) for _ in range(2)]  # 2 global crops
        
        loss = loss_fn(student_outputs, teacher_outputs)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.dim() == 0  # Scalar loss
        assert loss.item() >= 0  # Loss should be non-negative
    
    def test_multi_crop_wrapper(self):
        """Test multi-crop wrapper."""
        backbone = create_tiny_vit(num_classes=10)
        head = DINOHead(in_dim=192, out_dim=1024)
        
        wrapper = MultiCropWrapper(backbone, head)
        
        # Create crops of different sizes
        crops = [
            torch.randn(4, 3, 224, 224),  # Global crop 1
            torch.randn(4, 3, 224, 224),  # Global crop 2  
            torch.randn(4, 3, 96, 96),    # Local crop 1
            torch.randn(4, 3, 96, 96)     # Local crop 2
        ]
        
        outputs = wrapper(crops)
        
        assert len(outputs) == 4
        for output in outputs:
            assert output.shape == (4, 1024)
    
    def test_dino_model_creation(self):
        """Test DINO model creation."""
        model = create_dino_model(
            img_size=64,  # Smaller for testing
            embed_dim=96,
            depth=2,
            num_heads=3,
            out_dim=512
        )
        
        assert isinstance(model, DINO)
        
        # Check that teacher parameters don't require gradients
        for param in model.teacher.parameters():
            assert not param.requires_grad
        
        # Check that student parameters do require gradients
        for param in model.student.parameters():
            assert param.requires_grad
    
    def test_dino_forward_pass(self):
        """Test DINO forward pass."""
        model = create_dino_model(
            img_size=64,
            embed_dim=96, 
            depth=2,
            out_dim=512
        )
        
        # Create multi-crop input
        crops = [
            torch.randn(2, 3, 64, 64),  # Global crop 1
            torch.randn(2, 3, 64, 64),  # Global crop 2
            torch.randn(2, 3, 32, 32),  # Local crop 1
            torch.randn(2, 3, 32, 32),  # Local crop 2
        ]
        
        loss, info = model(crops)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.dim() == 0
        assert isinstance(info, dict)
        assert 'loss' in info
    
    def test_teacher_momentum_update(self):
        """Test teacher momentum update."""
        model = create_dino_model(
            img_size=64,
            embed_dim=96,
            depth=2,
            out_dim=512
        )
        
        # Get initial teacher parameter
        initial_teacher_param = model.teacher.backbone.patch_embed.projection.weight.clone()
        
        # Update teacher
        model.update_teacher()
        
        # Check that teacher parameters changed
        updated_teacher_param = model.teacher.backbone.patch_embed.projection.weight
        assert not torch.equal(initial_teacher_param, updated_teacher_param)


class TestDataComponents:
    """Test data loading and augmentation components."""
    
    def test_gaussian_blur(self):
        """Test Gaussian blur augmentation."""
        blur = GaussianBlur(sigma_min=0.1, sigma_max=2.0)
        
        # Create dummy PIL image
        img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        
        blurred = blur(img)
        assert isinstance(blurred, Image.Image)
        assert blurred.size == img.size
    
    def test_multi_crop_augmentation(self):
        """Test multi-crop data augmentation."""
        transform = MultiCropDataAugmentation(
            global_crop_size=64,
            local_crop_size=32,
            global_crops_number=2,
            local_crops_number=4
        )
        
        # Create dummy PIL image
        img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
        
        crops = transform(img)
        
        assert len(crops) == 6  # 2 global + 4 local
        
        # Check crop sizes
        for i in range(2):  # Global crops
            assert crops[i].shape == (3, 64, 64)
        for i in range(2, 6):  # Local crops  
            assert crops[i].shape == (3, 32, 32)
    
    def test_dino_dataset(self):
        """Test DINO dataset wrapper."""
        # Create synthetic base dataset
        base_dataset = create_synthetic_dataset(num_samples=50, image_size=64)
        
        # Get one sample
        crops, label = base_dataset[0]
        
        assert isinstance(crops, list)
        assert len(crops) > 0  # Should have some crops
        assert isinstance(label, int)
    
    def test_dino_dataloader(self):
        """Test DINO dataloader with collate function."""
        dataset = create_synthetic_dataset(num_samples=20, image_size=64)
        
        dataloader = create_dino_dataloader(
            dataset, batch_size=4, shuffle=False, num_workers=0
        )
        
        crops_batch, labels_batch = next(iter(dataloader))
        
        assert isinstance(crops_batch, list)
        assert len(crops_batch) > 0
        assert crops_batch[0].shape[0] == 4  # Batch size
        assert labels_batch.shape == (4,)


class TestTrainingComponents:
    """Test training-related components."""
    
    def test_cosine_scheduler(self):
        """Test cosine learning rate scheduler."""
        scheduler = CosineScheduler(
            base_lr=0.001,
            final_lr=1e-6,
            total_epochs=100,
            warmup_epochs=10
        )
        
        # Test warmup phase
        lr_epoch_5 = scheduler.get_lr(5)
        assert 0 < lr_epoch_5 < 0.001  # Should be warming up
        
        # Test peak learning rate
        lr_epoch_10 = scheduler.get_lr(10)
        assert abs(lr_epoch_10 - 0.001) < 1e-6  # Should be at base_lr
        
        # Test decay phase
        lr_epoch_90 = scheduler.get_lr(90)
        assert lr_epoch_90 < 0.001  # Should be decaying
    
    def test_teacher_momentum_scheduler(self):
        """Test teacher momentum scheduler."""
        scheduler = TeacherMomentumScheduler(base_momentum=0.996, total_epochs=100)
        
        momentum_start = scheduler.get_momentum(0)
        momentum_end = scheduler.get_momentum(99)
        
        assert momentum_start >= 0.996
        assert momentum_end > momentum_start  # Should increase over time
        assert momentum_end <= 1.0


class TestVisualizationComponents:
    """Test visualization utilities."""
    
    def test_attention_visualizer_init(self):
        """Test attention visualizer initialization."""
        model = create_tiny_vit()
        visualizer = AttentionVisualizer(model)
        
        assert visualizer.model is not None
        assert hasattr(visualizer, 'device')
    
    def test_attention_map_extraction_via_visualizer(self):
        """Test attention map extraction via visualizer."""
        model = create_tiny_vit()
        visualizer = AttentionVisualizer(model)
        
        x = torch.randn(1, 3, 224, 224)
        attention_maps = visualizer.get_attention_maps(x, layer_idx=-1)
        
        assert attention_maps.shape == (1, 3, 197, 197)
    
    def test_feature_visualizer(self):
        """Test feature visualizer."""
        visualizer = FeatureVisualizer()
        
        # Test with dummy data
        dummy_features = np.random.randn(100, 50)
        dummy_labels = np.random.randint(0, 5, 100)
        
        visualizer.features = dummy_features
        visualizer.labels = dummy_labels
        
        # Test neighbor finding
        neighbors = visualizer.find_nearest_neighbors(0, k=5)
        assert len(neighbors) == 5
        assert 0 not in neighbors  # Should exclude query itself


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_end_to_end_training_setup(self):
        """Test complete training setup without actual training."""
        # Create small model and dataset
        model = create_dino_model(
            img_size=32,  # Very small for testing
            embed_dim=64,
            depth=2,
            num_heads=2,
            out_dim=256
        )
        
        dataset = create_synthetic_dataset(num_samples=20, image_size=32)
        
        # Create dataloader
        dataloader = create_dino_dataloader(
            dataset, batch_size=4, shuffle=False, num_workers=0
        )
        
        # Test one forward pass
        crops_batch, _ = next(iter(dataloader))
        loss, info = model(crops_batch)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.item() >= 0
    
    def test_checkpointing(self):
        """Test model checkpointing and loading."""
        model = create_dino_model(
            img_size=32,
            embed_dim=64,
            depth=2,
            out_dim=256
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save model
            checkpoint_path = Path(temp_dir) / 'test_checkpoint.pth'
            
            checkpoint = {
                'model_state_dict': model.state_dict(),
                'epoch': 5,
                'loss': 1.23
            }
            
            torch.save(checkpoint, checkpoint_path)
            
            # Load model
            loaded_checkpoint = torch.load(checkpoint_path)
            
            # Create new model and load state
            new_model = create_dino_model(
                img_size=32,
                embed_dim=64, 
                depth=2,
                out_dim=256
            )
            
            new_model.load_state_dict(loaded_checkpoint['model_state_dict'])
            
            # Check that parameters match
            for p1, p2 in zip(model.parameters(), new_model.parameters()):
                assert torch.equal(p1, p2)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_dataset(self):
        """Test handling of empty dataset."""
        # This should work but produce empty batches
        dataset = create_synthetic_dataset(num_samples=0)
        assert len(dataset) == 0
    
    def test_single_sample_batch(self):
        """Test batch size of 1."""
        model = create_dino_model(img_size=32, embed_dim=64, depth=2, out_dim=256)
        dataset = create_synthetic_dataset(num_samples=1, image_size=32)
        
        dataloader = create_dino_dataloader(
            dataset, batch_size=1, shuffle=False, num_workers=0
        )
        
        crops_batch, _ = next(iter(dataloader))
        loss, info = model(crops_batch)
        
        assert isinstance(loss, torch.Tensor)
    
    def test_mismatched_crop_sizes(self):
        """Test handling of different crop sizes."""
        model = create_dino_model(img_size=32, embed_dim=64, depth=2, out_dim=256)
        
        # Create crops of different sizes
        crops = [
            torch.randn(2, 3, 32, 32),   # Correct size
            torch.randn(2, 3, 16, 16),   # Different size - should work
        ]
        
        # This should work because MultiCropWrapper handles different sizes
        loss, info = model(crops)
        assert isinstance(loss, torch.Tensor)
    
    def test_gradient_flow(self):
        """Test that gradients flow correctly through student but not teacher."""
        model = create_dino_model(img_size=32, embed_dim=64, depth=2, out_dim=256)
        
        crops = [torch.randn(2, 3, 32, 32) for _ in range(2)]
        
        loss, _ = model(crops)
        loss.backward()
        
        # Check that student parameters have gradients
        student_has_grad = any(
            p.grad is not None and p.grad.abs().sum() > 0 
            for p in model.student.parameters()
        )
        assert student_has_grad, "Student parameters should have gradients"
        
        # Check that teacher parameters don't have gradients
        teacher_has_grad = any(
            p.grad is not None 
            for p in model.teacher.parameters()
        )
        assert not teacher_has_grad, "Teacher parameters should not have gradients"


# Fixtures for common test objects
@pytest.fixture
def tiny_vit():
    """Create a tiny ViT for testing."""
    return create_tiny_vit(img_size=64, num_classes=10)

@pytest.fixture
def tiny_dino():
    """Create a tiny DINO model for testing."""
    return create_dino_model(
        img_size=32,
        embed_dim=64,
        depth=2,
        num_heads=2,
        out_dim=256
    )

@pytest.fixture
def test_dataset():
    """Create a test dataset."""
    return create_synthetic_dataset(num_samples=20, image_size=32)

@pytest.fixture 
def test_dataloader(test_dataset):
    """Create a test dataloader."""
    return create_dino_dataloader(
        test_dataset, batch_size=4, shuffle=False, num_workers=0
    )


# Helper functions for test utilities
def count_parameters(model):
    """Count total parameters in a model."""
    return sum(p.numel() for p in model.parameters())

def check_tensor_shapes(tensor_list, expected_shapes):
    """Check that list of tensors have expected shapes."""
    assert len(tensor_list) == len(expected_shapes)
    for tensor, expected_shape in zip(tensor_list, expected_shapes):
        assert tensor.shape == expected_shape


if __name__ == "__main__":
    # Run tests if executed directly
    import subprocess
    import sys
    
    print("Running DINOv3 test suite...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"\nTest result: {'PASSED' if result.returncode == 0 else 'FAILED'}")
    sys.exit(result.returncode)