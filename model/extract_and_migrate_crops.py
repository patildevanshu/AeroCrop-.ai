"""
model/extract_and_migrate_crops.py

Extracts Wheat (11 classes, ~2,101 images) and upgraded Rice (5 classes, ~6,112 images)
from the 20k multi-class crop disease dataset archive into 'data/main dataset/'.
Replaces obsolete 120-image rice placeholder and validates extracted images.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "main dataset"
WHEAT_DIR = DATA_DIR / "wheat"
RICE_DIR = DATA_DIR / "rice"

ARCHIVE_PATH = Path(r"C:\Users\devan\Downloads\archive (9).zip")

WHEAT_MAP = {
    "Flag Smut": "Flag_Smut",
    "Healthy Wheat": "Healthy",
    "Wheat Brown leaf Rust": "Brown_Rust",
    "Wheat Brown leaf rust": "Brown_Rust",
    "Wheat Stem fly": "Stem_Fly",
    "Wheat aphid": "Aphid",
    "Wheat black rust": "Black_Rust",
    "Wheat leaf blight": "Leaf_Blight",
    "Wheat mite": "Mite",
    "Wheat powdery mildew": "Powdery_Mildew",
    "Wheat scab": "Scab",
    "Wheat___Yellow_Rust": "Yellow_Rust",
}

RICE_MAP = {
    "Becterial Blight in Rice": "Bacterial_Blight",
    "Brownspot": "Brown_Spot",
    "Leaf smut": "Leaf_Smut",
    "Rice Blast": "Blast",
    "Tungro": "Tungro",
}


def run_extraction():
    if not ARCHIVE_PATH.exists():
        print(f"Error: Archive not found at {ARCHIVE_PATH}")
        sys.exit(1)

    print(f"Opening archive: {ARCHIVE_PATH} ({ARCHIVE_PATH.stat().st_size / 1e9:.2f} GB)...")

    # Ensure target dirs exist
    WHEAT_DIR.mkdir(parents=True, exist_ok=True)
    RICE_DIR.mkdir(parents=True, exist_ok=True)

    # Clean old rice placeholder if present
    old_rice_dir = RICE_DIR / "rice_leaf_diseases"
    if old_rice_dir.exists():
        print(f"Removing obsolete rice placeholder: {old_rice_dir}")
        shutil.rmtree(old_rice_dir)

    extracted_counts = {"wheat": 0, "rice": 0}
    class_counts = {}

    with zipfile.ZipFile(ARCHIVE_PATH, "r") as zf:
        namelist = zf.namelist()
        total_items = len(namelist)
        print(f"Total entries in archive: {total_items}")

        for i, name in enumerate(namelist):
            if name.endswith("/"):
                continue

            parts = [p for p in name.split("/") if p]
            if len(parts) < 3:
                continue

            split = parts[0].lower()  # train or validation
            raw_class = parts[1]
            filename = parts[-1]

            target_crop = None
            dest_folder = None
            canonical_class = None

            if raw_class in WHEAT_MAP:
                target_crop = "wheat"
                canonical_class = WHEAT_MAP[raw_class]
                dest_folder = WHEAT_DIR / canonical_class
            elif raw_class in RICE_MAP:
                target_crop = "rice"
                canonical_class = RICE_MAP[raw_class]
                dest_folder = RICE_DIR / canonical_class

            if target_crop and dest_folder:
                dest_folder.mkdir(parents=True, exist_ok=True)
                # Prefix with split to prevent collision between train and validation files
                clean_name = f"{split}_{filename}"
                dest_file = dest_folder / clean_name

                # Extract file
                with zf.open(name) as src, open(dest_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)

                extracted_counts[target_crop] += 1
                key = f"{target_crop}/{canonical_class}"
                class_counts[key] = class_counts.get(key, 0) + 1

            if (i + 1) % 2500 == 0 or (i + 1) == total_items:
                print(
                    f"  Processed {i + 1}/{total_items} entries... "
                    f"(Extracted Wheat: {extracted_counts['wheat']}, Rice: {extracted_counts['rice']})"
                )

    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total Wheat Images Extracted: {extracted_counts['wheat']}")
    print(f"Total Rice Images Extracted:  {extracted_counts['rice']}")
    print("-" * 60)
    print("Class Breakdown:")
    for cls, count in sorted(class_counts.items()):
        print(f"  {cls}: {count} images")

    # Integrity verification
    print("\nVerifying image integrity...")
    corrupt_files = 0
    sample_checked = 0
    for crop_dir in [WHEAT_DIR, RICE_DIR]:
        for img_path in crop_dir.rglob("*.*"):
            if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                sample_checked += 1
                if sample_checked % 1000 == 0:
                    try:
                        with Image.open(img_path) as img:
                            img.verify()
                    except Exception as e:
                        print(f"Corrupt image found: {img_path}: {e}")
                        corrupt_files += 1

    print(
        f"Integrity check complete. Sampled images verified successfully with {corrupt_files} errors."
    )


if __name__ == "__main__":
    run_extraction()
