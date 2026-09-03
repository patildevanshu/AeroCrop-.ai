"""
AeroCrop.ai — FastAPI Application Entry Point

MVC Role: Application bootstrap
  - Registers Controller routers (Predict, Weather, Auth, Plots, History)
  - Serves the View (static HTML/CSS/JS & uploads)
  - Configures CORS, database lifecycle, logging, and startup events

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from controllers import (
    auth_router,
    history_router,
    plot_router,
    predict_router,
    weather_router,
    mandi_router,
)
from database.connection import init_db

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aerocrop")


# ── Lifespan (Startup & Shutdown Lifecycle Manager) ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    # ── Startup ────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  🌿  AeroCrop.ai  v1.0.0 — Starting up")
    logger.info("  Device   : %s", config.DEVICE)
    logger.info("  Weights  : %s", config.WEIGHTS_PATH)
    logger.info("  Database : %s", config.DATABASE_URL)
    logger.info("  API Docs : http://localhost:8000/docs")
    logger.info("  Frontend : http://localhost:8000/")
    logger.info("=" * 60)

    # Initialize database tables
    await init_db()

    yield
    # ── Shutdown ───────────────────────────────────────────────────────────
    logger.info("  🌿  AeroCrop.ai — Shutting down gracefully")


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
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (CSS, JS) & Uploads ───────────────────────────────────────
# Mount React built assets (Vite dist/assets) if present, otherwise legacy static
FRONTEND_DIST = getattr(config, "FRONTEND_DIST_DIR", os.path.join(config.BASE_DIR, "frontend", "dist"))
REACT_ASSETS_PATH = os.path.join(FRONTEND_DIST, "assets")

if os.path.exists(REACT_ASSETS_PATH):
    app.mount("/assets", StaticFiles(directory=REACT_ASSETS_PATH), name="assets")

STATIC_PATH = os.path.join(config.VIEWS_DIR, "static")
if os.path.exists(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

os.makedirs(config.UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=config.UPLOADS_DIR), name="uploads")

# ── Register Controllers (Routers) ─────────────────────────────────────────
app.include_router(auth_router)
app.include_router(plot_router)
app.include_router(history_router)
app.include_router(predict_router)
app.include_router(weather_router)
app.include_router(mandi_router)


# ── Root Route — Serve Frontend ────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the React frontend dashboard (or legacy HTML if not built)."""
    react_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index, media_type="text/html")

    legacy_index = os.path.join(config.VIEWS_DIR, "index.html")
    if os.path.exists(legacy_index):
        return FileResponse(legacy_index, media_type="text/html")

    return JSONResponse({"detail": "Frontend not found. Please build the frontend with 'npm run build'."}, status_code=404)


# ── Health Check ───────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health():
    """Returns service health, database status, and device info."""
    return {
        "status":  "ok",
        "device":  config.DEVICE,
        "version": "1.0.0",
        "crops":   list(config.CROP_NPK_TARGETS.keys()),
    }
