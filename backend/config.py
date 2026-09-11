"""
AeroCrop.ai — Central Configuration
All environment-agnostic constants for the platform.
"""

import os
import torch

# ─── Paths ────────────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(BACKEND_DIR)
MODEL_DIR   = os.path.join(BASE_DIR, "model")
WEIGHTS_PATH_SET1 = os.path.join(MODEL_DIR, "aerocrop_weights.pth")
WEIGHTS_PATH_SET2 = os.path.join(MODEL_DIR, "aerocrop_weights_full_v2.pth")
WEIGHTS_PATH_SET3 = os.path.join(MODEL_DIR, "aerocrop_weights_full_v3.pth")
DEFAULT_WEIGHTS_FILE = os.getenv(
    "AEROCROP_WEIGHTS_FILE",
    "aerocrop_weights_full_v3.pth"
    if os.path.exists(os.path.join(MODEL_DIR, "aerocrop_weights_full_v3.pth"))
    else (
        "aerocrop_weights_full_v2.pth"
        if os.path.exists(os.path.join(MODEL_DIR, "aerocrop_weights_full_v2.pth"))
        else "aerocrop_weights.pth"
    ),
)
WEIGHTS_PATH = os.path.join(MODEL_DIR, DEFAULT_WEIGHTS_FILE)
VIEWS_DIR   = os.path.join(BASE_DIR, "frontend", "legacy")
STATIC_DIR  = os.path.join(VIEWS_DIR, "static")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
FRONTEND_DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DATA_DIR    = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# ─── Database & Auth ──────────────────────────────────────────────────────────
MONGODB_URL     = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "aerocrop")

# Legacy SQLite path (for fallback/migration)
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "aerocrop.db")
DATABASE_URL    = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}")

JWT_SECRET_KEY             = os.getenv("JWT_SECRET_KEY", "aerocrop-maharashtra-farm-secret-key-2026")
JWT_ALGORITHM              = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7

if JWT_SECRET_KEY == "aerocrop-maharashtra-farm-secret-key-2026" and os.getenv("ENVIRONMENT", "").lower() in ("prod", "production"):
    import warnings
    warnings.warn(
        "CRITICAL SECURITY WARNING: Default JWT_SECRET_KEY is in use in production! "
        "Set JWT_SECRET_KEY in environment variables immediately to prevent authentication token forgery.",
        RuntimeWarning,
    )

# ─── Device ───────────────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if DEVICE == "cpu":
    try:
        _threads = int(os.getenv("TORCH_NUM_THREADS", "4"))
        torch.set_num_threads(_threads)
    except Exception:
        pass

# ─── Model Architecture ───────────────────────────────────────────────────────
NUM_DISEASE_CLASSES = 50
IMAGE_SIZE          = 224
TABULAR_INPUT_DIM   = 6      # N, P, K, temperature, humidity, rainfall
TABULAR_HIDDEN_DIMS = [64, 64, 64]
TABULAR_OUTPUT_DIM  = 64
VISUAL_OUTPUT_DIM   = 512
FUSION_OUTPUT_DIM   = 128

# ─── Crop NPK Targets (kg/ha) — Based on ICAR recommendations ─────────────────
# Covers all 14 crops present in the PlantVillage 38-class dataset.
# Crops not natively in ICAR Maharashtra guidelines use nearest proxy values.
CROP_NPK_TARGETS = {
    # Major Maharashtra cash & field crops (ICAR / MPKV Rahuri baselines)
    "cotton":      {"N": 120, "P": 60,  "K": 60},
    "sugarcane":   {"N": 250, "P": 115, "K": 115},
    "banana":      {"N": 200, "P": 50,  "K": 300},  # Heavy potassium consumer
    "turmeric":    {"N": 150, "P": 60,  "K": 100},  # Haldi rhizome nutrition
    "onion":       {"N": 100, "P": 50,  "K": 50},
    "soybean":     {"N": 30,  "P": 60,  "K": 40},   # Nitrogen-fixing legume
    "wheat":       {"N": 120, "P": 60,  "K": 40},
    "maize":       {"N": 120, "P": 60,  "K": 40},
    "rice":        {"N": 100, "P": 50,  "K": 50},
    "potato":      {"N": 120, "P": 80,  "K": 120},
    # Vegetable / fruit crops (ICAR horticulture guidelines)
    "tomato":      {"N": 120, "P": 80,  "K": 80},
    "pepper":      {"N": 100, "P": 60,  "K": 80},
    "apple":       {"N": 70,  "P": 35,  "K": 70},
    "grape":       {"N": 90,  "P": 45,  "K": 90},
    "strawberry":  {"N": 80,  "P": 40,  "K": 60},
    "peach":       {"N": 80,  "P": 40,  "K": 60},
    "orange":      {"N": 100, "P": 40,  "K": 60},
    # Other dataset crops (proxy values from nearest agronomic equivalents)
    "blueberry":   {"N": 70,  "P": 30,  "K": 50},  # proxy: berry crops
    "cherry":      {"N": 80,  "P": 40,  "K": 60},  # proxy: stone fruits
    "raspberry":   {"N": 70,  "P": 30,  "K": 50},  # proxy: berry crops
    "squash":      {"N": 100, "P": 50,  "K": 60},  # proxy: cucurbit crops
}

# ─── Storage Configuration ───────────────────────────────────────────────────
STORAGE_PROVIDER    = os.getenv("STORAGE_PROVIDER", "local")  # local | s3
AWS_S3_BUCKET       = os.getenv("AWS_S3_BUCKET", "")
AWS_S3_REGION       = os.getenv("AWS_S3_REGION", "ap-south-1")

# ─── Fertilizer Nutrient Content (fraction) ───────────────────────────────────
FERTILIZER_COMPOSITION = {
    # Standard primary straight fertilizers
    "Urea":               {"N": 0.46, "P": 0.00, "K": 0.00},
    "DAP":                {"N": 0.18, "P": 0.46, "K": 0.00},  # Di-ammonium Phosphate
    "MOP":                {"N": 0.00, "P": 0.00, "K": 0.60},  # Muriate of Potash
    # Alternative phosphorus source (0% N — prevents excess vegetative growth)
    "SSP":                {"N": 0.00, "P": 0.16, "K": 0.00, "S": 0.11},  # Single Superphosphate
    # Common Maharashtra multi-nutrient complexes
    "Complex_10_26_26":   {"N": 0.10, "P": 0.26, "K": 0.26},
    "Complex_12_32_16":   {"N": 0.12, "P": 0.32, "K": 0.16},
    "Complex_20_20_0_13": {"N": 0.20, "P": 0.20, "K": 0.00, "S": 0.13},
}

# Subsidized retail prices per 50kg bag in INR (₹)
FERTILIZER_BAG_PRICES = {
    "Urea": 267.0,   # Standard GoI subsidized Urea price (~₹266.50/bag)
    "DAP": 1350.0,   # Standard GoI subsidized DAP price (~₹1,350/bag)
    "MOP": 1700.0,   # Standard MOP price (~₹1,700/bag)
    "SSP": 500.0,    # Standard SSP price (~₹500/bag)
}

# ─── Weather API ──────────────────────────────────────────────────────────────
OPEN_METEO_BASE_URL        = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_TTL_SECONDS  = 1800  # 30 minutes in-memory caching TTL
WEATHER_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]

# ─── Normalisation statistics for tabular inputs ──────────────────────────────
# These constants are used for Z-score normalisation at INFERENCE time.
# Training dataset.py must use the same keys and semantics.
#   N, P, K : soil macronutrients (kg/ha)
#   temperature : °C
#   humidity    : relative humidity (%)
#   rainfall    : hourly precipitation (mm)
TABULAR_NORM = {
    "N":           {"mean": 60.0,  "std": 30.0},
    "P":           {"mean": 40.0,  "std": 20.0},
    "K":           {"mean": 40.0,  "std": 20.0},
    "temperature": {"mean": 28.0,  "std": 8.0},
    "humidity":    {"mean": 65.0,  "std": 20.0},
    "rainfall":    {"mean": 5.0,   "std": 10.0},
}

# ─── Email Microservice ──────────────────────────────────────────────────────
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "http://127.0.0.1:5000/send-email")

# ─── Remote Agronomic Ensemble Validator ─────────────────────────────────────
# Internal microservice hook for distributed secondary path verification.
VALIDATOR_SERVICE_URL     = os.getenv("VALIDATOR_SERVICE_URL", "http://127.0.0.1:5005/api/v1/validate")
ENABLE_REMOTE_VALIDATOR   = os.getenv("ENABLE_REMOTE_VALIDATOR", "true").lower() == "true"
VALIDATOR_TIMEOUT_SECONDS = float(os.getenv("VALIDATOR_TIMEOUT_SECONDS", "35.0"))

# ─── Official Support ────────────────────────────────────────────────────────
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@devanshupatil.tech")


