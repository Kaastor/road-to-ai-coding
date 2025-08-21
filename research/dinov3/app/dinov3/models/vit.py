"""
Simple Vision Transformer (ViT) Implementation for Educational Purposes

This module implements a simplified Vision Transformer suitable for learning
the core concepts of DINOv3. The implementation focuses on clarity over
performance optimization.

Key Components:
- Patch Embedding: Convert image patches to tokens
- Positional Encoding: Add spatial position information
- Transformer Blocks: Multi-head attention + MLP
- Classification Head: Final feature projection
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class PatchEmbedding(nn.Module):
    """
    Convert image into patches and embed them.
    
    This is the first step in ViT: split image into non-overlapping patches
    and linearly project each patch to create token embeddings.
    """
    
    def __init__(self, img_size: int = 224, patch_size: int = 16, embed_dim: int = 192):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        # Linear projection of patches
        # Conv2d with kernel=patch_size and stride=patch_size effectively
        # splits image into patches and projects them
        self.projection = nn.Conv2d(
            in_channels=3, 
            out_channels=embed_dim,
            kernel_size=patch_size,
            stride=patch_size
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input image tensor [B, 3, H, W]
        
        Returns:
            Patch embeddings [B, num_patches, embed_dim]
        """
        B, C, H, W = x.shape
        assert H == self.img_size and W == self.img_size, f"Image size must be {self.img_size}x{self.img_size}"
        
        # Project patches: [B, 3, H, W] -> [B, embed_dim, H//patch_size, W//patch_size]
        x = self.projection(x)
        
        # Flatten spatial dimensions: [B, embed_dim, H', W'] -> [B, embed_dim, num_patches]
        x = x.flatten(2)
        
        # Transpose to get [B, num_patches, embed_dim]
        x = x.transpose(1, 2)
        
        return x


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention mechanism.
    
    This is the core component that allows tokens to attend to each other,
    enabling the model to learn spatial relationships between patches.
    """
    
    def __init__(self, embed_dim: int = 192, num_heads: int = 3):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)
        
        # Linear projections for queries, keys, and values
        self.qkv = nn.Linear(embed_dim, embed_dim * 3)
        self.proj = nn.Linear(embed_dim, embed_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor [B, N, embed_dim] where N is number of tokens
        
        Returns:
            Attention output [B, N, embed_dim]
        """
        B, N, C = x.shape
        
        # Generate Q, K, V: [B, N, C] -> [B, N, 3*C] -> [B, N, 3, num_heads, head_dim]
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim)
        # Permute to [3, B, num_heads, N, head_dim]
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        # Compute attention scores: [B, num_heads, N, head_dim] @ [B, num_heads, head_dim, N] -> [B, num_heads, N, N]
        attn_scores = (q @ k.transpose(-2, -1)) * self.scale
        attn_probs = F.softmax(attn_scores, dim=-1)
        
        # Apply attention to values: [B, num_heads, N, N] @ [B, num_heads, N, head_dim] -> [B, num_heads, N, head_dim]
        attn_output = attn_probs @ v
        
        # Reshape and project: [B, num_heads, N, head_dim] -> [B, N, embed_dim]
        attn_output = attn_output.transpose(1, 2).reshape(B, N, C)
        output = self.proj(attn_output)
        
        return output


class MLP(nn.Module):
    """
    Multi-Layer Perceptron (Feed-Forward Network).
    
    Applied to each token independently after self-attention.
    Uses GELU activation for better performance.
    """
    
    def __init__(self, embed_dim: int = 192, mlp_ratio: float = 4.0):
        super().__init__()
        hidden_dim = int(embed_dim * mlp_ratio)
        
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, embed_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor [B, N, embed_dim]
        
        Returns:
            MLP output [B, N, embed_dim]
        """
        x = self.fc1(x)
        x = self.act(x)
        x = self.fc2(x)
        return x


class TransformerBlock(nn.Module):
    """
    Single Transformer block: LayerNorm -> MultiHeadAttention -> LayerNorm -> MLP
    with residual connections.
    
    This is the fundamental building block of the Vision Transformer.
    """
    
    def __init__(self, embed_dim: int = 192, num_heads: int = 3, mlp_ratio: float = 4.0):
        super().__init__()
        
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = MultiHeadAttention(embed_dim, num_heads)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = MLP(embed_dim, mlp_ratio)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor [B, N, embed_dim]
        
        Returns:
            Transformer block output [B, N, embed_dim]
        """
        # Self-attention with residual connection
        x = x + self.attn(self.norm1(x))
        
        # MLP with residual connection
        x = x + self.mlp(self.norm2(x))
        
        return x


class SimpleViT(nn.Module):
    """
    Simplified Vision Transformer for educational purposes.
    
    Architecture:
    1. Patch Embedding: Convert image patches to tokens
    2. Add [CLS] token and positional embeddings
    3. Stack of Transformer blocks
    4. Final layer norm and projection head
    
    This implementation is much smaller than production ViTs but contains
    all the essential components for understanding the architecture.
    """
    
    def __init__(
        self, 
        img_size: int = 224,
        patch_size: int = 16, 
        embed_dim: int = 192,
        depth: int = 3,
        num_heads: int = 3,
        mlp_ratio: float = 4.0,
        num_classes: int = 1000
    ):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.num_patches = (img_size // patch_size) ** 2
        
        # Patch embedding
        self.patch_embed = PatchEmbedding(img_size, patch_size, embed_dim)
        
        # [CLS] token - learnable token used for classification
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        
        # Positional embeddings - learnable position encoding
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, mlp_ratio)
            for _ in range(depth)
        ])
        
        # Final layer norm
        self.norm = nn.LayerNorm(embed_dim)
        
        # Classification head
        self.head = nn.Linear(embed_dim, num_classes)
        
        # Initialize parameters
        self._init_weights()
        
    def _init_weights(self):
        """Initialize model parameters."""
        # Initialize positional embeddings
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        
        # Initialize linear layers
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.trunc_normal_(module.weight, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.zeros_(module.bias)
                nn.init.ones_(module.weight)
    
    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the feature extraction pipeline.
        
        Args:
            x: Input image tensor [B, 3, H, W]
        
        Returns:
            Feature representations [B, N+1, embed_dim] where N is num_patches
        """
        B = x.shape[0]
        
        # Patch embedding: [B, 3, H, W] -> [B, num_patches, embed_dim]
        x = self.patch_embed(x)
        
        # Add [CLS] token: [B, num_patches, embed_dim] -> [B, num_patches+1, embed_dim]
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)
        
        # Add positional embeddings
        x = x + self.pos_embed
        
        # Apply transformer blocks
        for block in self.blocks:
            x = block(x)
        
        # Apply final layer norm
        x = self.norm(x)
        
        return x
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Full forward pass including classification head.
        
        Args:
            x: Input image tensor [B, 3, H, W]
        
        Returns:
            Classification logits [B, num_classes]
        """
        features = self.forward_features(x)
        
        # Use [CLS] token for classification
        cls_features = features[:, 0]
        logits = self.head(cls_features)
        
        return logits
    
    def get_attention_maps(self, x: torch.Tensor, layer_idx: int = -1) -> torch.Tensor:
        """
        Extract attention maps for visualization.
        
        Args:
            x: Input image tensor [B, 3, H, W]
            layer_idx: Which transformer layer to extract attention from (-1 for last)
        
        Returns:
            Attention maps [B, num_heads, N+1, N+1]
        """
        B = x.shape[0]
        
        # Get patch embeddings and add cls token + positional encoding
        x = self.patch_embed(x)
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)
        x = x + self.pos_embed
        
        # Forward through blocks until target layer
        target_layer = len(self.blocks) + layer_idx if layer_idx < 0 else layer_idx
        
        for i, block in enumerate(self.blocks):
            if i == target_layer:
                # Extract attention from this block
                x_norm = block.norm1(x)
                B, N, C = x_norm.shape
                
                qkv = block.attn.qkv(x_norm).reshape(B, N, 3, block.attn.num_heads, block.attn.head_dim)
                qkv = qkv.permute(2, 0, 3, 1, 4)
                q, k, v = qkv[0], qkv[1], qkv[2]
                
                attn_scores = (q @ k.transpose(-2, -1)) * block.attn.scale
                attn_maps = F.softmax(attn_scores, dim=-1)
                
                return attn_maps
            
            x = block(x)
        
        raise ValueError(f"Layer index {layer_idx} out of range")


def create_tiny_vit(img_size: int = 224, num_classes: int = 1000) -> SimpleViT:
    """
    Create a tiny ViT model suitable for quick experimentation.
    
    Args:
        img_size: Input image size
        num_classes: Number of output classes
    
    Returns:
        Tiny ViT model
    """
    return SimpleViT(
        img_size=img_size,
        patch_size=16,
        embed_dim=192,
        depth=3,
        num_heads=3,
        mlp_ratio=4.0,
        num_classes=num_classes
    )


def create_small_vit(img_size: int = 224, num_classes: int = 1000) -> SimpleViT:
    """
    Create a small ViT model with more capacity.
    
    Args:
        img_size: Input image size
        num_classes: Number of output classes
    
    Returns:
        Small ViT model
    """
    return SimpleViT(
        img_size=img_size,
        patch_size=16,
        embed_dim=384,
        depth=6,
        num_heads=6,
        mlp_ratio=4.0,
        num_classes=num_classes
    )


if __name__ == "__main__":
    # Test the ViT implementation
    model = create_tiny_vit(img_size=224, num_classes=10)
    
    # Print model info
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    # Test forward pass
    x = torch.randn(2, 3, 224, 224)
    
    # Test feature extraction
    features = model.forward_features(x)
    print(f"Feature shape: {features.shape}")
    
    # Test full forward pass
    logits = model(x)
    print(f"Output shape: {logits.shape}")
    
    # Test attention extraction
    attn_maps = model.get_attention_maps(x, layer_idx=-1)
    print(f"Attention maps shape: {attn_maps.shape}")