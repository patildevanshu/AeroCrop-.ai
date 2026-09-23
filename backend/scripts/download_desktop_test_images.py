#!/usr/bin/env python3
"""
AeroCrop.ai — Automated Desktop Test Leaf Dataset Generator
Downloads 6 verified leaf images per supported crop (3 Healthy + 3 Diseased)
directly from the internet into subfolders on the user's Desktop.

All images are authentic agricultural leaf photographs completely independent
of the PlantVillage / training dataset.

Folder structure:
C:\\Users\\devan\\Desktop\\AeroCrop_Test_Images\\
    ├── cotton\\
    │   ├── cotton_healthy_01.jpg
    │   ├── cotton_healthy_02.jpg
    │   ├── cotton_healthy_03.jpg
    │   ├── cotton_diseased_01.jpg
    │   ├── cotton_diseased_02.jpg
    │   └── cotton_diseased_03.jpg
    ├── sugarcane\\
    ...
"""

import sys
import io
import time
import re
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DESKTOP_DIR = Path(r"C:\Users\devan\Desktop\AeroCrop_Test_Images")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

CROP_QUERIES = {
    "cotton": {
        "healthy": ["cotton plant healthy green leaf close up photography", "cotton crop fresh green foliage leaf"],
        "diseased": ["cotton leaf bacterial blight disease close up", "cotton leaf spot alternaria disease"],
    },
    "sugarcane": {
        "healthy": ["sugarcane plant healthy green leaf close up", "sugarcane crop fresh foliage leaf"],
        "diseased": ["sugarcane red rot leaf disease close up", "sugarcane brown spot leaf pathology"],
    },
    "banana": {
        "healthy": ["banana plant healthy green leaf close up", "banana tree fresh green leaf foliage"],
        "diseased": ["banana sigatoka leaf spot disease close up", "banana panama wilt infected leaf"],
    },
    "turmeric": {
        "healthy": ["turmeric plant healthy green leaf close up", "curcuma longa fresh green leaf"],
        "diseased": ["turmeric leaf blotch disease close up", "turmeric leaf spot colletotrichum symptoms"],
    },
    "onion": {
        "healthy": ["onion plant healthy green leaf foliage close up", "allium cepa fresh green leaf stalk"],
        "diseased": ["onion purple blotch leaf disease close up", "onion stemphylium leaf blight symptoms"],
    },
    "soybean": {
        "healthy": ["soybean plant healthy green leaf close up", "glycine max fresh green foliage leaf"],
        "diseased": ["soybean cercospora leaf blight disease close up", "soybean brown spot septoria leaf disease"],
    },
    "wheat": {
        "healthy": ["wheat plant healthy green leaf flag leaf close up", "wheat crop fresh green foliage leaf"],
        "diseased": ["wheat leaf rust puccinia disease close up", "wheat powdery mildew septoria leaf blight"],
    },
    "maize": {
        "healthy": ["corn maize plant healthy green leaf close up", "corn crop fresh green foliage leaf"],
        "diseased": ["corn maize northern leaf blight close up", "corn gray leaf spot cercospora disease"],
    },
    "rice": {
        "healthy": ["rice paddy plant healthy green leaf close up", "rice crop fresh green foliage leaf"],
        "diseased": ["rice bacterial leaf blight disease close up", "rice brown spot blast disease leaf symptoms"],
    },
    "potato": {
        "healthy": ["potato plant healthy green leaf close up", "potato crop fresh green foliage leaf"],
        "diseased": ["potato early blight alternaria leaf disease close up", "potato late blight phytophthora leaf disease"],
    },
    "tomato": {
        "healthy": ["tomato plant healthy green leaf close up", "tomato crop fresh green foliage leaf"],
        "diseased": ["tomato early blight alternaria leaf disease close up", "tomato septoria leaf spot disease symptoms"],
    },
    "pepper": {
        "healthy": ["bell pepper chilli plant healthy green leaf close up", "capsicum annuum fresh green leaf"],
        "diseased": ["pepper leaf bacterial spot xanthomonas close up", "chilli leaf curl virus anthracnose disease"],
    },
    "apple": {
        "healthy": ["apple tree healthy green leaf close up", "malus domestica fresh green foliage leaf"],
        "diseased": ["apple scab venturia inaequalis leaf disease close up", "cedar apple rust gymnosporangium leaf disease"],
    },
    "grape": {
        "healthy": ["grapevine healthy green leaf close up", "vitis vinifera fresh green foliage leaf"],
        "diseased": ["grape black rot guignardia leaf disease close up", "grape downy mildew plasmopara leaf disease"],
    },
    "strawberry": {
        "healthy": ["strawberry plant healthy green leaf close up", "fragaria fresh green foliage leaf"],
        "diseased": ["strawberry leaf scorch diplocarpon close up", "strawberry common leaf spot mycosphaerella"],
    },
    "peach": {
        "healthy": ["peach tree healthy green leaf close up", "prunus persica fresh green foliage leaf"],
        "diseased": ["peach leaf curl taphrina deformans close up", "peach rust powdery mildew leaf disease"],
    },
    "orange": {
        "healthy": ["citrus orange tree healthy green leaf close up", "citrus sinensis fresh green foliage leaf"],
        "diseased": ["citrus canker xanthomonas leaf disease close up", "citrus black spot phyllosticta leaf symptoms"],
    },
    "blueberry": {
        "healthy": ["blueberry bush healthy green leaf close up", "vaccinium corymbosum fresh green leaf"],
        "diseased": ["blueberry leaf rust thekopsora disease close up", "blueberry septoria leaf spot symptoms"],
    },
    "cherry": {
        "healthy": ["cherry tree healthy green leaf close up", "prunus avium fresh green foliage leaf"],
        "diseased": ["cherry leaf spot blumeriella jaapii disease close up", "cherry powdery mildew leaf symptoms"],
    },
    "raspberry": {
        "healthy": ["raspberry bush healthy green leaf close up", "rubus idaeus fresh green foliage leaf"],
        "diseased": ["raspberry leaf spot sphaerulina disease close up", "raspberry yellow rust phragmidium leaf disease"],
    },
    "squash": {
        "healthy": ["squash pumpkin plant healthy green leaf close up", "cucurbita pepo fresh green foliage leaf"],
        "diseased": ["squash powdery mildew podosphaera leaf close up", "squash downy mildew pseudoperonospora leaf disease"],
    },
}


def search_bing_image_urls(query: str, count: int = 15) -> list[str]:
    """Search Bing async image endpoint and extract direct image URLs."""
    url = (
        f"https://www.bing.com/images/async?"
        f"q={urllib.parse.quote(query)}&first=0&count={count}"
        f"&scenario=ImageBasicHover&datsrc=N_I&layout=RowBased&vintage=1"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&quot;', html)
        seen = set()
        clean = []
        for m in matches:
            low = m.lower()
            if m not in seen and not any(bad in low for bad in [".svg", ".gif", ".ico", "logo", "icon"]):
                seen.add(m)
                clean.append(m)
        return clean
    except Exception as e:
        print(f"    [Warn] Search query failed for '{query}': {e}")
        return []


def download_and_verify_leaf_image(url: str, dest_path: Path) -> bool:
    """Download image, verify with Pillow, enforce leaf-friendly aspect ratio and size."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()

        if len(data) < 8000:  # Ignore thumbnails < 8KB
            return False

        # Verify integrity
        img = Image.open(io.BytesIO(data))
        img.verify()

        # Reload for processing
        img = Image.open(io.BytesIO(data))

        # Must be at least 250x250
        if img.width < 250 or img.height < 250:
            return False

        # Reject extreme aspect ratios (banners/headers)
        aspect = max(img.width / img.height, img.height / img.width)
        if aspect > 2.5:
            return False

        if img.mode != "RGB":
            img = img.convert("RGB")

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest_path, "JPEG", quality=90, optimize=True)
        return True
    except Exception:
        return False


def collect_images_for_category(crop_name: str, category: str, queries: list[str], target_dir: Path, target_count: int = 3) -> int:
    """Collect target_count images for category (healthy or diseased)."""
    saved = 0
    # Check already downloaded valid files
    for i in range(1, target_count + 1):
        f = target_dir / f"{crop_name}_{category}_{i:02d}.jpg"
        if f.exists() and f.stat().st_size > 8000:
            saved += 1

    if saved >= target_count:
        return saved

    for q in queries:
        if saved >= target_count:
            break
        urls = search_bing_image_urls(q, count=20)
        for u in urls:
            if saved >= target_count:
                break
            dest = target_dir / f"{crop_name}_{category}_{saved + 1:02d}.jpg"
            if download_and_verify_leaf_image(u, dest):
                saved += 1
                size_kb = dest.stat().st_size / 1024
                print(f"    [{category.upper()}] Saved {dest.name} ({size_kb:.1f} KB)")
                time.sleep(0.2)

    return saved


def main():
    print("====================================================================")
    print("🌱 AeroCrop.ai — Desktop Leaf Test Dataset Downloader")
    print(f"📂 Destination  : {DESKTOP_DIR}")
    print(f"🌾 Total Crops  : {len(CROP_QUERIES)} crops")
    print(f"🌿 Per Crop     : 3 Healthy Leaf Images + 3 Diseased Leaf Images = 6 Total")
    print("====================================================================\n")

    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

    summary = {}
    total_downloaded = 0

    for idx, (crop, q_dict) in enumerate(CROP_QUERIES.items(), 1):
        crop_dir = DESKTOP_DIR / crop
        print(f"[{idx:02d}/{len(CROP_QUERIES)}] Processing crop: {crop.upper()}...")

        h_count = collect_images_for_category(crop, "healthy", q_dict["healthy"], crop_dir, target_count=3)
        d_count = collect_images_for_category(crop, "diseased", q_dict["diseased"], crop_dir, target_count=3)

        total_for_crop = h_count + d_count
        summary[crop] = (h_count, d_count)
        total_downloaded += total_for_crop
        print(f"  -> {crop}: {h_count}/3 Healthy, {d_count}/3 Diseased (Total: {total_for_crop}/6)\n")
        time.sleep(0.4)

    print("\n====================================================================")
    print("📊 DOWNLOAD SUMMARY REPORT")
    print("====================================================================")
    for crop, (h, d) in summary.items():
        status = "✅ PASS (6/6)" if (h >= 3 and d >= 3) else f"⚠️ ({h}/3 Healthy, {d}/3 Diseased)"
        print(f"  - {crop:14s} : {h} Healthy + {d} Diseased  {status}")
    print("--------------------------------------------------------------------")
    print(f"🎉 Total Images Saved : {total_downloaded} images")
    print(f"📁 Desktop Folder Path: {DESKTOP_DIR}")
    print("====================================================================")


if __name__ == "__main__":
    main()
