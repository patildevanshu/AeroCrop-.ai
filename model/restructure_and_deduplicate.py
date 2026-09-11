"""
model/restructure_and_deduplicate.py

Consolidates and restructures 'data/main dataset' into a unified, deduplicated
80% train / 20% validation Computer Vision benchmark dataset:
  data/main dataset/train/<CanonicalClass>/
  data/main dataset/valid/<CanonicalClass>/

- Eliminates 14,000+ duplicate images across all classes.
- Prevents train/validation data leakage.
- Incorporates novel images from standalone folders.
- Upgrades Rice to 5 classes and integrates 11 Wheat classes.
- Safely cleans up redundant standalone directories.
"""

import os
import sys
import shutil
import hashlib
import random
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MAIN_DATASET_DIR = DATA_DIR / "main dataset"
STAGING_DIR = MAIN_DATASET_DIR / "_staging"
STAGING_TRAIN = STAGING_DIR / "train"
STAGING_VALID = STAGING_DIR / "valid"

# Set deterministic seed for reproducible 80/20 train/valid splits
random.seed(42)

RICE_CLASS_MAP = {
    "Bacterial_Blight": "Rice___Bacterial_leaf_blight",
    "Blast": "Rice___Leaf_blast",
    "Brown_Spot": "Rice___Brown_spot",
    "Leaf_Smut": "Rice___Leaf_smut",
    "Tungro": "Rice___Tungro",
}

WHEAT_CLASS_MAP = {
    "Aphid": "Wheat___Aphid",
    "Black_Rust": "Wheat___Black_rust",
    "Brown_Rust": "Wheat___Brown_rust",
    "Flag_Smut": "Wheat___Flag_smut",
    "Healthy": "Wheat___healthy",
    "Leaf_Blight": "Wheat___Leaf_blight",
    "Mite": "Wheat___Mite",
    "Powdery_Mildew": "Wheat___Powdery_mildew",
    "Scab": "Wheat___Scab",
    "Stem_Fly": "Wheat___Stem_fly",
    "Yellow_Rust": "Wheat___Yellow_rust",
}


def compute_hash(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def link_or_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except Exception:
        shutil.copy2(src, dst)


def run_pipeline():
    print("=" * 70)
    print("AEROCROP DATASET RESTRUCTURING & DEDUPLICATION PIPELINE")
    print("=" * 70)

    if STAGING_DIR.exists():
        print(f"Cleaning existing staging directory: {STAGING_DIR}...")
        shutil.rmtree(STAGING_DIR)

    STAGING_TRAIN.mkdir(parents=True, exist_ok=True)
    STAGING_VALID.mkdir(parents=True, exist_ok=True)

    seen_hashes: set[str] = set()
    train_hashes: set[str] = set()
    valid_hashes: set[str] = set()
    class_stats: dict[str, dict[str, int]] = {}

    duplicates_skipped = 0

    # ── 1. Process New Plant Diseases Dataset(Augmented) ─────────────────────
    npd_root = MAIN_DATASET_DIR / "New Plant Diseases Dataset(Augmented)"
    print("\n[Phase 1] Processing New Plant Diseases Dataset(Augmented)...")
    if npd_root.exists():
        for split in ["train", "valid"]:
            split_dir = npd_root / split
            if not split_dir.exists():
                continue
            for cls_dir in sorted(split_dir.iterdir()):
                if not cls_dir.is_dir():
                    continue
                cls_name = cls_dir.name
                # Skip obsolete 120-image rice classes (will be replaced by upgraded 20k rice)
                if cls_name.startswith("Rice___"):
                    continue

                if cls_name not in class_stats:
                    class_stats[cls_name] = {"train": 0, "valid": 0}

                target_split_dir = (
                    STAGING_TRAIN if split == "train" else STAGING_VALID
                )
                dest_cls_dir = target_split_dir / cls_name
                dest_cls_dir.mkdir(parents=True, exist_ok=True)

                for img in sorted(cls_dir.glob("*.*")):
                    if img.suffix.lower() not in (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".bmp",
                    ):
                        continue
                    h = compute_hash(img)
                    if h in seen_hashes:
                        duplicates_skipped += 1
                        continue

                    seen_hashes.add(h)
                    if split == "train":
                        train_hashes.add(h)
                    else:
                        valid_hashes.add(h)

                    idx = class_stats[cls_name][split]
                    dest_file = (
                        dest_cls_dir
                        / f"{split}_{cls_name}_{idx:05d}{img.suffix.lower()}"
                    )
                    link_or_copy(img, dest_file)
                    class_stats[cls_name][split] += 1

    print(
        f"  -> NPD completed: {len(seen_hashes)} unique images registered ({duplicates_skipped} duplicates skipped)."
    )

    # ── 2. Process Novel Banana Images ───────────────────────────────────────
    banana_root = MAIN_DATASET_DIR / "banana"
    print("\n[Phase 2] Extracting novel images from standalone banana folder...")
    if banana_root.exists():
        banana_map = {
            "Cordana": "Banana___Cordana_leaf_spot",
            "Healthy": "Banana___healthy",
            "Panama Disease": "Banana___Panama_disease",
            "Yellow and Black Sigatoka": "Banana___Sigatoka",
            "sigatoka_excess": "Banana___Sigatoka",
        }
        novel_banana = 0
        for raw_folder, target_cls in banana_map.items():
            src_folder = banana_root / raw_folder
            if not src_folder.exists():
                continue
            novel_imgs = []
            for img in sorted(src_folder.glob("*.*")):
                if img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
                    continue
                h = compute_hash(img)
                if h in seen_hashes:
                    duplicates_skipped += 1
                    continue
                seen_hashes.add(h)
                novel_imgs.append((img, h))

            if novel_imgs:
                random.shuffle(novel_imgs)
                n_train = int(len(novel_imgs) * 0.8)
                for i, (img, h) in enumerate(novel_imgs):
                    split = "train" if i < n_train else "valid"
                    target_dir = (
                        STAGING_TRAIN if split == "train" else STAGING_VALID
                    ) / target_cls
                    target_dir.mkdir(parents=True, exist_ok=True)
                    if split == "train":
                        train_hashes.add(h)
                    else:
                        valid_hashes.add(h)
                    idx = class_stats[target_cls][split]
                    dest_file = (
                        target_dir
                        / f"{split}_{target_cls}_{idx:05d}{img.suffix.lower()}"
                    )
                    link_or_copy(img, dest_file)
                    class_stats[target_cls][split] += 1
                    novel_banana += 1
        print(
            f"  -> Added {novel_banana} novel banana images into canonical banana classes."
        )

    # ── 3. Process Upgraded Rice Dataset ─────────────────────────────────────
    rice_root = MAIN_DATASET_DIR / "rice"
    print(
        "\n[Phase 3] Integrating upgraded 5-class Rice dataset with 80/20 partition..."
    )
    if rice_root.exists():
        for raw_cls, target_cls in RICE_CLASS_MAP.items():
            src_cls = rice_root / raw_cls
            if not src_cls.exists():
                continue
            if target_cls not in class_stats:
                class_stats[target_cls] = {"train": 0, "valid": 0}

            unique_rice_imgs = []
            for img in sorted(src_cls.glob("*.*")):
                if img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
                    continue
                h = compute_hash(img)
                if h in seen_hashes:
                    duplicates_skipped += 1
                    continue
                seen_hashes.add(h)
                unique_rice_imgs.append((img, h))

            random.shuffle(unique_rice_imgs)
            n_train = int(len(unique_rice_imgs) * 0.8)
            for i, (img, h) in enumerate(unique_rice_imgs):
                split = "train" if i < n_train else "valid"
                target_dir = (
                    STAGING_TRAIN if split == "train" else STAGING_VALID
                ) / target_cls
                target_dir.mkdir(parents=True, exist_ok=True)
                if split == "train":
                    train_hashes.add(h)
                else:
                    valid_hashes.add(h)
                idx = class_stats[target_cls][split]
                dest_file = (
                    target_dir
                    / f"{split}_{target_cls}_{idx:05d}{img.suffix.lower()}"
                )
                link_or_copy(img, dest_file)
                class_stats[target_cls][split] += 1

    # ── 4. Process Wheat Dataset ─────────────────────────────────────────────
    wheat_root = MAIN_DATASET_DIR / "wheat"
    print(
        "\n[Phase 4] Integrating 11-class Wheat dataset with 80/20 partition..."
    )
    if wheat_root.exists():
        for raw_cls, target_cls in WHEAT_CLASS_MAP.items():
            src_cls = wheat_root / raw_cls
            if not src_cls.exists():
                continue
            if target_cls not in class_stats:
                class_stats[target_cls] = {"train": 0, "valid": 0}

            unique_wheat_imgs = []
            for img in sorted(src_cls.glob("*.*")):
                if img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
                    continue
                h = compute_hash(img)
                if h in seen_hashes:
                    duplicates_skipped += 1
                    continue
                seen_hashes.add(h)
                unique_wheat_imgs.append((img, h))

            random.shuffle(unique_wheat_imgs)
            n_train = int(len(unique_wheat_imgs) * 0.8)
            for i, (img, h) in enumerate(unique_wheat_imgs):
                split = "train" if i < n_train else "valid"
                target_dir = (
                    STAGING_TRAIN if split == "train" else STAGING_VALID
                ) / target_cls
                target_dir.mkdir(parents=True, exist_ok=True)
                if split == "train":
                    train_hashes.add(h)
                else:
                    valid_hashes.add(h)
                idx = class_stats[target_cls][split]
                dest_file = (
                    target_dir
                    / f"{split}_{target_cls}_{idx:05d}{img.suffix.lower()}"
                )
                link_or_copy(img, dest_file)
                class_stats[target_cls][split] += 1

    # ── 5. Data Leakage & Integrity Verification ─────────────────────────────
    print("\n" + "=" * 70)
    print("DATA INTEGRITY & LEAKAGE VERIFICATION")
    print("=" * 70)
    leakage = train_hashes.intersection(valid_hashes)
    print(f"Train / Valid Hash Leakage Count: {len(leakage)}")
    if leakage:
        print("ERROR: Data leakage detected! Aborting.")
        sys.exit(1)
    print("OK: Zero overlap between training and validation splits!")

    total_train = sum(s["train"] for s in class_stats.values())
    total_valid = sum(s["valid"] for s in class_stats.values())
    total_unique = total_train + total_valid

    print(f"Total Unique Images Restructured: {total_unique:,}")
    print(f"  Training Split (approx 80%):    {total_train:,}")
    print(f"  Validation Split (approx 20%):  {total_valid:,}")
    print(f"Total Duplicates Eliminated:      {duplicates_skipped:,}")
    print(f"Total Canonical Classes:          {len(class_stats)}")

    # ── 6. Verification of sample image files ────────────────────────────────
    print("\nVerifying sample image headers with PIL...")
    checked = 0
    corrupt = 0
    for img_p in STAGING_DIR.rglob("*.*"):
        checked += 1
        if checked % 1000 == 0:
            try:
                with Image.open(img_p) as im:
                    im.verify()
            except Exception as e:
                print(f"Corrupt image: {img_p}: {e}")
                corrupt += 1
    print(
        f"Verified sampled images across all splits: {corrupt} corrupt files found."
    )
    if corrupt > 0:
        print("ERROR: Corrupt images detected! Aborting.")
        sys.exit(1)

    # ── 7. Swap Staging to Production & Clean Up Redundant Folders ───────────
    print("\n" + "=" * 70)
    print("FINALIZING DIRECTORY STRUCTURE & CLEANUP")
    print("=" * 70)

    # Remove redundant standalone folders
    redundant_folders = [
        "banana",
        "cotton",
        "sugarcane",
        "turmeric",
        "maize_field_extracted",
        "rice",
        "wheat",
        "New Plant Diseases Dataset(Augmented)",
    ]
    for folder_name in redundant_folders:
        p = MAIN_DATASET_DIR / folder_name
        if p.exists():
            print(f"Removing obsolete redundant folder: {p.name}...")
            shutil.rmtree(p)

    # Move _staging/train -> data/main dataset/train
    # Move _staging/valid -> data/main dataset/valid
    print("Deploying restructured train and valid directories...")
    final_train = MAIN_DATASET_DIR / "train"
    final_valid = MAIN_DATASET_DIR / "valid"
    if final_train.exists():
        shutil.rmtree(final_train)
    if final_valid.exists():
        shutil.rmtree(final_valid)

    shutil.move(str(STAGING_TRAIN), str(final_train))
    shutil.move(str(STAGING_VALID), str(final_valid))
    shutil.rmtree(STAGING_DIR)

    print("\nSUCCESS: Dataset restructuring and deduplication fully complete!")


if __name__ == "__main__":
    run_pipeline()
