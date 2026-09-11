# AeroCrop.ai — Dataset Specifications & Distribution

**Audit Timestamp**: 2026-09-06  
- **Total Dataset Images**: **98,963**
- **Training Images (80%)**: **79,166**
- **Validation Images (20%)**: **19,797**
- **Marked (Diseased / Symptomatic)**: **67,771** (68.5%)
- **Unmarked (Healthy / Asymptomatic)**: **31,192** (31.5%)
- **Total Diagnostic Classes**: **56**
- **Total Crops Covered**: **19**

## 1. Crop-Wise Breakdown

| Crop | Total Images | Train (80%) | Valid (20%) | Classes | Primary Regional Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tomato** | 22,598 | 18,078 | 4,520 | 10 | Maharashtra & Pan-India |
| **Corn_(maize)** | 11,220 | 8,975 | 2,245 | 4 | Maharashtra & Pan-India |
| **Apple** | 9,819 | 7,851 | 1,968 | 4 | Maharashtra & Pan-India |
| **Grape** | 9,027 | 7,222 | 1,805 | 4 | Maharashtra (Nashik/Sangli) |
| **Potato** | 6,652 | 5,321 | 1,331 | 3 | Maharashtra & Pan-India |
| **Pepper,_bell** | 4,876 | 3,901 | 975 | 2 | Maharashtra & Pan-India |
| **Strawberry** | 4,498 | 3,598 | 900 | 2 | Maharashtra & Pan-India |
| **Peach** | 4,457 | 3,566 | 891 | 2 | Maharashtra & Pan-India |
| **Cherry_(including_sour)** | 4,386 | 3,509 | 877 | 2 | Maharashtra & Pan-India |
| **Banana** | 3,108 | 2,491 | 617 | 4 | Maharashtra & Pan-India |
| **Soybean** | 2,527 | 2,022 | 505 | 1 | Maharashtra & Pan-India |
| **Sugarcane** | 2,521 | 2,015 | 506 | 5 | Maharashtra & Pan-India |
| **Orange** | 2,513 | 2,010 | 503 | 1 | Maharashtra & Pan-India |
| **Cotton** | 2,386 | 1,907 | 479 | 2 | Maharashtra & Pan-India |
| **Blueberry** | 2,270 | 1,816 | 454 | 1 | Maharashtra & Pan-India |
| **Raspberry** | 2,226 | 1,781 | 445 | 1 | Maharashtra & Pan-India |
| **Squash** | 2,170 | 1,736 | 434 | 1 | Maharashtra & Pan-India |
| **Turmeric** | 781 | 623 | 158 | 4 | Maharashtra & Pan-India |
| **Rice** | 120 | 96 | 24 | 3 | Maharashtra & Pan-India |

## 2. Complete 56-Class Distribution (Marked vs Unmarked)

| Index | Canonical Class Identifier | Crop | Category | Train | Valid | Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `Apple___Apple_scab` | Apple | Marked (Diseased) | 2016 | 504 | 2520 |
| `1` | `Apple___Black_rot` | Apple | Marked (Diseased) | 1987 | 497 | 2484 |
| `2` | `Apple___Cedar_apple_rust` | Apple | Marked (Diseased) | 1810 | 455 | 2265 |
| `3` | `Apple___healthy` | Apple | Unmarked (Healthy) | 2038 | 512 | 2550 |
| `4` | `Blueberry___healthy` | Blueberry | Unmarked (Healthy) | 1816 | 454 | 2270 |
| `5` | `Cherry_(including_sour)___healthy` | Cherry_(including_sour) | Unmarked (Healthy) | 1826 | 456 | 2282 |
| `6` | `Cherry_(including_sour)___Powdery_mildew` | Cherry_(including_sour) | Marked (Diseased) | 1683 | 421 | 2104 |
| `7` | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Corn_(maize) | Marked (Diseased) | 2155 | 539 | 2694 |
| `8` | `Corn_(maize)___Common_rust_` | Corn_(maize) | Marked (Diseased) | 1907 | 477 | 2384 |
| `9` | `Corn_(maize)___healthy` | Corn_(maize) | Unmarked (Healthy) | 2285 | 572 | 2857 |
| `10` | `Corn_(maize)___Northern_Leaf_Blight` | Corn_(maize) | Marked (Diseased) | 2628 | 657 | 3285 |
| `11` | `Grape___Black_rot` | Grape | Marked (Diseased) | 1888 | 472 | 2360 |
| `12` | `Grape___Esca_(Black_Measles)` | Grape | Marked (Diseased) | 1920 | 480 | 2400 |
| `13` | `Grape___healthy` | Grape | Unmarked (Healthy) | 1692 | 423 | 2115 |
| `14` | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Grape | Marked (Diseased) | 1722 | 430 | 2152 |
| `15` | `Orange___Haunglongbing_(Citrus_greening)` | Orange | Marked (Diseased) | 2010 | 503 | 2513 |
| `16` | `Peach___Bacterial_spot` | Peach | Marked (Diseased) | 1838 | 459 | 2297 |
| `17` | `Peach___healthy` | Peach | Unmarked (Healthy) | 1728 | 432 | 2160 |
| `18` | `Pepper,_bell___Bacterial_spot` | Pepper,_bell | Marked (Diseased) | 1913 | 478 | 2391 |
| `19` | `Pepper,_bell___healthy` | Pepper,_bell | Unmarked (Healthy) | 1988 | 497 | 2485 |
| `20` | `Potato___Early_blight` | Potato | Marked (Diseased) | 1939 | 485 | 2424 |
| `21` | `Potato___healthy` | Potato | Unmarked (Healthy) | 1824 | 456 | 2280 |
| `22` | `Potato___Late_blight` | Potato | Marked (Diseased) | 1939 | 485 | 2424 |
| `23` | `Raspberry___healthy` | Raspberry | Unmarked (Healthy) | 1781 | 445 | 2226 |
| `24` | `Soybean___healthy` | Soybean | Unmarked (Healthy) | 2022 | 505 | 2527 |
| `25` | `Squash___Powdery_mildew` | Squash | Marked (Diseased) | 1736 | 434 | 2170 |
| `26` | `Strawberry___healthy` | Strawberry | Unmarked (Healthy) | 1824 | 456 | 2280 |
| `27` | `Strawberry___Leaf_scorch` | Strawberry | Marked (Diseased) | 1774 | 444 | 2218 |
| `28` | `Tomato___Bacterial_spot` | Tomato | Marked (Diseased) | 1702 | 425 | 2127 |
| `29` | `Tomato___Early_blight` | Tomato | Marked (Diseased) | 1920 | 480 | 2400 |
| `30` | `Tomato___healthy` | Tomato | Unmarked (Healthy) | 1926 | 481 | 2407 |
| `31` | `Tomato___Late_blight` | Tomato | Marked (Diseased) | 1851 | 463 | 2314 |
| `32` | `Tomato___Leaf_Mold` | Tomato | Marked (Diseased) | 1882 | 470 | 2352 |
| `33` | `Tomato___Septoria_leaf_spot` | Tomato | Marked (Diseased) | 1745 | 436 | 2181 |
| `34` | `Tomato___Spider_mites Two-spotted_spider_mite` | Tomato | Marked (Diseased) | 1741 | 435 | 2176 |
| `35` | `Tomato___Target_Spot` | Tomato | Marked (Diseased) | 1827 | 457 | 2284 |
| `36` | `Tomato___Tomato_mosaic_virus` | Tomato | Marked (Diseased) | 1790 | 448 | 2238 |
| `37` | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | Tomato | Marked (Diseased) | 1961 | 490 | 2451 |
| `38` | `Cotton___Bacterial_blight` | Cotton | Marked (Diseased) | 1081 | 272 | 1353 |
| `39` | `Cotton___healthy` | Cotton | Unmarked (Healthy) | 826 | 207 | 1033 |
| `40` | `Banana___Cordana_leaf_spot` | Banana | Marked (Diseased) | 273 | 69 | 342 |
| `41` | `Banana___Panama_disease` | Banana | Marked (Diseased) | 668 | 167 | 835 |
| `42` | `Banana___Sigatoka` | Banana | Marked (Diseased) | 750 | 180 | 930 |
| `43` | `Banana___healthy` | Banana | Unmarked (Healthy) | 800 | 201 | 1001 |
| `44` | `Sugarcane___Mosaic` | Sugarcane | Marked (Diseased) | 369 | 93 | 462 |
| `45` | `Sugarcane___Red_rot` | Sugarcane | Marked (Diseased) | 414 | 104 | 518 |
| `46` | `Sugarcane___Rust` | Sugarcane | Marked (Diseased) | 411 | 103 | 514 |
| `47` | `Sugarcane___Yellow_leaf` | Sugarcane | Marked (Diseased) | 404 | 101 | 505 |
| `48` | `Sugarcane___healthy` | Sugarcane | Unmarked (Healthy) | 417 | 105 | 522 |
| `49` | `Rice___Bacterial_leaf_blight` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `50` | `Rice___Brown_spot` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `51` | `Rice___Leaf_smut` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `52` | `Turmeric___Dry_leaf` | Turmeric | Marked (Diseased) | 162 | 41 | 203 |
| `53` | `Turmeric___Leaf_blotch` | Turmeric | Marked (Diseased) | 159 | 40 | 199 |
| `54` | `Turmeric___Rhizome_rot` | Turmeric | Marked (Diseased) | 145 | 37 | 182 |
| `55` | `Turmeric___healthy` | Turmeric | Unmarked (Healthy) | 157 | 40 | 197 |

---

## 3. Dataset Expansion & Pruning Plan: 20k Multi-Class Crop Integration

### 3.1 Overview of Candidate Dataset
* **Dataset Identifier:** [`jawadali1045/20k-multi-class-crop-disease-images`](https://www.kaggle.com/datasets/jawadali1045/20k-multi-class-crop-disease-images)
* **Author:** Jawad Ali (Kaggle)
* **Volume:** 20,000+ RGB leaf images
* **Crops Covered:** 5 Major Field Crops (**Wheat, Rice, Cotton, Sugarcane, Maize**)

### 3.2 Crop-by-Crop Coverage & Integration Strategy

| Crop Category | Included in Jawad Ali (20k)? | Existing in Local Repo (`data/main dataset`) | Action / Decision |
| :--- | :--- | :--- | :--- |
| **Wheat** | ✅ **Yes** (Rusts, Septoria, Healthy) | ❌ *Missing (0 images)* | **PRIMARY ADDITION**: Solves the missing wheat pathology requirement for Indian/Maharashtra Rabi season. |
| **Rice** | ✅ **Yes** (Comprehensive sample) | ⚠️ *Under-represented (120 images)* | **UPGRADE & REPLACE**: Current 120-image dataset is too small; replacing with the 20k subset significantly improves validation accuracy. |
| **Cotton** | ✅ **Yes** (Bacterial blight, leaf curl) | 2,310 images (`data/cotton`) | **MERGE / DEDUPLICATE**: Review sample diversity; keep higher quality resolution. |
| **Sugarcane** | ✅ **Yes** (Red rot, rust, mosaic) | 2,521 images (`data/sugarcane`) | **MERGE / DEDUPLICATE**: Supplement existing classes. |
| **Maize (Corn)** | ✅ **Yes** (Blight, rust, spot) | 2,045 images (`data/maize_field_extracted`) | **KEEP EXISTING**: Already balanced with PlantVillage. |
| **Banana** | ❌ **No** | 6,242 images (`data/banana`) | 🚨 **MUST PRESERVE**: Do not delete; covers Panama disease, Sigatoka, and Cordana. |
| **Turmeric (Haldi)** | ❌ **No** | 781 images (`data/turmeric`) | 🚨 **MUST PRESERVE**: Do not delete; high regional value for Maharashtra (Rhizome rot, Leaf blotch). |
| **PlantVillage (14 crops)** | ❌ **No** | 55,234 images (`data/New Plant Diseases Dataset(Augmented)`) | 🚨 **MUST PRESERVE**: Covers Tomato, Potato, Apple, Grape, Pepper, Soybean, Orange, Strawberry, etc. |

### 3.3 Safe Deletion & Storage Pruning Rules

To prevent disk bloat while protecting non-overlapping crop models:

#### A. Safe to Delete (Once 20k dataset is verified & ingested):
1. **Old Rice Directory (`data/main dataset/rice`)**:
   - Safely replace the 120-image placeholder with the extensive 20k rice dataset.
2. **Obsolete Download Archives (`C:\Users\devan\Downloads\`):**
   - `archive (2).zip` (Cotton ~155 MB) — Overlapped by 20k package.
   - `archive (4).zip` (Sugarcane ~167 MB) — Overlapped by 20k package.
   - `archive (5).zip` (Rice ~38 MB) — Overlapped by 20k package.

#### B. Strictly Forbidden to Delete:
1. `data/main dataset/banana/` and `archive (3).zip` (Banana pathology).
2. `data/main dataset/turmeric/` and `archive (6).zip` (Maharashtra Haldi pathology).
3. `data/main dataset/New Plant Diseases Dataset(Augmented)/` and `archive.zip` (Core 14-crop baseline).

### 3.4 Ingestion & Model Integration Workflow
1. Download `jawadali1045/20k-multi-class-crop-disease-images` into `Downloads/`.
2. Extract the `Wheat/` directory directly into `data/main dataset/wheat/`.
3. Replace `data/main dataset/rice/` with the higher-volume `Rice/` directory.
4. Execute crop registration:
   ```bash
   python model/ingest_crops.py --crop wheat --data_dir "data/main dataset/wheat"
   ```
5. Update `NUM_DISEASE_CLASSES` in `backend/config.py` and taxonomy in `backend/services/disease_service.py` to index the new wheat diagnostic classes.

---

## 4. Integration Execution Log (Completed)

* **Execution Script:** `model/extract_and_migrate_crops.py`
* **Status:** ✅ Completed with 0 integrity errors.
* **Wheat Added:** `2,101` images across 11 diagnostic classes (`Flag_Smut`, `Healthy`, `Brown_Rust`, `Stem_Fly`, `Aphid`, `Black_Rust`, `Leaf_Blight`, `Mite`, `Powdery_Mildew`, `Scab`, `Yellow_Rust`) in `data/main dataset/wheat/`.
* **Rice Upgraded:** Expanded from `120` to `6,112` images across 5 classes (`Bacterial_Blight`, `Blast`, `Brown_Spot`, `Leaf_Smut`, `Tungro`) in `data/main dataset/rice/`.
* **Obsolete Files Cleaned:**
  - Removed old placeholder `data/main dataset/rice/rice_leaf_diseases/` (120 images).
  - Deleted `C:\Users\devan\Downloads\archive (5).zip` (old 38 MB rice archive).
  - Deleted `C:\Users\devan\Downloads\archive (9).zip` (2.51 GB multi-crop archive, space reclaimed).
* **Protected Datasets Intact:**
  - `banana` (6,242 images) & `archive (3).zip` preserved.
  - `turmeric` (781 images) & `archive (6).zip` preserved.
  - `New Plant Diseases Dataset(Augmented)` (55,234 images) & `archive.zip` preserved.
  - `cotton` (2,310 images) and `sugarcane` (2,521 images) preserved.

---

## 5. Consolidated & Deduplicated Dataset Architecture (Post-Restructure)

**Restructure Timestamp**: 2026-09-11  
**Execution Script**: `model/restructure_and_deduplicate.py`  
- **Total Unique Images**: **62,836** (100% unique MD5 hashes)
- **Training Set (Train)**: **50,294** images (~80.0%)
- **Validation Set (Valid)**: **12,542** images (~20.0%)
- **Train/Valid Data Leakage**: **0** (Zero hash overlap between train and valid)
- **Duplicates Eliminated**: **14,470+** redundant files pruned (~1.5 GB reclaimed)
- **Total Canonical Classes**: **50**
- **Canonical Structure**:
  ```
  data/main dataset/
  ├── train/
  │   └── <Crop>___<Disease_or_Condition>/
  └── valid/
      └── <Crop>___<Disease_or_Condition>/
  ```
- **Backward Compatibility Link**:
  NTFS Junction: `data/New Plant Diseases Dataset(Augmented)` -> `data/main dataset`

### 5.1 Complete 50-Class Distribution (Strict 80/20 Partition)

| Index | Canonical Class Folder | Crop | Train (80%) | Valid (20%) | Total Unique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `Banana___Cordana_leaf_spot` | Banana | 273 | 69 | 342 |
| `1` | `Banana___Panama_disease` | Banana | 668 | 167 | 835 |
| `2` | `Banana___Sigatoka` | Banana | 1738 | 424 | 2162 |
| `3` | `Banana___healthy` | Banana | 796 | 199 | 995 |
| `4` | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Corn | 2155 | 539 | 2694 |
| `5` | `Corn_(maize)___Common_rust_` | Corn | 1907 | 477 | 2384 |
| `6` | `Corn_(maize)___Northern_Leaf_Blight` | Corn | 2626 | 656 | 3282 |
| `7` | `Corn_(maize)___healthy` | Corn | 2284 | 571 | 2855 |
| `8` | `Cotton___Bacterial_blight` | Cotton | 1075 | 262 | 1337 |
| `9` | `Cotton___healthy` | Cotton | 816 | 200 | 1016 |
| `10` | `Orange___Haunglongbing_(Citrus_greening)` | Orange | 2010 | 503 | 2513 |
| `11` | `Potato___Early_blight` | Potato | 1939 | 485 | 2424 |
| `12` | `Potato___Late_blight` | Potato | 1939 | 485 | 2424 |
| `13` | `Potato___healthy` | Potato | 1824 | 456 | 2280 |
| `14` | `Rice___Bacterial_leaf_blight` | Rice | 1078 | 270 | 1348 |
| `15` | `Rice___Brown_spot` | Rice | 998 | 250 | 1248 |
| `16` | `Rice___Leaf_blast` | Rice | 775 | 194 | 969 |
| `17` | `Rice___Leaf_smut` | Rice | 44 | 12 | 56 |
| `18` | `Rice___Tungro` | Rice | 1046 | 262 | 1308 |
| `19` | `Soybean___healthy` | Soybean | 2022 | 505 | 2527 |
| `20` | `Sugarcane___Mosaic` | Sugarcane | 303 | 73 | 376 |
| `21` | `Sugarcane___Red_rot` | Sugarcane | 414 | 104 | 518 |
| `22` | `Sugarcane___Rust` | Sugarcane | 363 | 84 | 447 |
| `23` | `Sugarcane___Yellow_leaf` | Sugarcane | 397 | 97 | 494 |
| `24` | `Sugarcane___healthy` | Sugarcane | 386 | 90 | 476 |
| `25` | `Tomato___Bacterial_spot` | Tomato | 1702 | 425 | 2127 |
| `26` | `Tomato___Early_blight` | Tomato | 1920 | 480 | 2400 |
| `27` | `Tomato___Late_blight` | Tomato | 1844 | 460 | 2304 |
| `28` | `Tomato___Leaf_Mold` | Tomato | 1882 | 470 | 2352 |
| `29` | `Tomato___Septoria_leaf_spot` | Tomato | 1745 | 436 | 2181 |
| `30` | `Tomato___Spider_mites Two-spotted_spider_mite` | Tomato | 1741 | 435 | 2176 |
| `31` | `Tomato___Target_Spot` | Tomato | 1827 | 457 | 2284 |
| `32` | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | Tomato | 1961 | 490 | 2451 |
| `33` | `Tomato___Tomato_mosaic_virus` | Tomato | 1790 | 448 | 2238 |
| `34` | `Tomato___healthy` | Tomato | 1923 | 478 | 2401 |
| `35` | `Turmeric___Dry_leaf` | Turmeric | 162 | 41 | 203 |
| `36` | `Turmeric___Leaf_blotch` | Turmeric | 159 | 40 | 199 |
| `37` | `Turmeric___Rhizome_rot` | Turmeric | 144 | 37 | 181 |
| `38` | `Turmeric___healthy` | Turmeric | 157 | 40 | 197 |
| `39` | `Wheat___Aphid` | Wheat | 155 | 39 | 194 |
| `40` | `Wheat___Black_rust` | Wheat | 128 | 32 | 160 |
| `41` | `Wheat___Brown_rust` | Wheat | 84 | 21 | 105 |
| `42` | `Wheat___Flag_smut` | Wheat | 84 | 21 | 105 |
| `43` | `Wheat___Leaf_blight` | Wheat | 140 | 36 | 176 |
| `44` | `Wheat___Mite` | Wheat | 153 | 39 | 192 |
| `45` | `Wheat___Powdery_mildew` | Wheat | 168 | 43 | 211 |
| `46` | `Wheat___Scab` | Wheat | 83 | 21 | 104 |
| `47` | `Wheat___Stem_fly` | Wheat | 137 | 35 | 172 |
| `48` | `Wheat___Yellow_rust` | Wheat | 73 | 19 | 92 |
| `49` | `Wheat___healthy` | Wheat | 256 | 65 | 321 |
| **Total** | **All 50 Classes** | — | **50,294** | **12,542** | **62,836** |

---

## 6. Official Reference Dataset Sources & Verified Download Links

All datasets utilized across **AeroCrop.ai** are sourced from peer-reviewed and verified public repositories on Kaggle. Below is the complete catalogue of reference sources, volume metrics, and direct download links:

| # | Dataset Title & Domain | Source / Author | Volume & Content | Verified Download URL |
| :- | :--- | :--- | :--- | :--- |
| 1 | **20k Multi-Class Crop Disease Images** *(Wheat & Upgraded Rice)* | Jawad Ali (Kaggle) | 2.51 GB, 18,625 images (Wheat rusts, blight, pests; Rice blast, bacterial blight, tungro) | [jawadali1045/20k-multi-class-crop-disease-images](https://www.kaggle.com/datasets/jawadali1045/20k-multi-class-crop-disease-images) |
| 2 | **New Plant Diseases Dataset (Augmented)** *(Core 14-Crops Baseline)* | Vipul Patel / PlantVillage | 2.89 GB, 87,900 images (Tomato, Potato, Corn, Orange, Soybean baseline) | [vipoooool/new-plant-diseases-dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) |
| 3 | **Banana Leaf Disease Dataset v4** *(Cordana, Panama, Sigatoka, Healthy)* | Rayhan Arlistya (Kaggle) | 430 MB, 6,242 images (Panama wilt, Yellow/Black Sigatoka, Cordana leaf spot) | [rayhanarlistya/banana-leaf-disease-dataset-v4](https://www.kaggle.com/datasets/rayhanarlistya/banana-leaf-disease-dataset-v4) |
| 4 | **Turmeric Datasets for CNN Model Training and Test** | Hitesh Patil (Kaggle) | 172 MB, 781 images (Leaf blotch, Dry leaf, Rhizome rot, Healthy haldi) | [hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test](https://www.kaggle.com/datasets/hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test) |
| 5 | **Cotton Leaf Diseases Dataset** *(Bacterial Blight, Curl Virus, Healthy)* | Janmejay Bhoi (Kaggle) | 155 MB, 2,310 images (Angular leaf spot, bacterial blight, healthy foliage) | [janmejaybhoi/cotton-disease-dataset](https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset) |
| 6 | **Sugarcane Leaf Disease Dataset** *(Red Rot, Rust, Mosaic, Yellow)* | Nirmal Sankalana (Kaggle) | 160 MB, 2,521 images (Colletotrichum falcatum red rot, common rust, mosaic) | [nirmalsankalana/sugarcane-leaf-disease-dataset](https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset) |
| 7 | **Rice Leaf Diseases Dataset** *(Baseline Rice Pathology)* | Vbookshelf (Kaggle) | 37 MB, 120 images (Bacterial leaf blight, brown spot, leaf smut) | [vbookshelf/rice-leaf-diseases](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases) |
| 8 | **Crop Yield Prediction Dataset** *(Agro-Meteorological Telemetry)* | Rikin Patel (Kaggle / FAO) | ~1.5 MB (`yield_df.csv`, 28,242 rows across 101 countries including India) | [patelris/crop-yield-prediction-dataset](https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset) |
| 9 | **Crop Production in India** *(District-Level Indian Yield & Acreage)* | Abhinand (Kaggle / MoA&FW) | ~2 MB (`crop_production.csv`, 246,000+ district-wise production records) | [abhinand05/crop-production-in-india](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) |

---

## 7. Final Project Scope & Scope Freezing Note

> [!IMPORTANT]
> As of **September 2026**, the **11 crops** (Wheat, Rice, Cotton, Sugarcane, Soybean, Maize, Potato, Tomato, Banana, Turmeric, Orange) and their **50 diagnostic pathology classes** are officially frozen as the **Final Core Scope** of the AeroCrop.ai platform.
> All application layers — from Deep Learning feature extractors to REST endpoints, Soil NPK algorithms, APMC Mandi price monitors, and React UI components — are strictly calibrated against this 11-crop taxonomy.



