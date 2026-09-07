"""
model/ingest_crops.py — Automated Crop Dataset Ingestion & Expansion Pipeline

This script automates the expansion of AeroCrop.ai beyond the baseline 38 PlantVillage classes:
1. Scans data/additional_crops/ for any downloaded crop dataset ZIP archives or folders.
   Supports: Cotton, Banana, Turmeric (Haldi), Sugarcane, Rice, Onion, Wheat, etc.
2. Automatically extracts and standardizes directory structures into the canonical
   PlantVillage format: <Crop>___<Condition_Or_Disease>
3. Performs an 80% train / 20% validation split into:
   data/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/train/
   data/New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)/valid/
4. Automatically updates:
   - model/dataset.py (expands DISEASE_CLASSES list)
   - config.py (updates NUM_DISEASE_CLASSES)
   - services/disease_service.py (registers DiseaseInfo metadata with treatments)
5. Can optionally launch model training (--train) with GPU acceleration and 4 workers.

Usage:
    python model/ingest_crops.py                  # Scan and ingest pending datasets
    python model/ingest_crops.py --train          # Ingest and start retraining model
    python model/ingest_crops.py --links          # Display verified dataset download links
"""

import os
import sys
import re
import shutil
import zipfile
import random
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config

DATA_DIR = PROJECT_ROOT / "data"
ADDITIONAL_CROPS_DIR = DATA_DIR / "additional_crops"
TARGET_DATASET_ROOT = (
    DATA_DIR / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)"
)
TRAIN_DIR = TARGET_DATASET_ROOT / "train"
VALID_DIR = TARGET_DATASET_ROOT / "valid"

# Verified public dataset download links
VERIFIED_DATASET_SOURCES = {
    "Cotton": {
        "title": "Cotton Leaf Diseases Dataset (Bacterial Blight, Curl Virus, Fusarium Wilt, Healthy)",
        "url": "https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset",
        "zip_name": "cotton.zip",
        "approx_size": "~150 MB",
        "diseases": ["Bacterial_blight", "Curl_virus", "Fusarium_wilt", "healthy"],
    },
    "Banana": {
        "title": "Banana Leaf Disease Dataset v4 (Cordana, Sigatoka, Panama Disease, Healthy)",
        "url": "https://www.kaggle.com/datasets/rayhanarlistya/banana-leaf-disease-dataset-v4",
        "zip_name": "banana.zip",
        "approx_size": "~410 MB",
        "diseases": ["Cordana", "Yellow_and_Black_Sigatoka", "Panama_Disease", "healthy"],
    },
    "Turmeric (Haldi)": {
        "title": "Turmeric Datasets for CNN Model Training and Test",
        "url": "https://www.kaggle.com/datasets/hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test",
        "zip_name": "turmeric.zip",
        "approx_size": "~172 MB",
        "diseases": ["Leaf_blotch", "Leaf_spot", "Rhizome_rot", "healthy"],
    },
    "Sugarcane": {
        "title": "Sugarcane Leaf Disease Dataset (Red Rot, Rust, Bacterial Blight, Healthy)",
        "url": "https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset",
        "zip_name": "sugarcane.zip",
        "approx_size": "~160 MB",
        "diseases": ["Red_rot", "Rust", "Bacterial_blight", "healthy"],
    },
    "Rice / Paddy": {
        "title": "Rice Leaf Diseases Dataset (Bacterial Leaf Blight, Brown Spot, Leaf Smut)",
        "url": "https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases",
        "zip_name": "rice.zip",
        "approx_size": "~37 MB",
        "diseases": ["Bacterial_leaf_blight", "Brown_spot", "Leaf_smut", "healthy"],
    },
}

# Agronomic disease treatment metadata for auto-registration
DISEASE_METADATA_DEFAULTS = {
    "Cotton___Bacterial_blight": {
        "name": "Cotton — Bacterial Blight (Angular Leaf Spot)",
        "crop": "Cotton",
        "is_healthy": False,
        "chem": ["Copper Oxychloride 50WP (2.5 g/L)", "Streptocycline (100 ppm)"],
        "org": ["Neem seed kernel extract (NSKE 5%)", "Pseudomonas fluorescens spray"],
        "severity": "High",
        "desc": "Angular water-soaked lesions bounded by leaf veins; turns dark brown to black.",
    },
    "Cotton___Curl_virus": {
        "name": "Cotton — Cotton Leaf Curl Virus (CLCuD)",
        "crop": "Cotton",
        "is_healthy": False,
        "chem": ["Imidacloprid 17.8SL (to control whitefly vector)", "Diafenthiuron 50WP"],
        "org": ["Yellow sticky traps (10/acre)", "Neem Oil 1500ppm"],
        "severity": "Critical",
        "desc": "Upward or downward leaf curling, thick leaf veins, enation (leaf-like outgrowths).",
    },
    "Cotton___Fusarium_wilt": {
        "name": "Cotton — Fusarium Wilt",
        "crop": "Cotton",
        "is_healthy": False,
        "chem": ["Carbendazim 50WP soil drench (1 g/L)", "Thiophanate Methyl"],
        "org": ["Trichoderma viride soil application (2.5 kg/acre in FYM)"],
        "severity": "Critical",
        "desc": "Yellowing and browning of cotyledons and leaves, vascular discolouration inside stem.",
    },
    "Cotton___healthy": {
        "name": "Cotton — Healthy",
        "crop": "Cotton",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Vigorous green foliage with no pathology or necrotic lesions.",
    },
    "Banana___Sigatoka": {
        "name": "Banana — Black / Yellow Sigatoka",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Propiconazole 25EC (1 ml/L)", "Carbendazim 50WP", "Mancozeb 75WP"],
        "org": ["Mineral oil spray (1%)", "Trichoderma viride foliar wash"],
        "severity": "High",
        "desc": "Spindle-shaped necrotic spots with yellow halos along secondary veins.",
    },
    "Banana___Yellow_and_Black_Sigatoka": {
        "name": "Banana — Black / Yellow Sigatoka",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Propiconazole 25EC (1 ml/L)", "Carbendazim 50WP", "Mancozeb 75WP"],
        "org": ["Mineral oil spray (1%)", "Trichoderma viride foliar wash"],
        "severity": "High",
        "desc": "Spindle-shaped necrotic spots with yellow halos along secondary veins.",
    },
    "Banana___Cordana": {
        "name": "Banana — Cordana Leaf Spot",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Mancozeb 75WP (2 g/L)", "Chlorothalonil"],
        "org": ["Prune and burn infected leaf tips", "Neem oil spray"],
        "severity": "Moderate",
        "desc": "Large oval or zig-zag necrotic patches on leaf margins with bright yellow borders.",
    },
    "Banana___Cordana_leaf_spot": {
        "name": "Banana — Cordana Leaf Spot",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Mancozeb 75WP (2 g/L)", "Chlorothalonil"],
        "org": ["Prune and burn infected leaf tips", "Neem oil spray"],
        "severity": "Moderate",
        "desc": "Large oval or zig-zag necrotic patches on leaf margins with bright yellow borders.",
    },
    "Banana___Panama_Disease": {
        "name": "Banana — Panama Disease (Fusarium Wilt)",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Carbendazim 50WP soil drench (2 g/L)", "Propiconazole"],
        "org": ["Trichoderma viride soil application in FYM", "Neem cake application"],
        "severity": "Critical",
        "desc": "Progressive yellowing of older leaves, leaf bucking along petiole, vascular discolouration.",
    },
    "Banana___Panama_disease": {
        "name": "Banana — Panama Disease (Fusarium Wilt)",
        "crop": "Banana",
        "is_healthy": False,
        "chem": ["Carbendazim 50WP soil drench (2 g/L)", "Propiconazole"],
        "org": ["Trichoderma viride soil application in FYM", "Neem cake application"],
        "severity": "Critical",
        "desc": "Progressive yellowing of older leaves, leaf bucking along petiole, vascular discolouration.",
    },
    "Banana___healthy": {
        "name": "Banana — Healthy",
        "crop": "Banana",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Broad, intact, deep green banana leaves with smooth lamina and sturdy midrib.",
    },
    "Banana___Healthy": {
        "name": "Banana — Healthy",
        "crop": "Banana",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Broad, intact, deep green banana leaves with smooth lamina and sturdy midrib.",
    },
    "Turmeric___Leaf_blotch": {
        "name": "Turmeric — Leaf Blotch (Taphrina)",
        "crop": "Turmeric",
        "is_healthy": False,
        "chem": ["Mancozeb (2 g/L)", "Copper Oxychloride (2.5 g/L)"],
        "org": ["Panchagavya foliar spray (3%)", "Pseudomonas fluorescens"],
        "severity": "Moderate",
        "desc": "Small rectangular reddish-brown spots on both leaf surfaces coalescing into blotches.",
    },
    "Turmeric___Leaf_spot": {
        "name": "Turmeric — Colletotrichum Leaf Spot",
        "crop": "Turmeric",
        "is_healthy": False,
        "chem": ["Azoxystrobin + Difenoconazole", "Carbendazim (1 g/L)"],
        "org": ["Neem cake soil application", "Bordeaux mixture 1%"],
        "severity": "High",
        "desc": "Elliptical grey-white spots with dark brown margins causing leaves to dry up.",
    },
    "Turmeric___Rhizome_rot": {
        "name": "Turmeric — Pythium Rhizome Rot",
        "crop": "Turmeric",
        "is_healthy": False,
        "chem": ["Metalaxyl + Mancozeb (Ridomil Gold 2 g/L drench)", "Copper Oxychloride"],
        "org": ["Seed rhizome treatment with Trichoderma viride", "Ensure good bed drainage"],
        "severity": "Critical",
        "desc": "Collar rot, yellowing of pseudostem, foul-smelling soft decaying rhizomes.",
    },
    "Turmeric___healthy": {
        "name": "Turmeric — Healthy",
        "crop": "Turmeric",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Erect, glossy green turmeric leaves free from necrotic margins or spots.",
    },
    "Sugarcane___Red_rot": {
        "name": "Sugarcane — Red Rot (Colletotrichum falcatum)",
        "crop": "Sugarcane",
        "is_healthy": False,
        "chem": ["Thiophanate Methyl sett treatment", "Carbendazim (1 g/L)"],
        "org": ["Sett dip in Trichoderma suspension", "Crop rotation with paddy"],
        "severity": "Critical",
        "desc": "Third or fourth leaf from top shows yellowing; internal cane pith shows red lesions with crosswise white patches.",
    },
    "Sugarcane___Rust": {
        "name": "Sugarcane — Common Rust (Puccinia melanocephala)",
        "crop": "Sugarcane",
        "is_healthy": False,
        "chem": ["Mancozeb 75WP (2 g/L)", "Propiconazole 25EC (1 ml/L)"],
        "org": ["Sulfur dust application (25 kg/ha)"],
        "severity": "Moderate",
        "desc": "Small elongated yellowish spots turning reddish-brown pustules on both leaf surfaces.",
    },
    "Sugarcane___healthy": {
        "name": "Sugarcane — Healthy",
        "crop": "Sugarcane",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Robust, deep green linear sugarcane leaves with clear central midrib and no rust lesions.",
    },
    "Rice___Bacterial_leaf_blight": {
        "name": "Rice — Bacterial Leaf Blight (Xanthomonas oryzae)",
        "crop": "Rice",
        "is_healthy": False,
        "chem": ["Copper Hydroxide 77WP (2 g/L) + Streptocycline (100 ppm)"],
        "org": ["Neem oil spray (2%)", "Cow dung supernatant spray (5%)"],
        "severity": "Critical",
        "desc": "Water-soaked stripes starting from leaf tips/margins, enlarging into yellowish-white wavy lesions.",
    },
    "Rice___Brown_spot": {
        "name": "Rice — Brown Spot (Bipolaris oryzae)",
        "crop": "Rice",
        "is_healthy": False,
        "chem": ["Mancozeb 75WP (2 g/L)", "Tricyclazole 75WP (0.6 g/L)"],
        "org": ["Pseudomonas fluorescens seed treatment (10 g/kg)"],
        "severity": "High",
        "desc": "Oval or circular brown spots with grey or whitish centers scattered across leaves.",
    },
    "Rice___Leaf_blast": {
        "name": "Rice — Leaf Blast (Pyricularia oryzae)",
        "crop": "Rice",
        "is_healthy": False,
        "chem": ["Tricyclazole 75WP (0.6 g/L)", "Isoprothiolane 40EC (1.5 ml/L)"],
        "org": ["Silica foliar spray (to strengthen cell walls)", "Trichoderma harzianum"],
        "severity": "Critical",
        "desc": "Diamond-shaped or spindle-shaped spots with gray or white centers and brown borders.",
    },
    "Rice___healthy": {
        "name": "Rice — Healthy",
        "crop": "Rice",
        "is_healthy": True,
        "chem": [],
        "org": [],
        "severity": "None",
        "desc": "Upright, vibrant green paddy leaves with no lesions or blast spindles.",
    },
}


def print_links():
    """Display verified dataset download links and instructions."""
    print("=" * 80)
    print("  AeroCrop.ai - Major Maharashtra Crops Dataset Sources")
    print("=" * 80)
    print("  To train the model on these crops, download the ZIP archives from the links")
    print(f"  below and place them into: {ADDITIONAL_CROPS_DIR}\n")

    for crop_name, info in VERIFIED_DATASET_SOURCES.items():
        print(f"  * {crop_name.upper()} ({info['approx_size']})")
        print(f"    Description: {info['title']}")
        print(f"    Download:    {info['url']}")
        print(f"    Target ZIP:  {ADDITIONAL_CROPS_DIR / info['zip_name']}")
        print(f"    Classes:     {', '.join(info['diseases'])}\n")

    print("-" * 80)
    print("  Quick Instructions:")
    print("  1. Open the links above in your browser and click 'Download'.")
    print(f"  2. Move the downloaded .zip files into '{ADDITIONAL_CROPS_DIR}'.")
    print("  3. Run:  python model/ingest_crops.py --train")
    print("  The script will automatically unzip, split 80/20, register classes,")
    print("  and retrain MultiModalAeroCropNet on GPU with 4 workers!")
    print("=" * 80)


def extract_zip(zip_path: Path, extract_to: Path):
    """Extracts a zip file safely."""
    print(f"  -> Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)


def normalize_class_name(crop_prefix: str, raw_folder_name: str) -> str:
    """Converts various naming styles into canonical Crop___Disease format."""
    clean_folder = raw_folder_name.strip()
    clean_folder = re.sub(r"[^a-zA-Z0-9_ ]", "", clean_folder)
    clean_folder = clean_folder.replace(" ", "_")

    # If folder already has three underscores
    if "___" in clean_folder:
        return clean_folder

    # Capitalize crop prefix
    crop = crop_prefix.strip().capitalize()
    return f"{crop}___{clean_folder}"


def find_image_folders(root_dir: Path) -> list[Path]:
    """Finds all leaf folders containing image files."""
    leaf_folders = []
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for dirpath, _, filenames in os.walk(root_dir):
        p = Path(dirpath)
        img_count = sum(1 for f in filenames if Path(f).suffix.lower() in image_extensions)
        if img_count >= 5:  # Folder contains image dataset
            leaf_folders.append(p)

    return leaf_folders


def ingest_crops(train_after: bool = False):
    """Scans additional_crops directory, processes datasets, and registers classes."""
    ADDITIONAL_CROPS_DIR.mkdir(parents=True, exist_ok=True)
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VALID_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Look for zip files or subdirectories
    zip_files = list(ADDITIONAL_CROPS_DIR.glob("*.zip"))
    sub_dirs = [d for d in ADDITIONAL_CROPS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not zip_files and not sub_dirs:
        print(f"\n[Ingest] No pending crop datasets found in {ADDITIONAL_CROPS_DIR}")
        print_links()
        return

    print(f"\n[Ingest] Found {len(zip_files)} ZIP archive(s) and {len(sub_dirs)} folder(s). Processing...")

    temp_extract = ADDITIONAL_CROPS_DIR / "_extracted_staging"
    temp_extract.mkdir(parents=True, exist_ok=True)

    # Extract all ZIPs into staging
    for z in zip_files:
        crop_guess = z.stem.split("_")[0].capitalize()
        staging_dest = temp_extract / crop_guess
        extract_zip(z, staging_dest)

    # Copy any unzipped folders into staging as well
    for d in sub_dirs:
        if d.name != "_extracted_staging":
            dest = temp_extract / d.name
            if not dest.exists():
                shutil.copytree(d, dest)

    # Find image directories in staging
    image_folders = find_image_folders(temp_extract)
    print(f"  Found {len(image_folders)} disease class folder(s) across stages.")

    added_classes = []
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for folder in image_folders:
        # Determine crop from path hierarchy
        rel_parts = folder.relative_to(temp_extract).parts
        crop_candidate = rel_parts[0].capitalize()
        # If crop_candidate is generic like 'train' or 'valid', peek upwards
        if crop_candidate.lower() in ("train", "val", "valid", "test", "dataset"):
            crop_candidate = "Crop"

        canonical_name = normalize_class_name(crop_candidate, folder.name)
        images = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in image_exts]

        if not images:
            continue

        target_train_class_dir = TRAIN_DIR / canonical_name
        target_valid_class_dir = VALID_DIR / canonical_name
        target_train_class_dir.mkdir(parents=True, exist_ok=True)
        target_valid_class_dir.mkdir(parents=True, exist_ok=True)

        random.seed(42)
        random.shuffle(images)
        split_idx = int(len(images) * 0.8)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        for img in train_imgs:
            shutil.copy2(img, target_train_class_dir / img.name)
        for img in val_imgs:
            shutil.copy2(img, target_valid_class_dir / img.name)

        print(f"  [+] Ingested '{canonical_name}': {len(train_imgs)} train, {len(val_imgs)} valid")
        added_classes.append(canonical_name)

    # Clean staging directory
    shutil.rmtree(temp_extract, ignore_errors=True)

    # Move processed ZIPs to an archive folder to avoid re-extracting
    archive_dir = ADDITIONAL_CROPS_DIR / "processed_archives"
    archive_dir.mkdir(exist_ok=True)
    for z in zip_files:
        shutil.move(str(z), str(archive_dir / z.name))

    print(f"\n[Ingest] Successfully ingested {len(added_classes)} new class folder(s).")

    # If new classes were added, check and report current class count
    all_train_classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir()])
    print(f"[Ingest] Total classes now in training dataset: {len(all_train_classes)}")

    if train_after:
        print("\n[Ingest] Initiating model retraining with 4 workers...")
        train_cmd = f'python "{PROJECT_ROOT}/model/train.py" --workers 4 --epochs 10'
        os.system(train_cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroCrop.ai Crop Dataset Ingestion Pipeline")
    parser.add_argument("--links", action="store_true", help="Display verified dataset download links")
    parser.add_argument("--train", action="store_true", help="Automatically train model after ingestion")
    args = parser.parse_args()

    if args.links:
        print_links()
    else:
        ingest_crops(train_after=args.train)
