# AeroCrop.ai — Technical Documentation

> Living document. Updated after every development milestone.

---

## Project Overview

**AeroCrop.ai** is a Multi-Modal Multi-Task Deep Learning advisory platform for commercial agriculture in Maharashtra, India. It simultaneously performs four actions from a single leaf image + soil data submission:

1. **Disease Diagnosis** — 38-class classification with confidence %
2. **Treatment Prescription** — Chemical + organic recommendations
3. **Fertilizer Dosage** — Exact Urea, DAP, MOP quantities (kg/ha)
4. **Yield Forecast** — Expected harvest in tons/hectare (t/ha)

---

## Architecture

### MVC Structure

```
MVC Layer       | Directory          | Responsibility
─────────────── | ────────────────── | ──────────────────────────────────────
Model           | model/             | PyTorch neural network + inference service
Service         | services/          | Business logic (disease DB, NPK math, weather)
Controller      | controllers/       | FastAPI routes orchestrating model + services
View            | views/             | HTML/CSS/JS glassmorphic frontend
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
- `config.py` — Central configuration
- `requirements.txt` — Dependencies
- `model/__init__.py`, `model/architecture.py`, `model/inference.py`
- `services/__init__.py`, `services/disease_service.py`, `services/fertilizer_service.py`, `services/weather_service.py`
- `controllers/__init__.py`, `controllers/predict_controller.py`, `controllers/weather_controller.py`
- `views/index.html`, `views/static/css/style.css`, `views/static/js/app.js`
- `main.py`
- `README.md`, `documentation.md`

**Architecture decisions:**
- MVC pattern adopted for separation of concerns
- InferenceService implemented as a Singleton with graceful mock fallback
- All 38 PlantVillage disease classes catalogued with full treatment prescriptions
- Open-Meteo API selected for weather (free tier, no key required)

---

## Next Steps

- [ ] `model/train.py` — Training pipeline with synthetic + real dataset support
- [ ] `model/dataset.py` — PyTorch Dataset class for PlantVillage images
- [ ] Unit tests (`tests/`) — fertilizer math, disease lookup, weather fallback
- [ ] Model training on PlantVillage 87K dataset (Kaggle download required)
- [ ] Load trained `.pth` weights into `model/aerocrop_weights.pth`
