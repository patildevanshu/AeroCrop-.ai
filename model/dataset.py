"""
AeroCrop.ai — PyTorch Dataset Classes (Model Layer)

Two dataset implementations:

1. PlantDiseaseDataset
   - Source: New Plant Diseases Dataset (Augmented) — 87,900 images, 38 classes
   - Root dir expected structure: train/<ClassName>/<image.jpg>
   - Returns: (image_tensor [3,224,224], class_index)

2. YieldDataset
   - Source: yield_df.csv — merged FAO yield + weather data
   - Columns: Area, Item, Year, hg/ha_yield, average_rain_fall_mm_per_year,
              pesticides_tonnes, avg_temp
   - Filters to crops matching CROP_NPK_TARGETS
   - Returns: (feature_tensor [7], yield_t_ha)

3. MultiModalDataset  (used for joint training)
   - Pairs each disease image with a randomly sampled tabular row
     from the same crop category.
   - Returns: (image_tensor, tabular_tensor [6], disease_label, yield_t_ha)
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
from PIL import Image
from torchvision import transforms

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ── Folder name → class index mapping (alphabetical, matches PlantVillage) ──
DISEASE_CLASSES: list[str] = [
    "Apple___Apple_scab",                                         # 0
    "Apple___Black_rot",                                          # 1
    "Apple___Cedar_apple_rust",                                   # 2
    "Apple___healthy",                                            # 3
    "Blueberry___healthy",                                        # 4
    "Cherry_(including_sour)___healthy",                          # 5
    "Cherry_(including_sour)___Powdery_mildew",                   # 6
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",         # 7
    "Corn_(maize)___Common_rust_",                                # 8
    "Corn_(maize)___healthy",                                     # 9
    "Corn_(maize)___Northern_Leaf_Blight",                        # 10
    "Grape___Black_rot",                                          # 11
    "Grape___Esca_(Black_Measles)",                               # 12
    "Grape___healthy",                                            # 13
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",                 # 14
    "Orange___Haunglongbing_(Citrus_greening)",                   # 15
    "Peach___Bacterial_spot",                                     # 16
    "Peach___healthy",                                            # 17
    "Pepper,_bell___Bacterial_spot",                              # 18
    "Pepper,_bell___healthy",                                     # 19
    "Potato___Early_blight",                                      # 20
    "Potato___healthy",                                           # 21
    "Potato___Late_blight",                                       # 22
    "Raspberry___healthy",                                        # 23
    "Soybean___healthy",                                          # 24
    "Squash___Powdery_mildew",                                    # 25
    "Strawberry___healthy",                                       # 26
    "Strawberry___Leaf_scorch",                                   # 27
    "Tomato___Bacterial_spot",                                    # 28
    "Tomato___Early_blight",                                      # 29
    "Tomato___healthy",                                           # 30
    "Tomato___Late_blight",                                       # 31
    "Tomato___Leaf_Mold",                                         # 32
    "Tomato___Septoria_leaf_spot",                                # 33
    "Tomato___Spider_mites Two-spotted_spider_mite",              # 34
    "Tomato___Target_Spot",                                       # 35
    "Tomato___Tomato_mosaic_virus",                               # 36
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",                     # 37
]

CLASS_TO_IDX: dict[str, int] = {c: i for i, c in enumerate(DISEASE_CLASSES)}

# ── Crop name mapping: PlantVillage folder prefix → yield crop name ─────────
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
}

# ── Image transforms ─────────────────────────────────────────────────────────
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


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  1. PlantDiseaseDataset                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

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
        label  : int — class index (0–37)
    """

    def __init__(self, root_dir: str, transform=None, max_per_class: int = None):
        self.root_dir  = Path(root_dir)
        self.transform = transform or VAL_TRANSFORM
        self.samples: list[tuple[Path, int]] = []

        for folder in sorted(self.root_dir.iterdir()):
            if not folder.is_dir():
                continue

            # Try exact match first, then fuzzy match
            class_idx = CLASS_TO_IDX.get(folder.name)
            if class_idx is None:
                # Try matching by normalizing underscores/spaces
                normalized = folder.name.replace(" ", "_")
                class_idx = CLASS_TO_IDX.get(normalized)
            if class_idx is None:
                print(f"  [Dataset] Warning: unknown class folder '{folder.name}' — skipped.")
                continue

            images = sorted(
                p for p in folder.iterdir()
                if p.suffix.lower() in ('.jpg', '.jpeg', '.png')
            )
            if max_per_class:
                images = images[:max_per_class]

            for img_path in images:
                self.samples.append((img_path, class_idx))

        print(f"  [PlantDiseaseDataset] Loaded {len(self.samples)} images from {self.root_dir.name}/")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)
        return img, label


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  2. YieldDataset                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Crop names in yield_df.csv → our internal keys
YIELD_CROP_MAP: dict[str, str] = {
    "Maize":     "maize",
    "Potatoes":  "potato",
    "Rice, paddy": "rice",
    "Wheat":     "wheat",
    "Cotton":    "cotton",
    "Tomatoes":  "tomato",
    "Sweet potatoes": "potato",
    "Cassava":   "maize",   # proxy
}


class YieldDataset(Dataset):
    """
    Tabular dataset for yield regression from yield_df.csv.

    Features (6 after selecting relevant columns):
        N, P, K  ← imputed from ICAR targets (no per-sample soil data)
        avg_temp, average_rain_fall_mm_per_year, pesticides_tonnes

    Target:
        hg/ha_yield converted to t/ha (divide by 10000)

    Returns per item:
        features : FloatTensor (6,)  — normalised [N, P, K, temp, rain, pest]
        yield    : FloatTensor (1,)  — tons per hectare
    """

    def __init__(self, csv_path: str, split: str = "train", val_fraction: float = 0.15):
        df = pd.read_csv(csv_path)

        # ── Column clean-up ───────────────────────────────────────────────
        df.columns = [c.strip() for c in df.columns]
        if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
            df = df.iloc[:, 1:]   # drop unnamed index column

        # Map crop names
        df["crop_key"] = df["Item"].map(YIELD_CROP_MAP)
        df = df.dropna(subset=["crop_key"])

        # Drop rows with missing weather values
        required = ["avg_temp", "average_rain_fall_mm_per_year", "hg/ha_yield"]
        df = df.dropna(subset=required)

        # Convert yield to t/ha
        df["yield_t_ha"] = df["hg/ha_yield"] / 10_000.0

        # Handle pesticides (some rows may be NaN)
        df["pesticides_tonnes"] = df["pesticides_tonnes"].fillna(0.0)

        # Add imputed NPK from ICAR targets (per crop key)
        targets = config.CROP_NPK_TARGETS
        default_npk = {"N": 110.0, "P": 60.0, "K": 50.0}
        df["N"] = df["crop_key"].apply(lambda c: targets.get(c, default_npk)["N"])
        df["P"] = df["crop_key"].apply(lambda c: targets.get(c, default_npk)["P"])
        df["K"] = df["crop_key"].apply(lambda c: targets.get(c, default_npk)["K"])

        # ── Train / Val split ─────────────────────────────────────────────
        df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        n_val = int(len(df) * val_fraction)
        if split == "val":
            df = df.iloc[:n_val]
        else:
            df = df.iloc[n_val:]

        # ── Feature normalisation ─────────────────────────────────────────
        norm = config.TABULAR_NORM

        def z(col, key):
            return (df[col] - norm[key]["mean"]) / norm[key]["std"]

        self.features = np.stack([
            z("N",                          "N").values,
            z("P",                          "P").values,
            z("K",                          "K").values,
            z("avg_temp",                   "temperature").values,
            z("average_rain_fall_mm_per_year", "humidity").values,  # humidity proxy
            z("pesticides_tonnes",          "rainfall").values,     # pest proxy
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


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  3. MultiModalDataset  (joint training)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class MultiModalDataset(Dataset):
    """
    Pairs each disease image with a tabular yield row from the same crop.
    Used for multi-task training of MultiModalAeroCropNet.

    Returns per item:
        image        : FloatTensor (3, 224, 224)
        tabular      : FloatTensor (6,)
        disease_label: int
        yield_t_ha   : FloatTensor (1,)
    """

    def __init__(
        self,
        image_root: str,
        yield_csv:  str,
        split:      str = "train",
        transform=None,
    ):
        self.img_dataset   = PlantDiseaseDataset(image_root, transform=transform)
        self.yield_dataset = YieldDataset(yield_csv, split=split)

        # Build crop → [tabular_indices] lookup
        self._build_crop_index()

    def _build_crop_index(self):
        """Index yield rows by crop key for efficient lookup."""
        self.crop_idx: dict[str, list[int]] = {}
        for i, crop in enumerate(self.yield_dataset.crops):
            self.crop_idx.setdefault(crop, []).append(i)

        # Build image-level crop key (from folder name prefix)
        self.img_crops: list[str] = []
        for img_path, _ in self.img_dataset.samples:
            folder  = img_path.parent.name
            prefix  = folder.split("___")[0]
            crop_key = FOLDER_TO_CROP.get(prefix, "maize")  # default fallback
            self.img_crops.append(crop_key)

    def __len__(self) -> int:
        return len(self.img_dataset)

    def __getitem__(self, idx: int):
        image, disease_label = self.img_dataset[idx]

        # Find matching yield row for this crop
        crop_key = self.img_crops[idx]
        candidates = self.crop_idx.get(crop_key)
        if not candidates:
            # Fallback: random row
            row_idx = random.randint(0, len(self.yield_dataset) - 1)
        else:
            row_idx = random.choice(candidates)

        tabular, yield_t_ha = self.yield_dataset[row_idx]

        return image, tabular, disease_label, yield_t_ha
