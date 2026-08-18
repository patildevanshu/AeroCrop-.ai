"""
AeroCrop.ai — FastAPI Application Entry Point

MVC Role: Application bootstrap
  - Registers Controller routers
  - Serves the View (static HTML/CSS/JS)
  - Configures CORS, logging, and startup events

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from controllers import predict_router, weather_router

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aerocrop")

# ── FastAPI App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AeroCrop.ai",
    description=(
        "Multi-Modal Deep Learning Platform for Crop Disease Diagnostics "
        "& Yield Forecasting — Maharashtra, India"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (CSS, JS) ─────────────────────────────────────────────────
STATIC_PATH = os.path.join(config.VIEWS_DIR, "static")
if os.path.exists(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# ── Register Controllers (Routers) ─────────────────────────────────────────
app.include_router(predict_router)
app.include_router(weather_router)


# ── Root Route — Serve Frontend ────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the main glassmorphic dashboard."""
    index_path = os.path.join(config.VIEWS_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return JSONResponse({"detail": "Frontend not found"}, status_code=404)


# ── Health Check ───────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health():
    """Returns service health and device info."""
    return {
        "status":  "ok",
        "device":  config.DEVICE,
        "version": "1.0.0",
        "crops":   list(config.CROP_NPK_TARGETS.keys()),
    }


# ── Startup Event ──────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("  🌿  AeroCrop.ai  v1.0.0 — Starting up")
    logger.info("  Device   : %s", config.DEVICE)
    logger.info("  Weights  : %s", config.WEIGHTS_PATH)
    logger.info("  API Docs : http://localhost:8000/docs")
    logger.info("  Frontend : http://localhost:8000/")
    logger.info("=" * 60)
