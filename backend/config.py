"""
AeroCrop.ai — Central Configuration
All environment-agnostic constants for the platform.
"""

import os
import torch

try:
    from dotenv import load_dotenv, dotenv_values
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    _root_dir = os.path.dirname(_backend_dir)
    # 1. Load root .env and backend/.env for backend settings
    for _env_file in [
        os.path.join(_root_dir, ".env"),
        os.path.join(_backend_dir, ".env"),
    ]:
        if os.path.exists(_env_file):
            _vals = dotenv_values(_env_file)
            for _k, _v in _vals.items():
                if _v and not os.environ.get(_k):
                    os.environ[_k] = str(_v)

    # 2. Extract SMTP credentials from email_service/.env without overriding backend PORT (PORT 5000 is for node microservice)
    _email_env = os.path.join(_backend_dir, "email_service", ".env")
    if os.path.exists(_email_env):
        _email_vals = dotenv_values(_email_env)
        for _k in ("FROM", "PASS", "EMAIL_USER", "EMAIL_PASS", "SMTP_USER", "SMTP_PASS"):
            if _k in _email_vals and _email_vals[_k] and not os.environ.get(_k):
                os.environ[_k] = str(_email_vals[_k])
except ImportError:
    pass

# ─── Paths ────────────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(BACKEND_DIR)
MODEL_DIR   = os.path.join(BASE_DIR, "model")
WEIGHTS_PATH_SET1 = os.path.join(MODEL_DIR, "aerocrop_weights_epoch80.pth")
WEIGHTS_PATH_SET2 = os.path.join(MODEL_DIR, "aerocrop_weights_epoch80.pth")
WEIGHTS_PATH_SET3 = os.path.join(MODEL_DIR, "aerocrop_weights_epoch80.pth")
DEFAULT_WEIGHTS_FILE = os.getenv("AEROCROP_WEIGHTS_FILE", "aerocrop_weights_epoch80.pth")
WEIGHTS_PATH = os.path.join(MODEL_DIR, DEFAULT_WEIGHTS_FILE)
VIEWS_DIR   = os.path.join(BASE_DIR, "frontend", "legacy")
STATIC_DIR  = os.path.join(VIEWS_DIR, "static")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
FRONTEND_DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DATA_DIR    = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# ─── Database & Auth ──────────────────────────────────────────────────────────
MONGODB_URL     = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
MONGODB_URI     = MONGODB_URL
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "aerocrop")

# Legacy SQLite path (for fallback/migration)
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "aerocrop.db")
DATABASE_URL    = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}")

JWT_SECRET_KEY             = os.getenv("JWT_SECRET_KEY", "aerocrop-maharashtra-farm-secret-key-2026")
JWT_ALGORITHM              = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7

if (not JWT_SECRET_KEY or JWT_SECRET_KEY == "aerocrop-maharashtra-farm-secret-key-2026") and os.getenv("ENVIRONMENT", "").lower() in ("prod", "production"):
    raise RuntimeError(
        "CRITICAL SECURITY CONFIGURATION ERROR: A secure custom JWT_SECRET_KEY must be configured in environment variables for production! "
        "Refusing to start with missing or default JWT secret key to prevent token forgery."
    )

# ─── Device ───────────────────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if DEVICE == "cpu":
    try:
        _threads = int(os.getenv("TORCH_NUM_THREADS", "4"))
        torch.set_num_threads(_threads)
    except Exception:
        pass

def _get_num_classes() -> int:
    _cpath = os.path.join(MODEL_DIR, "classes.json")
    if os.path.exists(_cpath):
        try:
            import json
            with open(_cpath, "r", encoding="utf-8") as f:
                cl = json.load(f)
                if len(cl) > 0:
                    return len(cl)
        except Exception:
            pass
    return 134

NUM_DISEASE_CLASSES = _get_num_classes()
IMAGE_SIZE          = 224
TABULAR_INPUT_DIM   = 3      # temperature, humidity, rainfall
TABULAR_HIDDEN_DIMS = [64, 64, 64]
TABULAR_OUTPUT_DIM  = 64
VISUAL_OUTPUT_DIM   = 512
FUSION_OUTPUT_DIM   = 128

WEATHER_FEATURES = ["temperature", "humidity", "rainfall"]

# ─── Supported Agricultural Crops ─────────────────────────────────────────────
SUPPORTED_CROPS = [
    "cotton", "sugarcane", "banana", "turmeric", "onion", "soybean",
    "wheat", "maize", "rice", "potato", "tomato", "pepper", "apple",
    "grape", "strawberry", "peach", "orange", "blueberry", "cherry",
    "raspberry", "squash",
]

# ─── Storage Configuration ───────────────────────────────────────────────────
STORAGE_PROVIDER    = os.getenv("STORAGE_PROVIDER", "local")  # local | s3
AWS_S3_BUCKET       = os.getenv("AWS_S3_BUCKET", "")
AWS_S3_REGION       = os.getenv("AWS_S3_REGION", "ap-south-1")

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
# These constants are used for Z-score normalisation at INFERENCE and TRAINING time.
#   temperature : °C
#   humidity    : relative humidity (%)
#   rainfall    : daily precipitation (mm)
TABULAR_NORM = {
    "temperature": {"mean": 28.0,  "std": 8.0},
    "humidity":    {"mean": 65.0,  "std": 20.0},
    "rainfall":    {"mean": 5.0,   "std": 10.0},
}

# ─── Email Microservice ──────────────────────────────────────────────────────
EMAIL_MICROSERVICE_BASE_URL = os.getenv(
    "EMAIL_MICROSERVICE_BASE_URL",
    "https://aero-email.devanshupatil.tech"
)
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", f"{EMAIL_MICROSERVICE_BASE_URL}/send-email")
EMAIL_OTP_SERVICE_URL = os.getenv("EMAIL_OTP_SERVICE_URL", f"{EMAIL_MICROSERVICE_BASE_URL}/send-otp")

# ─── Remote Agronomic Ensemble Validator ─────────────────────────────────────
# Internal microservice hook for distributed secondary path verification.
VALIDATOR_SERVICE_URL     = os.getenv("VALIDATOR_SERVICE_URL", "http://127.0.0.1:5005/api/v1/validate")
ENABLE_REMOTE_VALIDATOR   = os.getenv("ENABLE_REMOTE_VALIDATOR", "true").lower() == "true"
VALIDATOR_TIMEOUT_SECONDS = float(os.getenv("VALIDATOR_TIMEOUT_SECONDS", "35.0"))

# ─── Official Support ────────────────────────────────────────────────────────
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@devanshupatil.tech")

# ─── SMTP Email Delivery (Gmail / Standard SMTP) ─────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

# Sanitize email and app password (strip surrounding whitespace and spaces within app password)
_raw_user = os.getenv("SMTP_USER") or os.getenv("FROM") or os.getenv("EMAIL_USER") or ""
SMTP_USER = _raw_user.strip() if _raw_user else ""

_raw_pass = os.getenv("SMTP_PASS") or os.getenv("PASS") or os.getenv("EMAIL_PASS") or ""
SMTP_PASS = _raw_pass.replace(" ", "").strip() if _raw_pass else ""

SMTP_FROM = os.getenv("SMTP_FROM", f"AeroCrop.ai Support <{SMTP_USER}>" if SMTP_USER else "AeroCrop.ai Support")
SMTP_TIMEOUT_SECONDS = float(os.getenv("SMTP_TIMEOUT_SECONDS", "12.0"))
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
OTP_COOLDOWN_SECONDS = int(os.getenv("OTP_COOLDOWN_SECONDS", "30"))
DEV_ALLOW_OTP_BYPASS = os.getenv("DEV_ALLOW_OTP_BYPASS", "true" if os.getenv("ENVIRONMENT", "").lower() not in ("prod", "production") else "false").lower() == "true"
IS_SMTP_CONFIGURED = bool(
    SMTP_USER
    and SMTP_PASS
    and "your_email" not in SMTP_USER
    and "your_16_char" not in SMTP_PASS
)

# ─── Object Storage Provider (Local Filesystem / AWS S3) ──────────────────────
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local").lower()
AWS_S3_BUCKET    = os.getenv("AWS_S3_BUCKET", os.getenv("S3_BUCKET_NAME", ""))
AWS_S3_REGION    = os.getenv("AWS_S3_REGION", os.getenv("AWS_REGION", "ap-south-1"))

