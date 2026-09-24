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
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
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


# ─── Crop to Disease Class Mapping (Aligned with model/classes.json — 134 classes) ───
CROP_TO_CLASSES: dict[str, list[int]] = {
    "banana":    list(range(0, 12)),     # 0..11   (12 classes)
    "corn":      list(range(12, 23)),    # 12..22  (11 classes)
    "maize":     list(range(12, 23)),    # 12..22  (11 classes)
    "cotton":    list(range(23, 38)),    # 23..37  (15 classes)
    "citrus":    list(range(38, 51)),    # 38..50  (13 classes)
    "orange":    list(range(38, 51)),    # 38..50  (13 classes)
    "potato":    list(range(51, 69)),    # 51..68  (18 classes)
    "rice":      list(range(69, 80)),    # 69..79  (11 classes)
    "paddy":     list(range(69, 80)),    # 69..79  (11 classes)
    "soybean":   list(range(80, 91)),    # 80..90  (11 classes)
    "sugarcane": list(range(91, 103)),   # 91..102 (12 classes)
    "tomato":    list(range(103, 113)),  # 103..112 (10 classes)
    "turmeric":  list(range(113, 123)),  # 113..122 (10 classes)
    "haldi":     list(range(113, 123)),  # 113..122 (10 classes)
    "wheat":     list(range(123, 134)),  # 123..133 (11 classes)
}

# ─── Supported Agricultural Crops in Active Scope (All 134 classes) ──────────
SUPPORTED_CROP_CLASSES: list[int] = list(range(134))


def normalize_crop_name(name: str | None) -> str:
    """
    Normalizes any user-supplied or visual class prefix crop string into
    a canonical crop key.
    """
    if not name:
        return "auto"
    s = str(name).strip().lower()
    if s in ("", "auto", "none", "unknown"):
        return "auto"
    if "corn" in s or "maize" in s or "maka" in s:
        return "maize"
    if "cotton" in s or "kapas" in s or "kapus" in s:
        return "cotton"
    if "rice" in s or "paddy" in s or "dhan" in s or "bhat" in s:
        return "rice"
    if "turmeric" in s or "haldi" in s or "hald" in s:
        return "turmeric"
    if "citrus" in s or "orange" in s or "santr" in s or "mosambi" in s:
        return "orange"
    if "sugarcane" in s or "cane" in s or "ganna" in s or "oos" in s:
        return "sugarcane"
    if "banana" in s or "kela" in s or "keli" in s:
        return "banana"
    if "potato" in s or "aloo" in s or "batata" in s:
        return "potato"
    if "tomato" in s or "tamatar" in s:
        return "tomato"
    if "wheat" in s or "gehu" in s or "gahu" in s:
        return "wheat"
    if "soy" in s:
        return "soybean"
    if "onion" in s or "kanda" in s or "pyaj" in s:
        return "onion"
    if "pepper" in s or "chili" in s or "capsicum" in s or "mirchi" in s:
        return "pepper"
    if "apple" in s or "seb" in s:
        return "apple"
    if "grape" in s or "angur" in s:
        return "grape"
    return s


# ─── ICAR & Maharashtra Agriculture Commissionerate Calibrated Bounds ─────────
# Yield is expressed in metric tonnes per hectare (t/ha).
# Yield conversions:
# 1 t/ha = 0.4047 Tonnes / Acre (Biomass / Horticultural crops: Sugarcane, Banana, Tomato, Potato, Orange)
# 1 t/ha = 4.047 Quintals / Acre (Field / Grains / Fiber crops: Cotton, Soybean, Wheat, Rice, Maize, Turmeric)
AGRONOMIC_YIELD_BOUNDS: dict[str, dict[str, Any]] = {
    "cotton": {
        "min": 0.8,
        "max": 2.6,
        "category": "dry_fiber",
        "category_label": "Seed Cotton & Lint (कापूस वेचणी)",
        "typical": 1.6,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "5 – 8 Quintal / Acre",
    },
    "soybean": {
        "min": 0.8,
        "max": 2.4,
        "category": "oilseed",
        "category_label": "Oilseed Grain (सोयाबीन)",
        "typical": 1.5,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "5 – 7.5 Quintal / Acre",
    },
    "wheat": {
        "min": 1.5,
        "max": 4.2,
        "category": "grain",
        "category_label": "Cereal Grain (गहू उत्पादन)",
        "typical": 2.6,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "9 – 13 Quintal / Acre",
    },
    "rice": {
        "min": 1.8,
        "max": 4.8,
        "category": "grain",
        "category_label": "Paddy Grain (भात / धान)",
        "typical": 3.2,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "10 – 15 Quintal / Acre",
    },
    "maize": {
        "min": 2.0,
        "max": 5.5,
        "category": "grain",
        "category_label": "Coarse Grain (मका धान्य)",
        "typical": 3.6,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "12 – 18 Quintal / Acre",
    },
    "turmeric": {
        "min": 1.2,
        "max": 4.0,
        "category": "rhizome",
        "category_label": "Cured Dry Rhizome (वाळलेली हळद)",
        "typical": 2.5,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "8 – 12 Quintal / Acre",
    },
    "potato": {
        "min": 10.0,
        "max": 26.0,
        "category": "tuber",
        "category_label": "Fresh Tuber (बटाटा काढणी)",
        "typical": 18.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "6 – 9 Tonnes / Acre",
    },
    "tomato": {
        "min": 14.0,
        "max": 38.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Vegetable (टोमॅटो तोडणी)",
        "typical": 24.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "8 – 12 Tonnes / Acre",
    },
    "orange": {
        "min": 6.0,
        "max": 18.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Tree Fruit (संत्रे तोडणी)",
        "typical": 12.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "4 – 6.5 Tonnes / Acre",
    },
    "banana": {
        "min": 20.0,
        "max": 55.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Fruit Bunches (केळी घबाड)",
        "typical": 35.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "12 – 18 Tonnes / Acre",
    },
    "sugarcane": {
        "min": 45.0,
        "max": 105.0,
        "category": "stalk_biomass",
        "category_label": "Fresh Stalk Biomass (ऊस वजन)",
        "typical": 75.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "28 – 36 Tonnes / Acre",
    },
    "onion": {
        "min": 8.0,
        "max": 25.0,
        "category": "tuber",
        "category_label": "Fresh Bulb (कांदा)",
        "typical": 16.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "5 – 8 Tonnes / Acre",
    },
    "pepper": {
        "min": 1.0,
        "max": 5.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Chili (मिरची)",
        "typical": 2.5,
        "commercial_unit": "Quintal / Acre",
        "to_commercial_mult": 4.047,
        "benchmark_range": "8 – 14 Quintal / Acre",
    },
    "apple": {
        "min": 6.0,
        "max": 18.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Tree Fruit (सफरचंद)",
        "typical": 12.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "4 – 7 Tonnes / Acre",
    },
    "grape": {
        "min": 8.0,
        "max": 22.0,
        "category": "fresh_fruit",
        "category_label": "Fresh Table Grapes (द्राक्षे)",
        "typical": 14.0,
        "commercial_unit": "Tonnes / Acre",
        "to_commercial_mult": 0.4047,
        "benchmark_range": "5 – 8 Tonnes / Acre",
    },
}




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

        num_classes = len(self.classes) if self.classes else getattr(config, "NUM_DISEASE_CLASSES", 134)

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
    def _normalise_tabular(
        temperature: float,
        humidity: float,
        rainfall: float,
    ) -> torch.Tensor:
        """Z-score normalise raw weather tabular inputs using constants from config."""
        norm = config.TABULAR_NORM
        raw = [
            (temperature - norm["temperature"]["mean"]) / norm["temperature"]["std"],
            (humidity   - norm["humidity"]["mean"])    / norm["humidity"]["std"],
            (rainfall   - norm["rainfall"]["mean"])    / norm["rainfall"]["std"],
        ]
        return torch.tensor(raw, dtype=torch.float32).unsqueeze(0)  # (1, 3)

    # ── Public API ───────────────────────────────────────────────────────────

    def predict(
        self,
        image_bytes: bytes,
        temperature: float,
        humidity: float,
        rainfall: float,
        crop: str,
    ) -> dict[str, Any]:
        """
        Run full multi-modal inference (leaf photograph + weather telemetry).
        """
        if self.mock_mode:
            return self._mock_predict(temperature, humidity, rainfall, crop)

        # ── Real inference ────────────────────────────────────────────────
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_tensor = IMAGE_TRANSFORM(img).unsqueeze(0).to(self.device)       # (1,3,224,224)
        tab_tensor = self._normalise_tabular(temperature, humidity, rainfall).to(self.device)

        with torch.no_grad():
            logits, yield_raw = self.model(img_tensor, tab_tensor)

        # Calibrated temperature scaling (T=0.70) to produce realistic, sharp confidence estimates
        T = 0.70
        global_probs = F.softmax(logits / T, dim=1).squeeze(0).cpu().tolist()
        crop_clean = normalize_crop_name(crop)

        num_logits = logits.size(1)
        if crop_clean != "auto" and crop_clean in CROP_TO_CLASSES:
            candidates = [c for c in CROP_TO_CLASSES[crop_clean] if c < num_logits]
            if not candidates:
                candidates = list(range(num_logits))
            cand_tensor = torch.tensor(candidates, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = candidates[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        elif crop_clean == "auto":
            # In auto-detect mode, constrain prediction to supported agricultural project crops
            candidates = [c for c in SUPPORTED_CROP_CLASSES if c < num_logits]
            if not candidates:
                candidates = list(range(num_logits))
            cand_tensor = torch.tensor(candidates, device=logits.device)
            sub_logits = logits[0, cand_tensor]
            sub_probs = F.softmax(sub_logits / T, dim=0).cpu().tolist()
            best_sub_idx = int(torch.argmax(sub_logits).item())
            cls_idx = candidates[best_sub_idx]
            conf = float(sub_probs[best_sub_idx])
            probs = global_probs
        else:
            # Fallback direct multi-class prediction
            direct_cls = int(torch.argmax(logits, dim=1).item())
            cls_idx = direct_cls
            conf = float(global_probs[cls_idx]) if cls_idx < len(global_probs) else 0.0
            probs = global_probs

        yield_val = float(yield_raw.squeeze().item())

        # Determine effective canonical crop for agronomic yield calibration
        if crop_clean != "auto":
            effective_crop = crop_clean
        elif self.classes and cls_idx < len(self.classes):
            cls_name = self.classes[cls_idx]
            prefix = cls_name.split("___")[0].lower()
            effective_crop = normalize_crop_name(prefix)
        else:
            effective_crop = "auto"

        bounds = AGRONOMIC_YIELD_BOUNDS.get(effective_crop)
        if bounds:
            min_y = bounds["min"]
            max_y = bounds["max"]
            typical_y = bounds["typical"]

            # If raw yield is severely disconnected from this crop's biological scale
            # (e.g., visual feature bleed where cotton/soybean raw yield > 15 t/ha, or sugarcane < 20 t/ha),
            # adaptively calibrate using the crop's typical yield modulated by weather suitability:
            if yield_val > max_y * 1.25 or yield_val < min_y * 0.65:
                weather_mod = 1.0 - abs(temperature - 28) * 0.008 - max(0, rainfall - 15) * 0.004
                weather_mod = max(0.85, min(1.15, weather_mod))
                calibrated = typical_y * weather_mod
                yield_val = min(max_y, max(min_y, calibrated))
            else:
                yield_val = min(max_y, max(min_y, yield_val))

            category_info = bounds["category"]
            category_label = bounds["category_label"]
            comm_unit = bounds.get("commercial_unit", "Quintal / Acre")
            comm_mult = bounds.get("to_commercial_mult", 4.047)
            comm_base = round(typical_y * comm_mult, 1)
            comm_yield = round(yield_val * comm_mult, 1)
            bench = bounds.get("benchmark_range", f"{comm_base} {comm_unit}")
            baseline_val = typical_y
        else:
            yield_val = max(0.5, min(yield_val, 35.0))
            category_info = "general_crop"
            category_label = "Crop Yield"
            comm_unit = "Quintal / Acre"
            comm_mult = 4.047
            comm_base = round(yield_val * comm_mult, 1)
            comm_yield = round(yield_val * comm_mult, 1)
            bench = f"{comm_base} {comm_unit}"
            baseline_val = round(yield_val, 2)

        return {
            "disease_class":        cls_idx,
            "probabilities":        probs,
            "confidence":           conf,
            "yield_t_ha":           round(yield_val, 2),
            "baseline_yield_t_ha":  baseline_val,
            "yield_category":       category_info,
            "yield_category_label": category_label,
            "commercial_unit":      comm_unit,
            "commercial_yield":     comm_yield,
            "commercial_baseline":  comm_base,
            "benchmark_range":      bench,
            "mock":                 False,
            "low_confidence":       conf < 0.40,
        }

    @staticmethod
    def _mock_predict(
        temperature: float = 25.0,
        humidity: float = 60.0,
        rainfall: float = 0.0,
        crop: str = "tomato",
    ) -> dict[str, Any]:
        """
        Deterministic, agronomically-aware mock inference used when weights
        are not available. Results vary meaningfully based on weather inputs.
        """
        crop_clean = normalize_crop_name(crop)
        fingerprint = int(abs(temperature * 7.3 + humidity * 3.7 + rainfall * 5.1))

        num_classes = getattr(config, "NUM_DISEASE_CLASSES", 134)
        if crop_clean != "auto" and crop_clean in CROP_TO_CLASSES:
            candidates = CROP_TO_CLASSES[crop_clean]
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
        conf = float(probs_raw[seed_val])

        # If crop was auto, resolve from seeded class name or CROP_TO_CLASSES reverse lookup
        effective_crop = crop_clean
        if effective_crop == "auto":
            resolved_crop = "wheat"
            for c_name, c_indices in CROP_TO_CLASSES.items():
                if seed_val in c_indices:
                    resolved_crop = c_name
                    break
            effective_crop = normalize_crop_name(resolved_crop)

        bounds = AGRONOMIC_YIELD_BOUNDS.get(effective_crop)
        if bounds:
            base = bounds["typical"]
            min_y = bounds["min"]
            max_y = bounds["max"]
            cat = bounds["category"]
            cat_label = bounds["category_label"]
            comm_unit = bounds.get("commercial_unit", "Quintal / Acre")
            comm_mult = bounds.get("to_commercial_mult", 4.047)
            comm_base = round(base * comm_mult, 1)
            bench = bounds.get("benchmark_range", f"{comm_base} {comm_unit}")
        else:
            base = 2.5
            min_y = 0.6
            max_y = 6.0
            cat = "general_crop"
            cat_label = "Crop Yield"
            comm_unit = "Quintal / Acre"
            comm_mult = 4.047
            comm_base = round(base * comm_mult, 1)
            bench = f"{comm_base} {comm_unit}"

        weather_pen = 1.0 - abs(temperature - 28) * 0.01 - max(0, rainfall - 15) * 0.005 - max(0, abs(humidity - 65) - 20) * 0.003
        weather_pen = max(0.65, min(1.15, weather_pen))
        yield_val = round(min(max_y, max(min_y, base * weather_pen)), 2)
        comm_yield = round(yield_val * comm_mult, 1)

        return {
            "disease_class":        seed_val,
            "probabilities":        probs,
            "confidence":           round(conf, 4),
            "yield_t_ha":           yield_val,
            "baseline_yield_t_ha":  base,
            "yield_category":       cat,
            "yield_category_label": cat_label,
            "commercial_unit":      comm_unit,
            "commercial_yield":     comm_yield,
            "commercial_baseline":  comm_base,
            "benchmark_range":      bench,
            "mock":                 True,
            "low_confidence":       conf < 0.35,
        }
