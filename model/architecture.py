"""
AeroCrop.ai — Multi-Modal Multi-Task Neural Network Architecture

Architecture:
  Visual Encoder  : ResNet-18 backbone  → 512-dim vector
  Tabular Encoder : 3-Layer MLP         → 64-dim vector
  Fusion Layer    : Concat (576-dim) → Linear → BN → ReLU → 128-dim embedding
  Task Head 1     : Disease Classification (38 classes)
  Task Head 2     : Yield Regression (t/ha)

Dataset Taxonomy: PlantVillage 38-class agricultural pathology dataset
"""

import torch
import torch.nn as nn
from torchvision import models
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class TabularEncoder(nn.Module):
    """
    3-Layer MLP that encodes soil (N, P, K) + weather (temp, humidity, rainfall)
    into a compact latent vector.

    Input  : (batch, 6)   — [N, P, K, temperature, humidity, rainfall]
    Output : (batch, 64)
    """

    def __init__(self, input_dim: int = 6, hidden_dims: list = None, output_dim: int = 64):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [64, 64, 64]

        layers = []
        in_dim = input_dim
        for h_dim in hidden_dims:
            layers += [
                nn.Linear(in_dim, h_dim),
                nn.BatchNorm1d(h_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2),
            ]
            in_dim = h_dim

        layers += [nn.Linear(in_dim, output_dim), nn.ReLU(inplace=True)]
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class MultiModalAeroCropNet(nn.Module):
    """
    Multi-Modal Multi-Task Deep Learning Network for AeroCrop.ai.

    Inputs:
      - image  : (batch, 3, 224, 224)  RGB leaf photograph
      - tabular: (batch, 6)            [N, P, K, temp, humidity, rainfall]

    Outputs:
      - disease_logits : (batch, 38)   Raw logits for disease classification
      - yield_pred     : (batch, 1)    Predicted crop yield in tons/hectare
    """

    def __init__(
        self,
        num_classes: int = 38,
        tabular_input_dim: int = 6,
        pretrained: bool = False,
    ):
        super().__init__()

        # ── 1. Visual Encoder (ResNet-18) ─────────────────────────────────
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        resnet = models.resnet18(weights=weights)
        # Remove the final FC layer; keep the 512-dim average-pooled features
        self.visual_encoder = nn.Sequential(*list(resnet.children())[:-1])
        visual_dim = 512

        # ── 2. Tabular Encoder (3-Layer MLP) ──────────────────────────────
        self.tabular_encoder = TabularEncoder(
            input_dim=tabular_input_dim,
            hidden_dims=[64, 64, 64],
            output_dim=64,
        )
        tabular_dim = 64

        # ── 3. Fusion Layer ───────────────────────────────────────────────
        fused_dim = visual_dim + tabular_dim  # 576
        self.fusion = nn.Sequential(
            nn.Linear(fused_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
        )

        # ── 4a. Task Head: Disease Classification ─────────────────────────
        self.disease_head = nn.Linear(128, num_classes)

        # ── 4b. Task Head: Yield Regression ───────────────────────────────
        self.yield_head = nn.Sequential(
            nn.Linear(128, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, 1),
            nn.ReLU(inplace=True),   # Yield is always non-negative
        )

    def forward(
        self, image: torch.Tensor, tabular: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            image   : Tensor (B, 3, 224, 224)
            tabular : Tensor (B, 6)  — normalised [N, P, K, temp, hum, rain]
        Returns:
            (disease_logits, yield_pred)
        """
        # Visual path
        v = self.visual_encoder(image)          # (B, 512, 1, 1)
        v = v.view(v.size(0), -1)               # (B, 512)

        # Tabular path
        t = self.tabular_encoder(tabular)       # (B, 64)

        # Fusion
        fused = torch.cat([v, t], dim=1)        # (B, 576)
        embedding = self.fusion(fused)          # (B, 128)

        # Task outputs
        disease_logits = self.disease_head(embedding)   # (B, 38)
        yield_pred     = self.yield_head(embedding)     # (B, 1)

        return disease_logits, yield_pred
