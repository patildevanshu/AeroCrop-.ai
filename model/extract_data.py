"""
AeroCrop.ai  Dataset Extraction Helper

Extracts both dataset zips from the Downloads folder into the
project's data/ directory.

Usage:
    python model/extract_data.py

Extracts:
    - archive.zip       data/New Plant Diseases Dataset(Augmented)/
    - archive (1).zip   data/yield_df.csv  (and other CSVs)
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path

# Paths
BASE_DIR      = Path(__file__).parent.parent
DATA_DIR      = BASE_DIR / "data"
DOWNLOADS_DIR = Path.home() / "Downloads"

DISEASE_ZIP   = DOWNLOADS_DIR / "archive.zip"
YIELD_ZIP     = DOWNLOADS_DIR / "archive (1).zip"


def extract_zip(zip_path: Path, dest_dir: Path, desc: str):
    if not zip_path.exists():
        print(f"   Not found: {zip_path}")
        return False

    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n   Extracting {desc}")
    print(f"     From : {zip_path}")
    print(f"     To   : {dest_dir}")
    print(f"     Size : {zip_path.stat().st_size / 1e9:.2f} GB")
    print("     This may take a few minutes for the disease dataset...\n")

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.namelist()
        total   = len(members)
        for i, member in enumerate(members, 1):
            zf.extract(member, dest_dir)
            if i % 5000 == 0 or i == total:
                pct = i / total * 100
                bar = "" * int(pct / 5) + "" * (20 - int(pct / 5))
                print(f"\r     [{bar}] {pct:5.1f}%  ({i:,}/{total:,} files)", end="", flush=True)

    print(f"\n   Done: {desc}")
    return True


def main():
    print("\n" + "=" * 60)
    print("    AeroCrop.ai  Dataset Extraction")
    print("=" * 60)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    #  1. Yield dataset (small  ~1 MB) 
    yield_csv_dest = DATA_DIR / "yield_df.csv"
    if yield_csv_dest.exists():
        print(f"\n   Yield data already extracted: {yield_csv_dest}")
    else:
        ok = extract_zip(YIELD_ZIP, DATA_DIR, "Yield Dataset CSVs")
        if ok:
            # Flatten if needed  move CSVs directly to data/
            for csv_file in DATA_DIR.rglob("*.csv"):
                target = DATA_DIR / csv_file.name
                if csv_file != target:
                    shutil.move(str(csv_file), str(target))
            print(f"   Yield CSVs extracted to {DATA_DIR}")

    #  2. Disease dataset (large  ~2.9 GB) 
    disease_train = DATA_DIR / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train"
    # Also accept the already-correct double-nested path (zip extracts this way)
    if disease_train.exists() and len(list(disease_train.iterdir())) == 38:
        print(f"\n   Disease dataset already extracted: {disease_train}")
    else:
        extract_zip(DISEASE_ZIP, DATA_DIR, "Disease Dataset (87,900 images)")

    #  Summary 
    print("\n" + "=" * 60)
    print("  Extraction complete. Directory structure:")
    for item in sorted(DATA_DIR.iterdir()):
        if item.is_dir():
            n = sum(1 for _ in item.rglob("*") if _.is_file())
            print(f"     {item.name}/   ({n:,} files)")
        else:
            print(f"     {item.name}   ({item.stat().st_size / 1e3:.0f} KB)")

    print("\n  Next step  train the model:")
    print("    python model/train.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
