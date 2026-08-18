"""
AeroCrop.ai — Inference Service (Model Layer)

Responsibilities:
  - Load model weights from disk (WEIGHTS_PATH from config)
  - Preprocess input image and tabular tensor
  - Run forward pass on GPU/CPU
  - If weights are absent → fall back to deterministic mock inference
    (ensures the web application works immediately without training)
"""

from __future__ import annotations
import os
import sys
import logging
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet

logger = logging.getLogger(__name__)

# ─── Image preprocessing pipeline (matches ResNet-18 training config) ────────
IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


class InferenceService:
    """
    Singleton inference service loaded once at application startup.
    """

    _instance: "InferenceService | None" = None

    def __new__(cls) -> "InferenceService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self.device = torch.device(config.DEVICE)
        self.model: MultiModalAeroCropNet | None = None
        self.mock_mode: bool = True
        self._load_model()
        self._initialised = True

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_model(self):
        """Attempt to load saved weights; fall back to mock mode if unavailable."""
        self.model = MultiModalAeroCropNet(
            num_classes=config.NUM_DISEASE_CLASSES,
            tabular_input_dim=config.TABULAR_INPUT_DIM,
            pretrained=False,
        ).to(self.device)

        if os.path.exists(config.WEIGHTS_PATH):
            try:
                state = torch.load(config.WEIGHTS_PATH, map_location=self.device)
                self.model.load_state_dict(state)
                self.model.eval()
                self.mock_mode = False
                logger.info("[InferenceService] Loaded weights from %s", config.WEIGHTS_PATH)
            except Exception as exc:
                logger.warning("[InferenceService] Failed to load weights: %s — using mock mode", exc)
                self.mock_mode = True
        else:
            logger.info(
                "[InferenceService] No weights at %s — running in mock inference mode.",
                config.WEIGHTS_PATH,
            )
            self.mock_mode = True

    @staticmethod
    def _normalise_tabular(N: float, P: float, K: float,
                           temperature: float, humidity: float,
                           rainfall: float) -> torch.Tensor:
        """Z-score normalise raw tabular inputs using constants from config."""
        norm = config.TABULAR_NORM
        raw = [
            (N          - norm["N"]["mean"])           / norm["N"]["std"],
            (P          - norm["P"]["mean"])           / norm["P"]["std"],
            (K          - norm["K"]["mean"])           / norm["K"]["std"],
            (temperature - norm["temperature"]["mean"]) / norm["temperature"]["std"],
            (humidity   - norm["humidity"]["mean"])    / norm["humidity"]["std"],
            (rainfall   - norm["rainfall"]["mean"])    / norm["rainfall"]["std"],
        ]
        return torch.tensor(raw, dtype=torch.float32).unsqueeze(0)  # (1, 6)

    # ── Public API ───────────────────────────────────────────────────────────

    def predict(
        self,
        image_bytes: bytes,
        N: float, P: float, K: float,
        temperature: float, humidity: float, rainfall: float,
        crop: str,
    ) -> dict[str, Any]:
        """
        Run full multi-modal inference.

        Returns:
            {
                "disease_class"  : int,
                "probabilities"  : list[float],   # 38 values
                "confidence"     : float,
                "yield_t_ha"     : float,
                "mock"           : bool,
            }
        """
        if self.mock_mode:
            return self._mock_predict(N, P, K, temperature, humidity, rainfall, crop)

        # ── Real inference ────────────────────────────────────────────────
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_tensor = IMAGE_TRANSFORM(img).unsqueeze(0).to(self.device)       # (1,3,224,224)
        tab_tensor = self._normalise_tabular(N, P, K, temperature, humidity, rainfall).to(self.device)

        with torch.no_grad():
            logits, yield_raw = self.model(img_tensor, tab_tensor)

        probs   = F.softmax(logits, dim=1).squeeze(0).cpu().tolist()
        cls_idx = int(torch.argmax(logits, dim=1).item())
        conf    = float(probs[cls_idx])
        yield_val = float(yield_raw.squeeze().item())

        return {
            "disease_class": cls_idx,
            "probabilities": probs,
            "confidence":    conf,
            "yield_t_ha":    round(yield_val, 2),
            "mock":          False,
        }

    @staticmethod
    def _mock_predict(
        N: float, P: float, K: float,
        temperature: float, humidity: float, rainfall: float,
        crop: str,
    ) -> dict[str, Any]:
        """
        Deterministic, agronomically-aware mock inference used when weights
        are not available. Results vary meaningfully based on soil/weather inputs.
        """
        # Derive a deterministic class index from input fingerprint
        seed_val = int((N * 3 + P * 7 + K * 5 + temperature * 2 + humidity) % 38)
        np.random.seed(seed_val)
        probs_raw = np.random.dirichlet(np.ones(38) * 0.5)
        # Boost the seeded class to simulate a confident prediction
        probs_raw[seed_val] += 1.2
        probs_raw /= probs_raw.sum()
        probs = probs_raw.tolist()
        conf  = float(probs_raw[seed_val])

        # Agronomic yield estimate: base + soil contribution + weather penalty
        base_yield = {"cotton": 1.8, "wheat": 3.2, "maize": 4.5, "rice": 3.8, "potato": 18.0}
        base = base_yield.get(crop.lower(), 3.0)
        soil_score   = min((N / 120 + P / 60 + K / 60) / 3.0, 1.0)
        weather_pen  = 1.0 - abs(temperature - 28) * 0.01 - max(0, rainfall - 15) * 0.005
        weather_pen  = max(0.5, min(1.0, weather_pen))
        yield_val    = round(base * soil_score * weather_pen, 2)

        return {
            "disease_class": seed_val,
            "probabilities": probs,
            "confidence":    round(conf, 4),
            "yield_t_ha":    yield_val,
            "mock":          True,
        }
