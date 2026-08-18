"""
AeroCrop.ai — Central Configuration
All environment-agnostic constants for the platform.
"""

import os
import torch

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "model")
WEIGHTS_PATH = os.path.join(MODEL_DIR, "aerocrop_weights.pth")
VIEWS_DIR   = os.path.join(BASE_DIR, "views")
STATIC_DIR  = os.path.join(VIEWS_DIR, "static")

# ─── Device ───────────────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─── Model Architecture ───────────────────────────────────────────────────────
NUM_DISEASE_CLASSES = 38
IMAGE_SIZE          = 224
TABULAR_INPUT_DIM   = 6      # N, P, K, temperature, humidity, rainfall
TABULAR_HIDDEN_DIMS = [64, 64, 64]
TABULAR_OUTPUT_DIM  = 64
VISUAL_OUTPUT_DIM   = 512
FUSION_OUTPUT_DIM   = 128

# ─── Crop NPK Targets (kg/ha) — Based on ICAR recommendations ─────────────────
CROP_NPK_TARGETS = {
    "cotton": {"N": 120, "P": 60,  "K": 60},
    "wheat":  {"N": 120, "P": 60,  "K": 40},
    "maize":  {"N": 120, "P": 60,  "K": 40},
    "rice":   {"N": 100, "P": 50,  "K": 50},
    "potato": {"N": 120, "P": 80,  "K": 120},
}

# ─── Fertilizer Nutrient Content (fraction) ───────────────────────────────────
FERTILIZER_COMPOSITION = {
    "Urea":  {"N": 0.46, "P": 0.00, "K": 0.00},
    "DAP":   {"N": 0.18, "P": 0.46, "K": 0.00},  # Di-ammonium Phosphate
    "MOP":   {"N": 0.00, "P": 0.00, "K": 0.60},  # Muriate of Potash
}

# ─── Weather API ──────────────────────────────────────────────────────────────
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
]

# ─── Normalisation statistics for tabular inputs (approx ranges) ──────────────
TABULAR_NORM = {
    "N":           {"mean": 60.0,  "std": 30.0},
    "P":           {"mean": 40.0,  "std": 20.0},
    "K":           {"mean": 40.0,  "std": 20.0},
    "temperature": {"mean": 28.0,  "std": 8.0},
    "humidity":    {"mean": 65.0,  "std": 20.0},
    "rainfall":    {"mean": 5.0,   "std": 10.0},
}
