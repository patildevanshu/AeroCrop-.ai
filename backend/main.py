"""
AeroCrop.ai — FastAPI Application Entry Point (Backend)

MVC Role: Application bootstrap
  - Registers Controller routers (Predict, Weather, Auth, Plots, History)
  - Serves the View (React built dashboard & legacy static HTML/CSS/JS & uploads)
  - Configures CORS, database lifecycle, logging, and startup events

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    or from root:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

# ── Ensure backend and project root are in sys.path ─────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

for path in [PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import backend.config as config
from backend.controllers import (
    auth_router,
    history_router,
    plot_router,
    predict_router,
    weather_router,
    mandi_router,
)
from backend.database.mongodb import init_mongodb, close_mongodb

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
    logger.info("  MongoDB  : %s (DB: %s)", config.MONGODB_URL, config.MONGODB_DB_NAME)
    logger.info("  API Docs : http://localhost:8000/docs")
    logger.info("  Frontend : http://localhost:8000/")
    logger.info("=" * 60)

    # Initialize MongoDB connection, indexes, and sequences
    await init_mongodb()

    yield
    # ── Shutdown ───────────────────────────────────────────────────────────
    logger.info("  🌿  AeroCrop.ai — Shutting down gracefully")
    await close_mongodb()


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
_raw_cors = os.getenv("CORS_ORIGINS", "")
raw_list = [origin.strip() for origin in _raw_cors.split(",") if origin.strip()]

allow_all_regex = "*" in _raw_cors or not raw_list or "devanshupatil.tech" in _raw_cors

CORS_ORIGINS = list(dict.fromkeys([
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://aerocrop.devanshupatil.tech",
    "https://aerocrop-ai.devanshupatil.tech",
    "https://api-aerocrop.devanshupatil.tech",
] + [o for o in raw_list if o != "*"]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"^https?://.*$" if allow_all_regex else r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (CSS, JS) & Uploads ───────────────────────────────────────
# Mount React built assets (Vite dist/assets) if present
FRONTEND_DIST = getattr(config, "FRONTEND_DIST_DIR", os.path.join(config.BASE_DIR, "frontend", "dist"))
REACT_ASSETS_PATH = os.path.join(FRONTEND_DIST, "assets")

if os.path.exists(REACT_ASSETS_PATH):
    app.mount("/assets", StaticFiles(directory=REACT_ASSETS_PATH), name="assets")

STATIC_PATH = getattr(config, "STATIC_DIR", os.path.join(config.BASE_DIR, "frontend", "legacy", "static"))
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


# ── Catch-all Route for SPA Navigation ────────────────────────────────────
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    """Support client-side routing for React SPA while skipping API/docs routes."""
    if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "uploads/", "assets/", "static/")):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    react_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index, media_type="text/html")

    legacy_index = os.path.join(config.VIEWS_DIR, "index.html")
    if os.path.exists(legacy_index):
        return FileResponse(legacy_index, media_type="text/html")

    return JSONResponse({"detail": "Not Found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
