"""
DINO Teacher-Student Framework Implementation

This module implements the core DINO (DIstillation with NO labels) framework,
which enables self-supervised learning through a teacher-student paradigm.

Key Components:
- Teacher and Student networks (same architecture, different parameter updates)
- Exponential Moving Average (EMA) updates for teacher
- Cross-entropy loss with temperature scaling
- Centering mechanism to prevent mode collapse
- Multi-crop training strategy

The magic of DINO:
1. Student sees augmented views of images and produces predictions
2. Teacher sees different augmented views and produces "soft targets"  
3. Student learns to match teacher's outputs (knowledge distillation)
4. Teacher is updated as EMA of student (self-distillation)
5. Centering prevents collapse to trivial solutions
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional
import numpy as np

from .vit import SimpleViT


class DINOHead(nn.Module):
    """
    Projection head for DINO framework.
    
    Maps the ViT features to a smaller dimension suitable for self-supervised
    learning. Uses a bottleneck architecture with normalization.
    """
    
    def __init__(
        self, 
        in_dim: int = 192, 
        out_dim: int = 65536,
        bottleneck_dim: int = 256,
        use_bn: bool = True
    ):
        super().__init__()
        
        # Build layers
        layers = []
        layers.append(nn.Linear(in_dim, bottleneck_dim))
        if use_bn:
            layers.append(nn.BatchNorm1d(bottleneck_dim))
        layers.append(nn.GELU())
        
        # Final projection to output dimension
        layers.append(nn.Linear(bottleneck_dim, out_dim))
        
        self.mlp = nn.Sequential(*layers)
        
        # Last layer is not followed by batch norm
        if use_bn:
            self.last_layer = nn.utils.weight_norm(nn.Linear(bottleneck_dim, out_dim, bias=False))
            self.last_layer.weight_g.data.fill_(1)
            self.last_layer.weight_g.requires_grad = False
        else:
            self.last_layer = None
            
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input features [B, in_dim]
        
        Returns:
            Projected features [B, out_dim]
        """
        if self.last_layer is not None:
            # Use all layers except last, then apply weight normalized layer
            x = self.mlp[:-1](x)
            x = self.last_layer(x)
        else:
            x = self.mlp(x)
        
        return x


class DINOLoss(nn.Module):
    """
    DINO loss function with temperature scaling and centering.
    
    The loss encourages the student to match the teacher's predictions
    while preventing mode collapse through centering.
    
    Key mechanisms:
    1. Temperature scaling: Controls sharpness of distributions
    2. Centering: Prevents collapse by centering teacher outputs
    3. Cross-entropy: Student learns to match teacher's soft targets
    """
    
    def __init__(
        self, 
        out_dim: int = 65536,
        teacher_temp: float = 0.04,
        student_temp: float = 0.1,
        center_momentum: float = 0.9
    ):
        super().__init__()
        self.teacher_temp = teacher_temp
        self.student_temp = student_temp
        self.center_momentum = center_momentum
        
        # Register center as buffer (not a parameter, but part of model state)
        self.register_buffer("center", torch.zeros(1, out_dim))
        
    def forward(
        self, 
        student_outputs: List[torch.Tensor], 
        teacher_outputs: List[torch.Tensor],
        epoch: int = 0
    ) -> torch.Tensor:
        """
        Compute DINO loss between teacher and student outputs.
        
        Args:
            student_outputs: List of student predictions for different crops
            teacher_outputs: List of teacher predictions for different crops  
            epoch: Current training epoch (for potential scheduling)
        
        Returns:
            DINO loss value
        """
        # Concatenate all student outputs
        student_out = torch.cat(student_outputs)
        
        # Concatenate all teacher outputs  
        teacher_out = torch.cat(teacher_outputs).detach()
        
        # Update center with teacher outputs (only from global crops typically)
        self.update_center(teacher_out)
        
        # Apply temperature scaling and centering
        student_out = student_out / self.student_temp
        teacher_out = F.softmax((teacher_out - self.center) / self.teacher_temp, dim=-1)
        
        # Compute cross-entropy loss
        # Student learns to match teacher outputs from global crops
        total_loss = 0
        n_loss_terms = 0
        
        # Teacher outputs are from global crops, student outputs include all crops
        for iq, teacher_out_single in enumerate(teacher_outputs):
            for v, student_out_single in enumerate(student_outputs):
                # Skip if comparing same crop index for global crops
                if v < len(teacher_outputs) and v == iq:
                    continue
                    
                loss = torch.sum(-teacher_out_single * F.log_softmax(student_out_single, dim=-1), dim=-1)
                total_loss += loss.mean()
                n_loss_terms += 1
        
        # Ensure we have at least some loss terms
        if n_loss_terms == 0:
            # Fallback: just use first teacher and student outputs
            teacher_out_single = teacher_outputs[0]
            student_out_single = student_outputs[-1] if len(student_outputs) > 1 else student_outputs[0]
            loss = torch.sum(-teacher_out_single * F.log_softmax(student_out_single, dim=-1), dim=-1)
            total_loss = loss.mean()
            n_loss_terms = 1
        
        total_loss /= n_loss_terms
        return total_loss
    
    @torch.no_grad()
    def update_center(self, teacher_output: torch.Tensor):
        """
        Update the center used for centering teacher outputs.
        
        Args:
            teacher_output: Teacher predictions [B, out_dim]
        """
        batch_center = torch.sum(teacher_output, dim=0, keepdim=True)
        
        # Apply momentum update
        self.center = self.center * self.center_momentum + batch_center * (1 - self.center_momentum)


class MultiCropWrapper(nn.Module):
    """
    Wrapper for applying backbone to multiple crops.
    
    DINO uses a multi-crop strategy where:
    - Global crops: Full resolution crops (few of them)
    - Local crops: Small crops (many of them)
    
    This allows the model to learn both global and local features.
    """
    
    def __init__(self, backbone: nn.Module, head: nn.Module):
        super().__init__()
        self.backbone = backbone
        self.head = head
        
    def forward(self, x: List[torch.Tensor]) -> List[torch.Tensor]:
        """
        Apply backbone and head to each crop.
        
        Args:
            x: List of image crops [B, 3, H, W]
        
        Returns:
            List of outputs for each crop [B, out_dim]
        """
        outputs = []
        
        for crop in x:
            # Extract features using backbone (use [CLS] token)
            features = self.backbone.forward_features(crop)
            cls_features = features[:, 0]  # [CLS] token features
            
            # Apply projection head
            output = self.head(cls_features)
            outputs.append(output)
            
        return outputs


class DINO(nn.Module):
    """
    Complete DINO framework implementation.
    
    This class orchestrates the teacher-student training by:
    1. Managing teacher and student networks
    2. Performing momentum updates on teacher
    3. Computing DINO loss
    4. Handling multi-crop augmentations
    """
    
    def __init__(
        self,
        backbone: SimpleViT,
        out_dim: int = 65536,
        bottleneck_dim: int = 256,
        teacher_temp: float = 0.04,
        student_temp: float = 0.1,
        center_momentum: float = 0.9,
        teacher_momentum: float = 0.996
    ):
        super().__init__()
        
        self.teacher_momentum = teacher_momentum
        embed_dim = backbone.embed_dim
        
        # Create student network
        self.student_backbone = backbone
        self.student_head = DINOHead(embed_dim, out_dim, bottleneck_dim)
        self.student = MultiCropWrapper(self.student_backbone, self.student_head)
        
        # Create teacher network (same architecture)
        teacher_backbone = SimpleViT(
            img_size=backbone.patch_embed.img_size,
            patch_size=backbone.patch_embed.patch_size,
            embed_dim=backbone.embed_dim,
            depth=len(backbone.blocks),
            num_heads=backbone.blocks[0].attn.num_heads,
            mlp_ratio=4.0,  # Assuming default
            num_classes=backbone.head.out_features
        )
        teacher_head = DINOHead(embed_dim, out_dim, bottleneck_dim)
        self.teacher = MultiCropWrapper(teacher_backbone, teacher_head)
        
        # Teacher parameters are not updated by gradients
        for p in self.teacher.parameters():
            p.requires_grad = False
        
        # Initialize teacher with student weights
        self.teacher.load_state_dict(self.student.state_dict())
        
        # DINO loss
        self.criterion = DINOLoss(
            out_dim=out_dim,
            teacher_temp=teacher_temp,
            student_temp=student_temp,
            center_momentum=center_momentum
        )
        
    def forward(self, images: List[torch.Tensor]) -> Tuple[torch.Tensor, dict]:
        """
        Forward pass through DINO framework.
        
        Args:
            images: List of image crops (first few are global, rest are local)
        
        Returns:
            loss: DINO loss value
            info: Dictionary with additional information
        """
        # Get student outputs for all crops
        student_outputs = self.student(images)
        
        # Get teacher outputs only for global crops (first 2 typically)
        teacher_outputs = self.teacher(images[:2])
        
        # Compute loss
        loss = self.criterion(student_outputs, teacher_outputs)
        
        # Additional info for logging
        info = {
            'loss': loss.item(),
            'student_outputs': len(student_outputs),
            'teacher_outputs': len(teacher_outputs)
        }
        
        return loss, info
    
    @torch.no_grad()
    def update_teacher(self):
        """
        Update teacher parameters using exponential moving average of student.
        
        This is called after each training step and is crucial for DINO's
        self-distillation mechanism.
        """
        for param_student, param_teacher in zip(
            self.student.parameters(), self.teacher.parameters()
        ):
            param_teacher.data.mul_(self.teacher_momentum).add_(
                param_student.data, alpha=1 - self.teacher_momentum
            )
    
    def get_teacher_momentum_schedule(self, epoch: int, max_epochs: int) -> float:
        """
        Cosine schedule for teacher momentum.
        
        Args:
            epoch: Current epoch
            max_epochs: Total number of epochs
            
        Returns:
            Updated teacher momentum value
        """
        base_momentum = 0.996
        final_momentum = 1.0
        
        momentum = final_momentum - (final_momentum - base_momentum) * (
            np.cos(np.pi * epoch / max_epochs) + 1
        ) / 2
        
        return momentum


def create_dino_model(
    img_size: int = 224,
    patch_size: int = 16,
    embed_dim: int = 192,
    depth: int = 3,
    num_heads: int = 3,
    out_dim: int = 8192,  # Smaller for educational purposes
    **kwargs
) -> DINO:
    """
    Create a DINO model with specified parameters.
    
    Args:
        img_size: Input image size
        patch_size: Patch size for ViT
        embed_dim: Embedding dimension
        depth: Number of transformer layers
        num_heads: Number of attention heads
        out_dim: Output dimension for projection head
        **kwargs: Additional arguments for DINO
    
    Returns:
        DINO model ready for training
    """
    # Create backbone
    backbone = SimpleViT(
        img_size=img_size,
        patch_size=patch_size,
        embed_dim=embed_dim,
        depth=depth,
        num_heads=num_heads,
        mlp_ratio=4.0,
        num_classes=1000  # Not used in self-supervised setting
    )
    
    # Create DINO framework
    model = DINO(
        backbone=backbone,
        out_dim=out_dim,
        **kwargs
    )
    
    return model


if __name__ == "__main__":
    # Test DINO implementation
    model = create_dino_model(
        img_size=224,
        embed_dim=192,
        depth=3,
        num_heads=3,
        out_dim=1024  # Small for testing
    )
    
    print(f"Student parameters: {sum(p.numel() for p in model.student.parameters()):,}")
    print(f"Teacher parameters: {sum(p.numel() for p in model.teacher.parameters()):,}")
    
    # Test forward pass with multi-crop
    global_crops = [torch.randn(2, 3, 224, 224) for _ in range(2)]
    local_crops = [torch.randn(2, 3, 96, 96) for _ in range(4)]
    all_crops = global_crops + local_crops
    
    # Forward pass
    loss, info = model(all_crops)
    print(f"Loss: {loss.item():.4f}")
    print(f"Info: {info}")
    
    # Test teacher update
    model.update_teacher()
    print("Teacher updated successfully!")
    
    # Test momentum scheduling
    momentum = model.get_teacher_momentum_schedule(epoch=10, max_epochs=100)
    print(f"Momentum at epoch 10: {momentum:.4f}")