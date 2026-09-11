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


# ─── Crop to Disease Class Mapping (Aligned with model/classes.json) ────────
CROP_TO_CLASSES: dict[str, list[int]] = {
    "banana": [0, 1, 2, 3],
    "corn": [4, 5, 6, 7],
    "maize": [4, 5, 6, 7],
    "cotton": [8, 9],
    "citrus": [10],
    "orange": [10],
    "potato": [11, 12, 13],
    "rice": [14, 15, 16, 17, 18],
    "paddy": [14, 15, 16, 17, 18],
    "soybean": [19],
    "sugarcane": [20, 21, 22, 23, 24],
    "tomato": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
    "turmeric": [35, 36, 37, 38],
    "haldi": [35, 36, 37, 38],
    "wheat": [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49],
}

# ─── Supported Agricultural Crops in Active Scope (All 50 classes) ──────────
SUPPORTED_CROP_CLASSES: list[int] = list(range(50))



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
        self.classes: list[str] = []
        self._load_model()
        self._initialised = True

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_model(self, weights_path: str | None = None):
        """Attempt to load saved weights; fall back to mock mode if unavailable."""
        resolved_path = weights_path or os.environ.get("AEROCROP_WEIGHTS_PATH") or config.WEIGHTS_PATH
        if not os.path.exists(resolved_path):
            alt = os.path.join(config.MODEL_DIR, str(resolved_path))
            if os.path.exists(alt):
                resolved_path = alt

        # Load class names from model/classes.json if present
        classes_path = os.path.join(config.MODEL_DIR, "classes.json")
        if os.path.exists(classes_path):
            try:
                import json
                with open(classes_path, "r", encoding="utf-8") as f:
                    self.classes = json.load(f)
            except Exception:
                self.classes = []

        num_classes = len(self.classes) if self.classes else getattr(config, "NUM_DISEASE_CLASSES", 50)

        if os.path.exists(resolved_path):
            try:
                state = torch.load(
                    resolved_path,
                    map_location=self.device,
                    weights_only=False,
                )
                if "disease_head.weight" in state:
                    num_classes = state["disease_head.weight"].shape[0]

                self.model = MultiModalAeroCropNet(
                    num_classes=num_classes,
                    tabular_input_dim=config.TABULAR_INPUT_DIM,
                    pretrained=False,
                ).to(self.device)

                self.model.load_state_dict(state)
                self.model.eval()
                self.mock_mode = False
                self.num_classes = num_classes
                self.active_weights_path = str(resolved_path)
                logger.info("[InferenceService] Loaded weights from %s (%d classes)", resolved_path, num_classes)
            except Exception as exc:
                logger.warning("[InferenceService] Failed to load weights: %s — using mock mode", exc)
                self.mock_mode = True
                self.model = MultiModalAeroCropNet(
                    num_classes=num_classes,
                    tabular_input_dim=config.TABULAR_INPUT_DIM,
                    pretrained=False,
                ).to(self.device)
        else:
            logger.info(
                "[InferenceService] No weights at %s — running in mock inference mode.",
                resolved_path,
            )
            self.mock_mode = True
            self.model = MultiModalAeroCropNet(
                num_classes=num_classes,
                tabular_input_dim=config.TABULAR_INPUT_DIM,
                pretrained=False,
            ).to(self.device)

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
        temperature: float,
        humidity: float,
        rainfall: float,
        crop: str,
        N: float | None = None,
        P: float | None = None,
        K: float | None = None,
    ) -> dict[str, Any]:
        """
        Run full multi-modal inference.
        N, P, K are optional. When omitted by the farmer, standard regional
        soil medians are used, maintaining full compatibility with the trained model.
        """
        target = config.CROP_NPK_TARGETS.get(crop.lower(), {"N": 100.0, "P": 50.0, "K": 50.0})
        n_val = float(N if N is not None else target.get("N", 100.0) * 1.0)
        p_val = float(P if P is not None else target.get("P", 50.0) * 1.0)
        k_val = float(K if K is not None else target.get("K", 50.0) * 1.0)

        if self.mock_mode:
            return self._mock_predict(n_val, p_val, k_val, temperature, humidity, rainfall, crop)

        # ── Real inference ────────────────────────────────────────────────
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_tensor = IMAGE_TRANSFORM(img).unsqueeze(0).to(self.device)       # (1,3,224,224)
        tab_tensor = self._normalise_tabular(n_val, p_val, k_val, temperature, humidity, rainfall).to(self.device)

        with torch.no_grad():
            logits, yield_raw = self.model(img_tensor, tab_tensor)

        # Calibrated temperature scaling (T=0.70) to produce realistic, sharp confidence estimates
        T = 0.70
        global_probs = F.softmax(logits / T, dim=1).squeeze(0).cpu().tolist()
        crop_lower = crop.lower().strip() if crop else "auto"

        if crop_lower != "auto" and crop_lower in CROP_TO_CLASSES:
            candidates = CROP_TO_CLASSES[crop_lower]
            cand_tensor = torch.tensor(candidates, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = candidates[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        elif crop_lower == "auto":
            # In auto-detect mode, constrain prediction to supported agricultural project crops
            cand_tensor = torch.tensor(SUPPORTED_CROP_CLASSES, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = SUPPORTED_CROP_CLASSES[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        else:
            # Fallback direct multi-class prediction
            direct_cls = int(torch.argmax(logits, dim=1).item())
            cls_idx = direct_cls
            conf = float(global_probs[cls_idx])
            probs = global_probs

        yield_val = float(yield_raw.squeeze().item())

        return {
            "disease_class":  cls_idx,
            "probabilities":  probs,
            "confidence":     conf,
            "yield_t_ha":     round(yield_val, 2),
            "mock":           False,
            "low_confidence": conf < 0.40,
        }

    @staticmethod
    def _mock_predict(
        N: float = 60.0,
        P: float = 30.0,
        K: float = 30.0,
        temperature: float = 25.0,
        humidity: float = 60.0,
        rainfall: float = 0.0,
        crop: str = "tomato",
    ) -> dict[str, Any]:
        """
        Deterministic, agronomically-aware mock inference used when weights
        are not available. Results vary meaningfully based on soil/weather inputs.
        """
        crop_lower = crop.lower().strip() if crop else "auto"
        fingerprint = int(abs(N * 3.1 + P * 7.3 + K * 5.7 + temperature * 2.3 + humidity * 1.7 + rainfall * 4.1))

        num_classes = getattr(config, "NUM_DISEASE_CLASSES", 38)
        if crop_lower != "auto" and crop_lower in CROP_TO_CLASSES:
            candidates = CROP_TO_CLASSES[crop_lower]
            seed_val = candidates[fingerprint % len(candidates)]
        else:
            seed_val = fingerprint % num_classes

        seed_val = seed_val % num_classes
        np.random.seed(seed_val)
        probs_raw = np.random.dirichlet(np.ones(num_classes) * 0.5)
        # Boost the seeded class to simulate a confident prediction
        probs_raw[seed_val] += 1.5
        probs_raw /= probs_raw.sum()
        probs = probs_raw.tolist()
        conf  = float(probs_raw[seed_val])

        # Agronomic yield estimate: base + soil contribution + weather penalty
        base_yield = {
            "tomato": 32.0, "orange": 24.0, "apple": 22.0, "grape": 20.0,
            "pepper": 18.0, "strawberry": 16.0, "peach": 16.0, "squash": 22.0,
            "cherry": 12.0, "blueberry": 9.0, "raspberry": 8.0, "soybean": 2.2,
            "maize": 4.5, "potato": 20.0, "cotton": 2.0, "wheat": 3.2, "rice": 4.0,
        }
        base = base_yield.get(crop_lower, 25.0)
        soil_score   = min((N / 120 + P / 60 + K / 60) / 3.0, 1.0)
        weather_pen  = 1.0 - abs(temperature - 28) * 0.01 - max(0, rainfall - 15) * 0.005
        weather_pen  = max(0.5, min(1.0, weather_pen))
        yield_val    = round(base * soil_score * weather_pen, 2)

        return {
            "disease_class":  seed_val,
            "probabilities":  probs,
            "confidence":     round(conf, 4),
            "yield_t_ha":     yield_val,
            "mock":           True,
            "low_confidence": conf < 0.35,
        }
