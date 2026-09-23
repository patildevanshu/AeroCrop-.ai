"""
AeroCrop.ai  PyTorch Dataset Classes (Model Layer)

Two dataset implementations:

1. PlantDiseaseDataset
   - Source: Multi-Source Agricultural Pathology Dataset — 166,630 images, 134 classes across 11 crops
   - Root dir expected structure: train/<ClassName>/<image.jpg>
   - Returns: (image_tensor [3,224,224], class_index)

2. YieldDataset
   - Source: crop_yield.csv or yield_df.csv
   - Columns: avg_temp, est_humidity, rain_mm_day, yield_t_ha
   - Returns: (weather_tensor [3], yield_t_ha)

3. MultiModalDataset  (used for joint training)
   - Pairs each disease image with a randomly sampled tabular weather row
     from the same crop category.
   - Returns: (image_tensor, weather_tensor [3], disease_label, yield_t_ha)
"""

from __future__ import annotations

import os
import sys
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from torchvision import transforms

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Load authoritative class taxonomy (matches model/classes.json and 134-class dataset)
def _load_classes() -> list[str]:
    classes_path = os.path.join(config.MODEL_DIR, "classes.json")
    if os.path.exists(classes_path):
        try:
            import json
            with open(classes_path, "r", encoding="utf-8") as f:
                cl = json.load(f)
                if len(cl) > 0:
                    return cl
        except Exception:
            pass
    train_dir = os.path.join(config.DATA_DIR, "main dataset", "train")
    if os.path.exists(train_dir):
        subdirs = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
        if len(subdirs) > 0:
            return subdirs
    return []

DISEASE_CLASSES: list[str] = _load_classes()
CLASS_TO_IDX: dict[str, int] = {c: i for i, c in enumerate(DISEASE_CLASSES)}

#  Crop name mapping: PlantVillage folder prefix  yield crop name 
FOLDER_TO_CROP: dict[str, str] = {
    "Corn_(maize)": "maize",
    "Potato":       "potato",
    "Tomato":       "tomato",
    "Apple":        "apple",
    "Grape":        "grape",
    "Peach":        "peach",
    "Cherry":       "cherry",
    "Pepper":       "pepper",
    "Strawberry":   "strawberry",
    "Soybean":      "soybean",
    "Blueberry":    "blueberry",
    "Raspberry":    "raspberry",
    "Squash":       "squash",
    "Orange":       "orange",
    "Cotton":       "cotton",
    "Banana":       "banana",
    "Turmeric":     "turmeric",
    "Sugarcane":    "sugarcane",
    "Onion":        "onion",
    "Rice":         "rice",
    "Wheat":        "wheat",
}

#  Image transforms 
TRAIN_TRANSFORM = transforms.Compose([
    transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.05),
    transforms.RandomRotation(degrees=15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

VAL_TRANSFORM = transforms.Compose([
    transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


# 
#   1. PlantDiseaseDataset                                                  
# 

class PlantDiseaseDataset(Dataset):
    """
    Dataset for plant leaf disease classification.

    Args:
        root_dir : Path to the 'train' or 'valid' directory.
                   Structure: <root_dir>/<ClassName>/<image.jpg>
        transform: torchvision transform pipeline.
        max_per_class: Limit images per class (useful for quick experiments).

    Returns per item:
        image  : FloatTensor (3, 224, 224)
        label  : int  class index (0-133)
    """

    def __init__(
        self,
        root_dir: str,
        transform=None,
        max_per_class: int = None,
        classes: list[str] | None = None,
    ):
        target_path = Path(root_dir)
        if not target_path.exists():
            candidates = [
                Path(config.DATA_DIR) / "main dataset" / target_path.name,
                Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / target_path.name,
                Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / target_path.name,
                Path(config.DATA_DIR) / target_path.name,
                Path(config.BASE_DIR) / root_dir,
            ]
            for c in candidates:
                if c.exists() and any(c.iterdir()):
                    target_path = c
                    break
        self.root_dir  = target_path
        self.transform = transform or VAL_TRANSFORM

        # Dynamic or explicit class indexing
        if classes is not None:
            self.classes = list(classes)
            self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        else:
            self.classes = list(DISEASE_CLASSES)
            self.class_to_idx = dict(CLASS_TO_IDX)

        self.samples: list[tuple[Path, int]] = []

        for folder in sorted(self.root_dir.iterdir()):
            if not folder.is_dir():
                continue

            # Try exact match first, then fuzzy match
            class_idx = self.class_to_idx.get(folder.name)
            if class_idx is None:
                normalized = folder.name.replace(" ", "_")
                class_idx = self.class_to_idx.get(normalized)
            if class_idx is None:
                print(f"  [Dataset] Warning: unknown class folder '{folder.name}'  skipped.")
                continue

            images = sorted(
                p for p in folder.iterdir()
                if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
            )
            if max_per_class:
                images = images[:max_per_class]

            for img_path in images:
                self.samples.append((img_path, class_idx))

        print(f"  [PlantDiseaseDataset] Loaded {len(self.samples)} images across {len(self.classes)} classes from {self.root_dir.name}/")

    @property
    def num_classes(self) -> int:
        return len(self.classes)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)
        return img, label


# 
#   2. YieldDataset                                                         
# 

# Crop names in yield_df.csv / crop_yield.csv -> our internal keys
YIELD_CROP_MAP: dict[str, str] = {
    "Maize":          "maize",
    "Potatoes":       "potato",
    "Potato":         "potato",
    "Sweet potatoes": "potato",
    "Sweet potato":   "potato",
    "Rice, paddy":    "rice",
    "Rice":           "rice",
    "Wheat":          "wheat",
    "Cotton":         "cotton",
    "Cotton(lint)":   "cotton",
    "Sugarcane":      "sugarcane",
    "Banana":         "banana",
    "Onion":          "onion",
    "Soybeans":       "soybean",
    "Soybean":        "soybean",
    "Soyabean":       "soybean",
    "Dry chillies":   "pepper",
    "Black pepper":   "pepper",
    "Turmeric":       "turmeric",
    "Cassava":        "potato",
    "Sorghum":        "maize",
}


class YieldDataset(Dataset):
    """
    Tabular dataset for yield regression supporting both:
    1. Modern Indian Agricultural Dataset (crop_yield.csv) with real Indian crops
       and seasonal weather telemetry.
    2. Legacy FAO yield_df.csv.

    Features (3 weather telemetry inputs):
        avg_temp, est_humidity, rain_mm_day

    Target:
        yield_t_ha — crop yield in metric tonnes per hectare
    """

    def __init__(self, csv_path: str, split: str = "train", val_fraction: float = 0.15):
        df = pd.read_csv(csv_path)

        # ── Column clean-up ──────────────────────────────────────────────────
        df.columns = [c.strip() for c in df.columns]
        if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
            df = df.iloc[:, 1:]   # drop unnamed index column

        # Check if pre-processed Indian Agricultural Dataset (crop_yield.csv)
        if "crop_key" in df.columns and "yield_t_ha" in df.columns and "avg_temp" in df.columns:
            required = ["crop_key", "avg_temp", "est_humidity", "rain_mm_day", "yield_t_ha"]
            for num_col in ["avg_temp", "est_humidity", "rain_mm_day", "yield_t_ha"]:
                df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
            df = df.dropna(subset=required).copy()
        else:
            # Map crop names
            item_col = "Crop" if "Crop" in df.columns else "Item"
            df["crop_key"] = df[item_col].map(YIELD_CROP_MAP)
            df = df.dropna(subset=["crop_key"]).copy()

            # Drop rows with missing weather values
            required = ["avg_temp", "average_rain_fall_mm_per_year", "hg/ha_yield"]
            df = df.dropna(subset=required).copy()

            # Convert yield to t/ha
            df["yield_t_ha"] = df["hg/ha_yield"] / 10_000.0

            # Handle pesticides (some rows may be NaN)
            if "pesticides_tonnes" in df.columns:
                df["pesticides_tonnes"] = df["pesticides_tonnes"].fillna(0.0)

            # ── Horticultural & Specialty Crops Agronomic Calibration ─────────────
            horticultural_baselines = {
                "tomato":     {"base": 32.0, "opt_temp": 26.0, "opt_rain": 4.0},
                "apple":      {"base": 22.0, "opt_temp": 20.0, "opt_rain": 3.5},
                "grape":      {"base": 20.0, "opt_temp": 25.0, "opt_rain": 2.5},
                "orange":     {"base": 24.0, "opt_temp": 28.0, "opt_rain": 3.0},
                "pepper":     {"base": 18.0, "opt_temp": 26.0, "opt_rain": 3.0},
                "peach":      {"base": 16.0, "opt_temp": 22.0, "opt_rain": 3.0},
                "strawberry": {"base": 16.0, "opt_temp": 22.0, "opt_rain": 3.5},
                "cherry":     {"base": 12.0, "opt_temp": 20.0, "opt_rain": 3.0},
                "blueberry":  {"base": 9.0,  "opt_temp": 21.0, "opt_rain": 3.0},
                "raspberry":  {"base": 8.0,  "opt_temp": 20.0, "opt_rain": 3.0},
                "squash":     {"base": 22.0, "opt_temp": 27.0, "opt_rain": 3.5},
                "banana":     {"base": 52.0, "opt_temp": 28.0, "opt_rain": 5.0},
                "sugarcane":  {"base": 92.0, "opt_temp": 30.0, "opt_rain": 6.0},
                "turmeric":   {"base": 26.0, "opt_temp": 27.0, "opt_rain": 4.5},
                "maize":      {"base": 6.2,  "opt_temp": 28.0, "opt_rain": 4.5},
                "cotton":     {"base": 2.8,  "opt_temp": 30.0, "opt_rain": 3.5},
            }

            synthetic_rows = []
            for h_crop, h_cfg in horticultural_baselines.items():
                sample_w = df[["avg_temp", "average_rain_fall_mm_per_year"]].sample(
                    n=min(len(df), 600),
                    random_state=42 + abs(hash(h_crop)) % 10000,
                    replace=True,
                ).copy()
                sample_w["crop_key"] = h_crop
                rain_daily = sample_w["average_rain_fall_mm_per_year"] / 365.0
                temp_eff = 1.0 - np.abs(sample_w["avg_temp"] - h_cfg["opt_temp"]) * 0.015
                rain_eff = 1.0 - np.abs(rain_daily - h_cfg["opt_rain"]) * 0.025
                mod = np.clip(temp_eff * rain_eff, 0.65, 1.35)
                rng = np.random.default_rng(abs(hash(h_crop)) % 10000)
                noise = rng.normal(0.0, 0.06, size=len(sample_w))
                sample_w["yield_t_ha"] = np.clip(h_cfg["base"] * (mod + noise), 1.0, 130.0)
                if "pesticides_tonnes" in df.columns:
                    sample_w["pesticides_tonnes"] = 0.0

                synthetic_rows.append(sample_w)

            if synthetic_rows:
                df = pd.concat([df] + synthetic_rows, ignore_index=True)

            # Convert annual rainfall to daily mm so it shares scale with live rainfall
            df["rain_mm_day"] = df["average_rain_fall_mm_per_year"] / 365.0

            # Estimate relative humidity (%) from rainfall and temperature proxy, bounded [30, 95]
            rain_factor = np.clip(df["rain_mm_day"] * 4.0, 0, 30)
            temp_factor = np.clip((35 - df["avg_temp"]) * 0.8, -10, 15)
            df["est_humidity"] = np.clip(55.0 + rain_factor + temp_factor, 30.0, 95.0)

        # ── Train / Val split ────────────────────────────────────────────────
        df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        n_val = int(len(df) * val_fraction)
        if split == "val":
            df = df.iloc[:n_val]
        else:
            df = df.iloc[n_val:]

        # ── Feature normalisation (Weather only: temp, humidity, rainfall) ──
        norm = config.TABULAR_NORM

        def z(col, key):
            return (df[col] - norm[key]["mean"]) / norm[key]["std"]

        self.features = np.stack([
            z("avg_temp",     "temperature").values,
            z("est_humidity", "humidity").values,
            z("rain_mm_day",  "rainfall").values,
        ], axis=1).astype(np.float32)

        self.labels = df["yield_t_ha"].values.astype(np.float32)
        self.crops  = df["crop_key"].values

        print(f"  [YieldDataset] {split}: {len(self.features)} rows | yield range: "
              f"{self.labels.min():.2f}–{self.labels.max():.2f} t/ha")

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        feat  = torch.tensor(self.features[idx], dtype=torch.float32)
        label = torch.tensor([self.labels[idx]],  dtype=torch.float32)
        return feat, label


# ─────────────────────────────────────────────────────────────────────────────
#   3. MultiModalDataset  (joint training)                                  
# ─────────────────────────────────────────────────────────────────────────────

class MultiModalDataset(Dataset):
    """
    Pairs each disease image with a tabular weather row from the same crop.
    Used for multi-task training of MultiModalAeroCropNet.

    Returns per item:
        image        : FloatTensor (3, 224, 224)
        tabular      : FloatTensor (3,)  # [temperature, humidity, rainfall]
        disease_label: int
        yield_t_ha   : FloatTensor (1,)
    """

    def __init__(
        self,
        image_root: str,
        yield_csv:  str,
        split:      str = "train",
        transform=None,
        max_per_class: int | None = None,
        classes: list[str] | None = None,
    ):
        self.split         = split
        self.img_dataset   = PlantDiseaseDataset(image_root, transform=transform, max_per_class=max_per_class, classes=classes)
        self.yield_dataset = YieldDataset(yield_csv, split=split)

        # Build crop -> [tabular_indices] lookup
        self._build_crop_index()

    @property
    def classes(self) -> list[str]:
        return self.img_dataset.classes

    @property
    def num_classes(self) -> int:
        return self.img_dataset.num_classes

    def _build_crop_index(self):
        """Index yield rows by crop key for efficient lookup."""
        self.crop_idx: dict[str, list[int]] = {}
        for i, crop in enumerate(self.yield_dataset.crops):
            self.crop_idx.setdefault(crop, []).append(i)

        # Build image-level crop key (from folder name prefix)
        folder_lower_to_crop = {k.lower(): v for k, v in FOLDER_TO_CROP.items()}
        self.img_crops: list[str] = []
        for img_path, _ in self.img_dataset.samples:
            folder  = img_path.parent.name
            prefix  = folder.split("___")[0]
            crop_key = FOLDER_TO_CROP.get(prefix) or folder_lower_to_crop.get(prefix.lower(), "maize")
            self.img_crops.append(crop_key)

    def __len__(self) -> int:
        return len(self.img_dataset)

    def __getitem__(self, idx: int):
        image, disease_label = self.img_dataset[idx]

        # Find matching yield row for this crop
        crop_key = self.img_crops[idx]
        candidates = self.crop_idx.get(crop_key)
        if not candidates:
            # Fallback
            row_idx = (idx % len(self.yield_dataset)) if self.split == "val" else random.randint(0, len(self.yield_dataset) - 1)
        else:
            # Deterministic pairing for validation to guarantee reproducible evaluation metrics across epochs
            row_idx = candidates[idx % len(candidates)] if self.split == "val" else random.choice(candidates)

        tabular, yield_t_ha = self.yield_dataset[row_idx]

        return image, tabular, disease_label, yield_t_ha
