# AeroCrop.ai 🌿

> **Multi-Modal Deep Learning & Field Economics Platform for Maharashtra Agriculture**  
> *Wheat · Rice · Cotton · Sugarcane · Soybean · Maize · Potato · Tomato · Banana · Turmeric · Orange*

---

## Overview

**AeroCrop.ai** is an end-to-end precision agriculture and field-intelligence platform built for smallholder and commercial farmers across Maharashtra's 36 districts. Combining computer vision, microclimatic telemetry, and commercial agronomics, the platform transforms a single leaf photograph and soil reading into immediate operational and financial guidance.

### Key Capabilities

1. **🔬 Multi-Modal Disease Diagnosis (50 Canonical Classes, 11 Final Project Crops, 62,836 Images)**:
   - Vision backbone: **ResNet-18** extracting deep spatial disease patterns across 50 canonical pathology classes.
   - Dataset: **62,836 clean, unique images** partitioned strictly 80% train (50,294) / 20% valid (12,542) with zero data leakage.
   - Tabular backbone: **3-layer MLP** encoding soil nutrients ($N, P, K$) and Open-Meteo microclimate ($T, H, R$).
   - Dual-head output: Simultaneous disease classification and non-negative harvest yield regression ($t/\text{ha}$).

2. **💨 Smart Foliar Spraying Safety Window (हवामान फवारणी सल्ला)**:
   - Real-time weather hazard engine evaluating rainfall ($>1\text{ mm}$ wash-off hazard) and wind speed ($>15\text{ km/h}$ chemical drift hazard).
   - Instant visual badges (`🟢 Safe to Spray`, `🟡 Caution`, `🔴 Hold Spray`) and localized warnings in Marathi, Hindi, and English.

3. **🧬 Commercial 50kg Bags & Growth-Stage Fertilizer Schedule (खत नियोजन)**:
   - Converts standard ICAR Recommended Dose of Fertilizer (RDF) or soil deficit into physical **50kg commercial bags of Urea, DAP, and MOP**.
   - Prescribes a scientific 3-stage split application calendar: **Basal (sowing)**, **Vegetative (30 DAS)**, and **Flowering (60 DAS)**.
   - Subsidized statutory pricing under GoI Nutrient Based Subsidy (Urea ₹267, DAP ₹1,350, MOP ₹1,700).
   - Dynamic area toggle for **Acres (एकर)**, **Gunthas (गुंठा)**, and **Hectares**.

4. **🏛️ APMC Mandi Rates & Harvest Gross Revenue Forecasting (बाजारभाव)**:
   - Market intelligence across major Maharashtra APMC hubs (Lasalgaon, Jalgaon, Pune, Nagpur, Latur, Kolhapur).
   - Maps predicted yield into expected quintals per acre and calculates **Gross Revenue (₹)** compared against official Minimum Support Price (MSP) benchmarks.

5. **🔊 Vernacular Voice Narration (बोलणारा कृषी सल्लागार)**:
   - Browser-native Web Speech API (`mr-IN`, `hi-IN`, `en-IN`) speaks aloud the complete pathology and remedy advisory for hands-free field use.

6. **📋 PMFBY Insurance Loss Proof & WhatsApp 1-Click Sharing**:
   - Generates legal PDF claim documentation for the **Pradhan Mantri Fasal Bima Yojana (PMFBY)** with surveyor signature blocks and leaf specimen imagery.
   - 1-click sharing of diagnoses and fertilizer plans to WhatsApp.

7. **👨‍🌾 Farmer Plot Management & Persistent History**:
   - Secure phone/password authentication with JWT cookies.
   - Multi-plot cadastral registry (crop, district, survey number, area in acres, baseline soil NPK).
   - Full chronological diagnosis history and yield trends.

8. **📞 ICAR Krishi Vigyan Kendra (KVK) Escalation Directory**:
   - District-wise extension center phone directory for human expert second opinions on complex field pathology.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Deep Learning** | PyTorch 2.x · torchvision (ResNet-18) · NumPy · Pillow |
| **Backend API** | FastAPI · Uvicorn (ASGI) · Python 3.12 |
| **Database** | MongoDB · Motor (Async `pymongo`) · Pydantic V2 · bcrypt · PyJWT |
| **Frontend** | React 18 · TypeScript · Vite · Lucide Icons · Chart.js |
| **Legacy Fallback** | Vanilla HTML5 / CSS3 / JavaScript SPA |
| **Microclimate** | Open-Meteo REST API (hourly temperature, humidity, rainfall, wind) |
| **Market Data** | Maharashtra APMC Mandi Service + Agmarknet + GoI MSP benchmarks |
| **Testing** | pytest · pytest-asyncio · httpx (146 passing tests) |

---

## Quick Start

### 1. Prerequisites
- Python $\ge 3.10$ (tested on Python 3.12)
- Node.js $\ge 18$ & npm (for React/Vite frontend)

### 2. Clone & Setup Backend

```bash
git clone <your-repo-url>
cd final_year_project

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On Linux/macOS

# Install backend dependencies
pip install -r requirements.txt

# (Optional) For GPU CUDA acceleration:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 3. Build Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

*Note: FastAPI automatically serves `frontend/dist/` at `http://localhost:8000/`. If `dist/` is absent, it seamlessly falls back to `views/`.*

### 4. Run Application Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

---

### Project Structure

```
final_year_project/
│
├── backend/                    # ── FASTAPI BACKEND & BUSINESS SERVICES ─────
│   ├── controllers/            # REST API routers (predict, weather, mandi, auth, plots, history)
│   ├── services/               # Core business services (pathology, fertilizer, weather, mandi, etc.)
│   ├── database/               # Async SQLite engine, connection pooling, and SQLAlchemy models
│   ├── email_service/          # Node.js PDF & SMTP email dispatch microservice
│   ├── config.py               # Backend configuration, thresholds, MSP, and subsidized prices
│   ├── main.py                 # FastAPI application bootstrap, middleware, and SPA server
│   └── requirements.txt        # Backend Python dependencies
│
├── frontend/                   # ── MODERN REACT 18 + VITE CLIENT ───────────
│   ├── src/                    # React components, context, translations (EN, MR, HI)
│   ├── dist/                   # Production compiled assets (HTML, CSS, JS)
│   ├── legacy/                 # Migrated legacy vanilla HTML/CSS/JS fallback views
│   ├── package.json            # Node dependencies & Vite build scripts
│   └── vite.config.ts          # Vite build & proxy configuration
│
├── model/                      # ── DEEP LEARNING & MODEL INFERENCE ─────────
│   ├── architecture.py         # MultiModalAeroCropNet (ResNet-18 vision + 3-layer MLP tabular)
│   ├── dataset.py              # PyTorch Dataset loaders, image transforms, and normalisation
│   ├── train.py                # Multi-task training pipeline (CosineAnnealingLR)
│   ├── inference.py            # Singleton InferenceService (weights inference + mock fallback)
│   ├── ingest_crops.py         # Multi-crop dataset ingestion utilities
│   └── extract_data.py         # Data extraction scripts
│
├── data/                       # Local SQLite database (aerocrop.db)
├── uploads/                    # Farmer uploaded specimen images
├── tests/                      # Automated test suite (154 passed tests)
├── docs/                       # Architectural and technical documentation
├── Dockerfile                  # Multi-stage production container build
├── docker-compose.yml          # Unified container orchestration
├── DEPLOYMENT.md               # Complete single-command deployment guide
├── main.py                     # Root runner bridge (uvicorn main:app --reload)
├── config.py                   # Root configuration re-export bridge
└── requirements.txt            # Root dependencies list
```

---

## API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict` | Frictionless inference (Leaf image + District + Crop, soil NPK optional) |
| `GET` | `/api/weather/{district}` | Real-time weather, wind speed, and spray safety status |
| `GET` | `/api/mandi/{district}/{crop}` | APMC modal prices, min/max spread, MSP, and revenue |
| `GET` | `/api/mandi/overview/{district}` | District-wide multi-crop APMC price summary |
| `POST` | `/api/auth/register` | Register new farmer account |
| `POST` | `/api/auth/login` | Authenticate farmer and receive secure HTTP-only JWT cookie |
| `GET` | `/api/plots` | List logged-in farmer's land plots |
| `POST` | `/api/plots` | Add new agricultural land plot |
| `GET` | `/api/history` | List historical diagnoses with crop filters |
| `GET` | `/api/disease/classes` | List all 38 supported disease classes |
| `GET` | `/docs` | Interactive Swagger UI API documentation |

---

## Automated Test Suite

AeroCrop.ai features a comprehensive automated test suite with **155 unit, integration, and security tests** with 100% pass rate:

```bash
# Run all tests
pytest -v

# Run dedicated farmer-centric feature tests
pytest tests/test_farmer_features.py -v
```

---

## Official Reference Datasets & Verified Kaggle Links

All agricultural pathology imagery and agro-meteorological telemetry used across AeroCrop.ai are derived from public peer-reviewed datasets:

| # | Dataset | Source / Author | Volume & Content | Download Link |
| :- | :--- | :--- | :--- | :--- |
| 1 | **20k Multi-Class Crop Disease Images** | Jawad Ali | 2.51 GB (Wheat rusts, blight, pests; Rice blast, bacterial blight, tungro) | [jawadali1045/20k-multi-class-crop-disease-images](https://www.kaggle.com/datasets/jawadali1045/20k-multi-class-crop-disease-images) |
| 2 | **New Plant Diseases Dataset (Augmented)** | Vipul Patel / PlantVillage | 2.89 GB (Tomato, Potato, Corn, Orange, Soybean) | [vipoooool/new-plant-diseases-dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) |
| 3 | **Banana Leaf Disease Dataset v4** | Rayhan Arlistya | 430 MB (Panama disease, Sigatoka, Cordana) | [rayhanarlistya/banana-leaf-disease-dataset-v4](https://www.kaggle.com/datasets/rayhanarlistya/banana-leaf-disease-dataset-v4) |
| 4 | **Turmeric Datasets for CNN** | Hitesh Patil | 172 MB (Leaf blotch, Dry leaf, Rhizome rot, Healthy) | [hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test](https://www.kaggle.com/datasets/hiteshpatil95/turmeric-datasets-for-cnn-model-training-and-test) |
| 5 | **Cotton Leaf Diseases Dataset** | Janmejay Bhoi | 155 MB (Bacterial blight, healthy) | [janmejaybhoi/cotton-disease-dataset](https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset) |
| 6 | **Sugarcane Leaf Disease Dataset** | Nirmal Sankalana | 160 MB (Red rot, Rust, Mosaic, Yellow leaf, Healthy) | [nirmalsankalana/sugarcane-leaf-disease-dataset](https://www.kaggle.com/datasets/nirmalsankalana/sugarcane-leaf-disease-dataset) |
| 7 | **Rice Leaf Diseases Dataset** | Vbookshelf | 37 MB (Bacterial leaf blight, brown spot, leaf smut) | [vbookshelf/rice-leaf-diseases](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases) |
| 8 | **Crop Yield Prediction Dataset** | Rikin Patel / FAO | 1.56 MB (`yield_df.csv`, 28,242 rows + India records) | [patelris/crop-yield-prediction-dataset](https://www.kaggle.com/datasets/patelris/crop-yield-prediction-dataset) |
| 9 | **Crop Production in India** | Abhinand / MoA&FW | 2 MB (`crop_production.csv`, 246,000+ district rows) | [abhinand05/crop-production-in-india](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) |

---

## Academic Verification & Model Performance

- **Target Geography**: All 36 districts of Maharashtra, India.
- **Final Crop Scope**: 11 Field Crops (**Wheat, Rice, Cotton, Sugarcane, Soybean, Maize, Potato, Tomato, Banana, Turmeric, Orange**).
- **Taxonomy Volume**: 50 Canonical Classes, 62,836 Unique Images (50,294 Train / 12,542 Valid, 0 duplicates).
- **Exam / Viva Defense Guide**: Comprehensive technical Q&A covering model design, commercial stoichiometry, spray safety math, and rural deployment is documented in [PROJECT_REVIEW_QUESTIONS_AND_ANSWERS.md](file:///d:/Codes/final_year_project/PROJECT_REVIEW_QUESTIONS_AND_ANSWERS.md).
