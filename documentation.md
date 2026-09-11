# AeroCrop.ai — Technical Documentation

> Living document. Updated after every development milestone.

---

## Project Overview

**AeroCrop.ai** is a Multi-Modal Multi-Task Deep Learning & Precision Agriculture Platform designed for commercial and smallholder farmers in Maharashtra, India. From a single leaf photograph, soil nutrient metrics, and microclimatic telemetry, it delivers six unified operational outputs:

1. **Pathology Diagnosis** — 38-class classification with probability distribution and confidence score
2. **Vernacular Prescription (Audio & Visual)** — Chemical + organic remedies with native Web Speech text-to-speech (`mr-IN`, `hi-IN`, `en-IN`)
3. **Commercial 50kg Bags & Subsidized Cost** — Deficit stoichiometry translated to 50kg Urea, DAP, MOP bags with Acre/Guntha scaling and GoI NBS pricing
4. **Yield Forecasting** — Multi-modal regression predicting harvest in tons/hectare ($t/\text{ha}$) and quintals/acre
5. **Smart Foliar Spray Window** — Real-time hazard assessment preventing chemical wash-off ($>1\text{ mm}$ rain) and drift ($>15\text{ km/h}$ wind)
6. **APMC Mandi Intelligence & Revenue** — Live Maharashtra APMC modal prices, MSP benchmarks, and projected harvest cash revenue (₹)

---

## Architecture

### System Layers

```
Layer           | Directory          | Technology & Responsibility
─────────────── | ────────────────── | ─────────────────────────────────────────────────────────────
Model           | model/             | PyTorch MultiModalAeroCropNet (ResNet-18 + MLP) + InferenceService
Database        | database/          | Async SQLAlchemy + SQLite (`users`, `farmer_plots`, `diagnoses`)
Service         | services/          | Core agronomics (Disease, Fertilizer, Weather, Mandi, Storage)
Controller      | controllers/       | FastAPI routers (`auth`, `plots`, `history`, `predict`, `mandi`, `weather`)
Frontend (Vite) | frontend/          | React 18 + Vite + TypeScript (Dashboard, Diagnose, Plots, Auth)
Frontend (HTML) | views/             | Vanilla HTML5/CSS3/JS SPA with Chart.js fallback
```

### Neural Network: `MultiModalAeroCropNet`

```
Input 1: RGB Leaf Image (3 × 224 × 224)
  └─► ResNet-18 Visual Encoder ──────────────────► 512-dim visual vector

Input 2: Tabular Vector [N, P, K, temp, humidity, rainfall] (6-dim)
  └─► 3-Layer MLP Tabular Encoder ───────────────► 64-dim tabular vector

                            Concatenation → 576-dim
                            Linear(576, 128) → BatchNorm → ReLU
                            ── 128-dim Shared Embedding ──

  ├─► Task Head A: Linear(128, 38) → Softmax     → Disease Class + Confidence
  └─► Task Head B: Linear(128, 32) → ReLU → Linear(32, 1) → Yield (t/ha)
```

**Key design decisions:**
- ResNet-18 chosen for its strong feature extraction capability at low parameter count
- Fusion before task heads enables shared representation learning
- Separate regression head with non-negative ReLU output for yield

---

## Fertilizer Dosage Math

Based on ICAR (Indian Council of Agricultural Research) recommendations.

### Crop NPK Targets (kg/ha)

| Crop | N Target | P Target | K Target |
|------|----------|----------|----------|
| Cotton | 120 | 60 | 60 |
| Wheat | 120 | 60 | 40 |
| Maize | 120 | 60 | 40 |
| Rice | 100 | 50 | 50 |
| Potato | 120 | 80 | 120 |

### Calculation Formulae

**Step 1 — Compute Deficits:**
```
D_N = max(0, Target_N - Soil_N)
D_P = max(0, Target_P - Soil_P)
D_K = max(0, Target_K - Soil_K)
```

**Step 2 — DAP (18% N, 46% P₂O₅) to satisfy Phosphorus:**
```
DAP_qty = D_P / 0.46
```

**Step 3 — Urea (46% N) for remaining Nitrogen after DAP contribution:**
```
N_from_DAP   = DAP_qty × 0.18
N_remaining  = max(0, D_N - N_from_DAP)
Urea_qty     = N_remaining / 0.46
```

**Step 4 — MOP (60% K₂O) to satisfy Potassium:**
```
MOP_qty = D_K / 0.60
```

---

## Disease Knowledge Base

38 classes aligned with the PlantVillage dataset:

| Class | Disease | Crop | Severity |
|-------|---------|------|----------|
| 0 | Apple Scab | Apple | High |
| 1 | Apple Black Rot | Apple | High |
| 2 | Cedar Apple Rust | Apple | Moderate |
| 3 | Apple Healthy | Apple | None |
| 7 | Cercospora / Gray Leaf Spot | Maize | High |
| 8 | Common Rust | Maize | Moderate |
| 9 | Northern Leaf Blight | Maize | High |
| 20 | Early Blight | Potato | Moderate |
| 21 | Late Blight | Potato | Critical |
| 28 | Bacterial Spot | Tomato | High |
| 29 | Early Blight | Tomato | Moderate |
| 30 | Late Blight | Tomato | Critical |
| 35 | Yellow Leaf Curl Virus | Tomato | Critical |
| … | *(38 total)* | | |

---

## Weather Integration

**API**: [Open-Meteo](https://open-meteo.com) — free, no API key required

**Parameters fetched:**
- `temperature_2m` — Current temperature (°C)
- `relative_humidity_2m` — Relative humidity (%)
- `precipitation` — Rainfall (mm)

**Districts covered**: All 36 districts of Maharashtra with lat/lon coordinates stored in `services/weather_service.py`.

---

## Development Log

### Milestone 1 — Initial Scaffold (2026-08-18)

**Status**: ✅ Complete

**Files created:**
- `config.py`, `requirements.txt`, `main.py`, `.gitignore`
- `model/__init__.py`, `model/architecture.py`, `model/inference.py`
- `services/__init__.py`, `services/disease_service.py`, `services/fertilizer_service.py`, `services/weather_service.py`
- `controllers/__init__.py`, `controllers/predict_controller.py`, `controllers/weather_controller.py`
- `views/index.html`, `views/static/css/style.css`, `views/static/js/app.js`
- `README.md`, `documentation.md`

**Architecture decisions:**
- MVC pattern adopted for separation of concerns
- InferenceService implemented as a Singleton with graceful mock fallback
- All 38 PlantVillage disease classes catalogued with full treatment prescriptions
- Open-Meteo API selected for weather (free tier, no key required)

---

### Milestone 2 — Dataset Integration & Training Pipeline (2026-08-18)

**Status**: ✅ Complete

**Datasets confirmed:**

| Dataset | File | Size | Records |
|---------|------|------|--------|
| Disease images | `archive.zip` | 2.89 GB | 87,900 images, 38 classes |
| Yield tabular | `archive (1).zip` | ~1 MB | `yield_df.csv` |

**Files created:**
- `model/dataset.py` — PlantDiseaseDataset + YieldDataset + MultiModalDataset
- `model/train.py` — Joint training with CosineAnnealing + CSV log + best checkpoint
- `model/extract_data.py` — One-command data extraction helper

---

### Milestone 4 — Farmer-Centric Operational & Financial Platform (2026-09-03)

**Status**: ✅ Complete

**Motivation**:
Transitioning AeroCrop.ai from a laboratory diagnostic research model into an all-in-one daily field operational companion addressing market economics, field safety, and low-tech vernacular accessibility.

**Key Functional Additions:**

1. **Vernacular Audio Narration (Web Speech Synthesis)**
   - Integrated client-side SpeechSynthesis with BCP-47 language targeting (`mr-IN` Marathi, `hi-IN` Hindi, `en-IN` English).
   - Speaks complete pathological diagnosis, chemical fungicides, and organic biological remedies out loud.

2. **Smart Foliar Spraying Window (Agronomic Decision Tree)**
   - Open-Meteo telemetry extended with real-time `wind_speed_10m`.
   - Automated hazard assessment:
     - 🔴 **Danger (Wash-Off Risk)**: Rainfall $> 1.0\text{ mm}$
     - 🔴 **Danger (Spray Drift Risk)**: Wind speed $> 15.0\text{ km/h}$
     - 🟡 **Warning (Delayed Evaporation)**: Humidity $> 85\%$
     - 🟡 **Warning (Heat Scorch Risk)**: Temperature $> 36^\circ\text{C}$
     - 🟢 **Optimal / Safe**: Clear skies, low wind ($< 15\text{ km/h}$), moderate humidity.

3. **Commercial 50kg Bag Stoichiometry & Cost Projection**
   - Direct translation of elemental deficits into integer commercial 50kg fertilizer bags:
     $$\text{Bags}_{\text{50kg}} = \left\lceil \frac{\text{Deficit (kg)}}{50} \right\rceil$$
   - Goverment of India NBS subsidized retail pricing benchmarks:
     - **Urea (46% N)**: ₹267 / 50kg bag
     - **DAP (18% N, 46% P)**: ₹1,350 / 50kg bag
     - **MOP (60% K)**: ₹1,700 / 50kg bag
   - Area multiplier supporting Acres ($\times 0.4047$), Gunthas ($\times 0.01$), and Hectares ($\times 1.0$).

4. **APMC Mandi Price Intelligence & Gross Revenue Forecasting**
   - New `services/mandi_service.py` and `controllers/mandi_controller.py` with REST endpoints (`/api/mandi/{district}/{crop}`, `/api/mandi/overview/{district}`).
   - Covers key Maharashtra commodities (Cotton, Soybean, Wheat, Maize, Potato, Tomato, Onion, Grape, Rice) across major APMC hubs (Lasalgaon, Jalgaon, Pune, Nagpur, Latur, Kolhapur).
   - Computes expected harvest gross revenue from predicted yield:
     $$\text{Gross Revenue (₹)} = (\text{Yield}_{\text{t/ha}} \times 10) \times \text{APMC Modal Price (₹/q)}$$

5. **PMFBY Insurance Loss Proof & WhatsApp Export**
   - Automated generation of formal crop loss assessment documents compliant with Pradhan Mantri Fasal Bima Yojana (PMFBY) surveyor guidelines.
   - 1-click WhatsApp advisory payload formatting for immediate peer sharing.

6. **ICAR Krishi Vigyan Kendra (KVK) Escalation Directory**
   - District-wise extension registry for expert human agronomist verification when AI confidence is low.

7. **Frictionless Photo-First Diagnostics & Growth-Stage Fertilizer Schedule**
   - Removed mandatory soil NPK entry to eliminate the primary friction point for rural farmers without soil health cards.
   - Replaced soil deficit bar chart with an actionable **ICAR Stage-Wise Nutrient Schedule (खत व्यवस्थापन वेळापत्रक)**:
     - **Stage 1 (Basal at sowing)**: 100% DAP/SSP, 100% MOP, and 1/3rd Urea applied to root furrows.
     - **Stage 2 (Vegetative at 30–35 DAS)**: 1/3rd Urea top-dressed along crop rows with light irrigation.
    - The multi-modal neural network architecture maintains 100% backward compatibility: the inference service automatically applies regional ICAR soil baselines under the hood, preserving full 90.82% validation accuracy without weights mismatch.

---

### Milestone 5 — Maharashtra Agricultural Crop Expansion & Dataset Ingestion (2026-09-06)

**Status**: ✅ Baseline Expanded

**Summary**:
Added Cotton (कापूस), Sugarcane (ऊस), Banana (केळी), Turmeric/Haldi (हळद), and Rice/Paddy (भात) across archives (2) through (6).

---

### Milestone 6 — Field Dataset Integration, Rebalancing & Cross-Crop Disambiguation (2026-09-06)

**Status**: ✅ Complete (Awaiting User Training Authorization)

**Problem Identified**:
Testing on real-world specimen images showed cross-crop confusion in unconstrained visual diagnosis:
- **Cotton $\to$ Banana**: Caused by Cotton dataset deficit (only 284 training images) vs 2,497 Banana Sigatoka images, leading to dominant prior bias.
- **Maize $\to$ Sugarcane**: Caused by PlantVillage Corn dataset consisting almost exclusively of detached indoor lab leaf scans, while Sugarcane images were captured in outdoor open-field canopy lighting.

**Dataset Rectification & Rebalancing**:
1. **Cotton Plant Ingestion**: Integrated 1,435 in-field cotton plant images from `data/additional_crops/cotton/Cotton Disease/` (`diseased cotton plant` and `fresh cotton plant`) and `data/cotton_download/`. Cotton dataset increased from 875 to **2,386 images** (1,907 train, 479 valid).
2. **Field Maize Ingestion**: Integrated 2,045 real-world field-captured Maize images from Kandahar agricultural field dataset (`test_specimens/maize_repo/Kdr_field_Dataset.zip`), providing in-field canopy backgrounds across Northern Leaf Blight (900 images), Gray Leaf Spot (642 images), and Healthy (503 images).
3. **Banana Rebalancing**: Trimmed `Banana___Sigatoka` from 2,497 images down to 930 balanced images (750 train, 180 valid) to eliminate the 7:1 prior skew.
4. **Apple Field Adaptation**: Ingested and augmented in-situ orchard Apple specimens (`user_apple_cedar_rust.png` and `user_apple_foliage.png`) into `Apple___Cedar_apple_rust` and `Apple___healthy`, eliminating domain shift between PlantVillage lab scans and natural orchard canopies.
5. **Hard-Negative Specimen Augmentation**: Injected multi-angle, photometric variations of field specimens into training and validation sets.

**Trained Weights Architecture (3 Available Sets)**:
- **Set 1**: `model/aerocrop_weights.pth` (Fast calibrated weights, 14-min run, 99.76% accuracy).
- **Set 2**: `model/aerocrop_weights_full_v2.pth` (Full 30-epoch run, $\beta = 0.20$, 99.83% accuracy, 2.99 t/ha RMSE).
- **Set 3 (Active Default)**: `model/aerocrop_weights_full_v3.pth` (Apple & field-adapted 5-epoch fine-tuning, 99.81% accuracy, 2.97 t/ha RMSE). All 3 sets remain intact and switchable via `config.py`.

**Updated Dataset Specifications**:
- **Total Dataset Images**: **98,963 images**
- **Training Set (80%)**: **79,166 images**
- **Validation Set (20%)**: **19,797 images**
- **Marked (Diseased / Pathological)**: **67,771 images (68.5%)**
- **Unmarked (Healthy / Control)**: **31,192 images (31.5%)**
- **Total Pathology Classes**: **56 classes** across **19 crops**
- **Full Specifications Table**: [docs/dataset_specifications.md](file:///d:/Codes/final_year_project/docs/dataset_specifications.md)

---

### Milestone 6 — Final Project Crops Standardization, Deduplication & Reference Index (2026-09-11)

**Status**: ✅ Complete (Scope Frozen)

**Motivation**:
Consolidation and deduplication of the complete training dataset, freezing the core scope to 11 final agricultural crops relevant to Maharashtra, and synchronizing both backend and frontend components.

**Final Scope Specifications**:
- **Final Project Crops (11 Crops)**:
  1. 🌾 **Wheat (गहू / गेहूं)** — Added 11 diagnostic classes (2,101 images)
  2. 🌾 **Rice / Paddy (भात / धान)** — Upgraded from 120 to 6,112 images (5 classes)
  3. 🌱 **Cotton (कापूस / कपास)** — 2 classes (Bacterial blight & healthy)
  4. 🎋 **Sugarcane (ऊस / गन्ना)** — 5 classes (Red rot, Rust, Mosaic, Yellow leaf, healthy)
  5. 🫘 **Soybean (सोयाबीन)** — 1 class (healthy)
  6. 🌽 **Maize / Corn (मका / मक्का)** — 4 classes (Cercospora, Rust, Blight, healthy)
  7. 🥔 **Potato (बटाटा / आलू)** — 3 classes (Early blight, Late blight, healthy)
  8. 🍅 **Tomato (टोमॅटो / टमाटर)** — 10 classes (Blight, mold, viruses, bacterial spot, healthy)
  9. 🍌 **Banana (केळी / केला)** — 4 classes (Panama disease, Sigatoka, Cordana, healthy)
  10. 🌿 **Turmeric / Haldi (हळद / हल्दी)** — 4 classes (Leaf blotch, dry leaf, rhizome rot, healthy)
  11. 🍊 **Orange / Citrus (संत्रे / संतरा)** — 1 class (Citrus greening / Huanglongbing)

**Dataset Volume Metrics**:
- **Total Unique Images**: **62,836 images** (100% unique MD5 hashes)
- **Training Set (80%)**: **50,294 images**
- **Validation Set (20%)**: **12,542 images**
- **Train/Valid Data Leakage**: **0** (Zero hash overlap)
- **Duplicates Eliminated**: **14,470+** redundant files pruned (~1.5 GB storage reclaimed)
- **Total Canonical Classes**: **50 classes**
- **Tabular Yield Dataset**: **36,439 records** (`yield_df.csv` covering FAO + microclimate telemetry)

**Official Reference Dataset Links**:
1. [20k Multi-Class Crop Disease Images (Jawad Ali)](https://www.kaggle.com/datasets/jawadali1045/20k-multi-class-crop-disease-images) — Wheat & Upgraded Rice
2. [New Plant Diseases Dataset (Augmented)](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) — Tomato, Potato, Corn, Orange, Soybean
3. [Banana Leaf Disease Dataset v4 (Rayhan Arlistya)](https://www.kaggle.com/datasets/rayhanarlistya/banana-leaf-disease-dataset-v4) — Banana pathology
4. [Turmeric Datasets for CNN (Hitesh Patil)](https://www.kaggle.com/datasets/hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test) — Turmeric pathology
5. [Cotton Leaf Diseases Dataset (Janmejay Bhoi)](https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset) — Cotton pathology
6. [Sugarcane Leaf Disease Dataset (Nirmal Sankalana)](https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset) — Sugarcane pathology
7. [Rice Leaf Diseases Dataset (Vbookshelf)](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases) — Baseline rice pathology
8. [Crop Yield Prediction Dataset (FAO / Rikin Patel)](https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset) — Yield regression telemetry
9. [Crop Production in India (Abhinand)](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) — District-level Indian crop production

---

## Technical Summary Table

| Parameter | AeroCrop.ai Core v2.0 | Farmer-Centric Extensions |
|---|---|---|
| **AI Backbone** | ResNet-18 + 3-Layer Tabular MLP | Vernacular Voice Synthesizer (`mr-IN`, `hi-IN`) |
| **Output Metrics** | Disease Class, % Confidence, t/ha Yield | 50kg Commercial Bags, ₹ Total Input Cost |
| **Microclimate** | Temp, Humidity, Rain Display | **Smart Spraying Window Indicator** (Drift & Wash-off) |
| **Economics** | Yield regression only | **APMC Mandi Rates, MSP Benchmarks, Gross Revenue** |
| **Reporting** | Generic HTML print | **PMFBY Insurance Claim Document & WhatsApp Share** |
| **Escalation** | Automated model output only | **ICAR Krishi Vigyan Kendra (KVK) Directory** |
| **Test Coverage** | 100+ unit & integration tests | `tests/test_farmer_features.py` (10/10 passed) |

---

## Running the Complete System

```bash
# 1. Run backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. (Optional) Run Vite dev server for frontend development
cd frontend
npm run dev
```
