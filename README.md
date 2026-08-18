# AeroCrop.ai 🌿

> **Multi-Modal Deep Learning Platform for Crop Disease Diagnostics & Yield Forecasting**
> *Maharashtra, India — Cotton · Wheat · Maize · Rice · Potato*

---

## Quick Start

### 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| pip | Latest |
| NVIDIA GPU *(optional)* | CUDA 12.1 (RTX 3050) |

### 2. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd final_year_project

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Install PyTorch (GPU-accelerated)

```bash
# For NVIDIA GPU (CUDA 12.1 — RTX 3050)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU only (slower inference)
pip install torch torchvision
```

### 4. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at **http://localhost:8000**

---

## Project Structure (MVC Architecture)

```
final_year_project/
│
├── main.py                     # FastAPI application entry point
├── config.py                   # Central configuration constants
├── requirements.txt            # Python dependencies
│
├── model/                      # ── MODEL LAYER ──────────────────────────
│   ├── __init__.py
│   ├── architecture.py         # MultiModalAeroCropNet (ResNet-18 + MLP)
│   ├── inference.py            # InferenceService (weights load / mock)
│   └── aerocrop_weights.pth    # ← Place trained weights here (if available)
│
├── services/                   # ── SERVICE LAYER (Business Logic) ───────
│   ├── __init__.py
│   ├── disease_service.py      # 38-class disease DB + treatments
│   ├── fertilizer_service.py   # NPK deficit & Urea/DAP/MOP calculations
│   └── weather_service.py      # Open-Meteo API + district coordinates
│
├── controllers/                # ── CONTROLLER LAYER ──────────────────────
│   ├── __init__.py
│   ├── predict_controller.py   # POST /api/predict
│   └── weather_controller.py   # GET  /api/weather/{district}
│
├── views/                      # ── VIEW LAYER (Frontend) ─────────────────
│   ├── index.html              # Glassmorphic dashboard
│   └── static/
│       ├── css/style.css       # Premium dark/glass stylesheet
│       └── js/app.js           # Frontend logic + Chart.js
│
├── README.md                   # ← You are here
└── documentation.md            # Full technical documentation
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve frontend dashboard |
| `GET` | `/api/health` | Server health + device info |
| `POST` | `/api/predict` | Full multi-modal inference |
| `GET` | `/api/disease/classes` | All 38 disease classes |
| `GET` | `/api/weather/districts` | List Maharashtra districts |
| `GET` | `/api/weather/{district}` | Live weather for a district |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

### POST `/api/predict` — Form Data

| Field | Type | Description |
|---|---|---|
| `image` | File | Leaf photograph (JPG/PNG) |
| `crop` | str | `cotton`, `wheat`, `maize`, `rice`, `potato` |
| `district` | str | Maharashtra district name |
| `N` | float | Soil Nitrogen (kg/ha) |
| `P` | float | Soil Phosphorus (kg/ha) |
| `K` | float | Soil Potassium (kg/ha) |

---

## Using Model Weights

If you have pre-trained weights (`.pth` file):

1. Copy the weights file to `model/aerocrop_weights.pth`
2. Restart the server — it will automatically detect and load them

Without weights, the system runs in **Smart Mock Mode** — results are deterministically derived from soil/weather inputs.

---

## Training the Model

*(Coming soon — training pipeline with synthetic data generator)*

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Deep Learning** | PyTorch · torchvision (ResNet-18) |
| **Backend** | FastAPI · uvicorn |
| **Frontend** | Vanilla HTML5 · CSS3 · JavaScript |
| **Charts** | Chart.js v4 |
| **Weather API** | Open-Meteo (free, no API key required) |
| **Architecture** | MVC (Model · View · Controller) |

---

## References

- **Disease Dataset**: [New Plant Diseases Dataset (Kaggle)](https://www.kaggle.com/vipoooool/new-plant-diseases-dataset) — 87,900 images, 38 classes
- **Disease Model**: Inspired by [PlantLeafDiseaseDetection](https://github.com/mayur7garg/PlantLeafDiseaseDetection)
- **Yield Model**: Inspired by [Crop-Yield-Prediction-using-Machine-Learning-Algorithms](https://github.com/ShubhamKJ123/Crop-Yield-Prediction-using-Machine-Learning-Algorithms)
- **NPK Targets**: ICAR recommendations for Maharashtra cash crops
