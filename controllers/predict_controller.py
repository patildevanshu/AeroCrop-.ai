"""
AeroCrop.ai — Predict Controller

Endpoints:
  POST /api/predict   → Full multi-modal inference
                       (disease + yield + fertilizer + weather combined)

MVC Role: Controller — orchestrates Model + Services, returns structured JSON.
"""

from __future__ import annotations
import logging
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.inference      import InferenceService
from services.disease_service    import DiseaseService
from services.fertilizer_service import FertilizerService
from services.weather_service    import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Prediction"])

# Lazy-loaded singleton
_inference: InferenceService | None = None

def _get_inference() -> InferenceService:
    global _inference
    if _inference is None:
        _inference = InferenceService()
    return _inference


@router.post("/predict", summary="Multi-modal crop disease + yield inference")
async def predict(
    image:    UploadFile = File(..., description="RGB leaf photograph (JPG/PNG)"),
    crop:     str        = Form(..., description="Crop type: cotton|wheat|maize|rice|potato"),
    district: str        = Form(..., description="Maharashtra district name"),
    N:        float      = Form(..., description="Soil Nitrogen level   (kg/ha)"),
    P:        float      = Form(..., description="Soil Phosphorus level (kg/ha)"),
    K:        float      = Form(..., description="Soil Potassium level  (kg/ha)"),
):
    """
    Unified inference endpoint — accepts a leaf image + soil data + district,
    returns disease diagnosis, fertilizer prescription, and yield forecast.
    """
    # ── 1. Validate image ────────────────────────────────────────────────────
    try:
        image_bytes = await image.read()
        _ = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file. Upload a valid JPG or PNG.")

    # ── 2. Fetch live weather for the given district ──────────────────────────
    weather = await WeatherService.fetch_weather(district)
    temperature = weather["temperature"]
    humidity    = weather["humidity"]
    rainfall    = weather["rainfall"]

    # ── 3. Run multi-modal inference ─────────────────────────────────────────
    try:
        inference_svc = _get_inference()
        result = inference_svc.predict(
            image_bytes=image_bytes,
            N=N, P=P, K=K,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            crop=crop,
        )
    except Exception as exc:
        logger.error("Inference failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(exc)}")

    # ── 4. Disease knowledge lookup ──────────────────────────────────────────
    disease_idx  = result["disease_class"]
    disease_info = DiseaseService.get_by_index(disease_idx)

    disease_payload = {
        "class_index":  disease_idx,
        "name":         disease_info.name         if disease_info else f"Class {disease_idx}",
        "crop":         disease_info.crop         if disease_info else crop.title(),
        "is_healthy":   disease_info.is_healthy   if disease_info else False,
        "severity":     disease_info.severity     if disease_info else "Unknown",
        "description":  disease_info.description  if disease_info else "",
        "chemical_treatment": disease_info.chemical_treatment if disease_info else [],
        "organic_treatment":  disease_info.organic_treatment  if disease_info else [],
        "confidence":   round(result["confidence"] * 100, 2),
        "probabilities": result["probabilities"],
    }

    # ── 5. Fertilizer recommendation ─────────────────────────────────────────
    fertilizer_payload = FertilizerService.calculate(crop, N, P, K)

    # ── 6. Compose final response ────────────────────────────────────────────
    return JSONResponse({
        "status":      "success",
        "mock_mode":   result["mock"],
        "crop":        crop.title(),
        "district":    district.title(),
        "weather":     weather,
        "disease":     disease_payload,
        "yield_t_ha":  result["yield_t_ha"],
        "fertilizer":  fertilizer_payload,
    })


@router.get("/disease/classes", summary="List all 38 disease classes")
async def list_diseases():
    """Returns the full 38-class disease taxonomy with treatments."""
    diseases = [
        {
            "class_index":         d.class_idx,
            "name":                d.name,
            "crop":                d.crop,
            "is_healthy":          d.is_healthy,
            "severity":            d.severity,
            "description":         d.description,
            "chemical_treatment":  d.chemical_treatment,
            "organic_treatment":   d.organic_treatment,
        }
        for d in DiseaseService.DISEASES
    ]
    return JSONResponse({"count": len(diseases), "diseases": diseases})
