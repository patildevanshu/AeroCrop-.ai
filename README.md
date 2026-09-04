# AeroCrop.ai 🌿

> **Multi-Modal Deep Learning & Field Economics Platform for Maharashtra Agriculture**  
> *Cotton · Soybean · Wheat · Maize · Potato · Tomato · Rice · Grape · Pepper*

---

## Overview

**AeroCrop.ai** is an end-to-end precision agriculture and field-intelligence platform built for smallholder and commercial farmers across Maharashtra's 36 districts. Combining computer vision, microclimatic telemetry, and commercial agronomics, the platform transforms a single leaf photograph and soil reading into immediate operational and financial guidance.

### Key Capabilities

1. **🔬 Multi-Modal Disease Diagnosis (90.82% Accuracy)**:
   - Vision backbone: **ResNet-18** extracting deep spatial disease patterns across 38 PlantVillage classes.
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
| **Database** | SQLite · SQLAlchemy (Async `aiosqlite`) · Passlib (bcrypt) · PyJWT |
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

## Project Structure

```
final_year_project/
│
├── main.py                     # FastAPI application entry point
├── config.py                   # Central configuration, MSP, subsidized bag prices
├── requirements.txt            # Python dependencies
├── documentation.md            # In-depth technical architecture document
├── PROJECT_REVIEW_QUESTIONS_AND_ANSWERS.md # Viva voce examination master guide
│
├── database/                   # ── DATABASE & ORM LAYER ────────────────────
│   ├── connection.py           # Async SQLite engine & session factory
│   └── models.py               # User, FarmerPlot, DiagnosisRecord schemas
│
├── model/                      # ── DEEP LEARNING MODEL LAYER ───────────────
│   ├── architecture.py         # MultiModalAeroCropNet (ResNet-18 + MLP)
│   ├── dataset.py              # Multi-modal PlantVillage PyTorch Dataset
│   ├── train.py                # Multi-task training pipeline (CosineAnnealingLR)
│   ├── inference.py            # Singleton InferenceService (90.82% weights / mock)
│   └── aerocrop_weights.pth    # Trained weights checkpoint
│
├── services/                   # ── BUSINESS & DOMAIN SERVICES ─────────────
│   ├── disease_service.py      # 38-class pathology database & dual prescriptions
│   ├── fertilizer_service.py   # NPK deficits, 50kg commercial bags, retail costs
│   ├── weather_service.py      # Open-Meteo telemetry & foliar spray decision tree
│   ├── mandi_service.py        # APMC market rates, trends, and revenue forecasting
│   ├── auth_service.py         # JWT tokens & bcrypt password hashing
│   ├── plot_service.py         # Plot CRUD & ownership verification
│   ├── history_service.py      # Diagnosis analytics & persistence
│   └── storage_service.py      # Local file & leaf photo storage provider
│
├── controllers/                # ── REST API CONTROLLERS ───────────────────
│   ├── predict_controller.py   # POST /api/predict
│   ├── weather_controller.py   # GET  /api/weather/{district}
│   ├── mandi_controller.py     # GET  /api/mandi/{district}/{crop}, overview
│   ├── auth_controller.py      # POST /api/auth/register, login, me, logout
│   ├── plot_controller.py      # CRUD /api/plots
│   └── history_controller.py   # GET  /api/history
│
├── frontend/                   # ── MODERN REACT 18 + VITE FRONTEND ─────────
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/      # Weather Radar, Mandi table, KVK directory
│   │   │   ├── diagnose/       # Image upload, Spray alert, Mandi card, Bags
│   │   │   ├── plots/          # Land plot management & cadastral cards
│   │   │   └── auth/           # Login / Register modals
│   │   ├── context/            # AuthContext, I18nContext (EN, MR, HI)
│   │   ├── utils/speech.ts     # Vernacular Web Speech API synthesis
│   │   └── types/index.ts      # TypeScript interfaces
│   └── dist/                   # Production build artifact
│
├── views/                      # ── LEGACY VANILLA SPA FALLBACK ─────────────
│   ├── index.html              # Glassmorphic HTML5 interface
│   └── static/css & js/        # Stylesheets and app.js logic
│
└── tests/                      # ── AUTOMATED TEST SUITE (146 TESTS) ────────
    ├── test_farmer_features.py # Spray windows, 50kg bags, APMC mandi, end-to-end
    ├── test_model_inference.py # Neural network inference, tensor shapes
    ├── test_fertilizer_service.py # Deficits, splits, SSP alternatives
    ├── test_weather_service.py # Open-Meteo API, caching, mock fallbacks
    ├── test_plots.py           # Multi-tenant plot isolation
    ├── test_auth.py            # Authentication & JWT security
    └── test_farmer_history.py  # Diagnosis analytics & pagination
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

AeroCrop.ai features a comprehensive automated test suite with **147 unit, integration, and security tests**:

```bash
# Run all tests
pytest -v

# Run dedicated farmer-centric feature tests
pytest tests/test_farmer_features.py -v
```

---

## Academic Verification & Model Performance

- **Trained Model Accuracy**: **90.82%** validation accuracy across 38 PlantVillage classes.
- **Yield Forecasting Error**: **6.72 t/ha** RMSE.
- **Weights File**: `model/aerocrop_weights.pth` (11.3M parameters, 45.1 MB).
- **Target Geography**: All 36 districts of Maharashtra, India.
- **Exam / Viva Defense Guide**: Comprehensive technical Q&A covering model design, commercial stoichiometry, spray safety math, and rural deployment is documented in [PROJECT_REVIEW_QUESTIONS_AND_ANSWERS.md](file:///d:/Codes/final_year_project/PROJECT_REVIEW_QUESTIONS_AND_ANSWERS.md).
