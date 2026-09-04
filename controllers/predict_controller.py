"""
AeroCrop.ai — Predict Controller

Endpoints:
  POST /api/predict         → Full multi-modal inference
                              (disease + yield + fertilizer + weather combined)
                              + Persistent saving when user is authenticated
  GET  /api/disease/classes → 38-class disease knowledge base
  POST /api/model/reload    → Hot-reload weights without server restart

MVC Role: Controller — orchestrates Model + Services, returns structured JSON.
"""

from __future__ import annotations
import logging
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection         import get_db
from database.models             import User, FarmPlot
from model.inference             import InferenceService
from services.auth_service       import get_optional_user
from services.disease_service    import DiseaseService
from services.fertilizer_service import FertilizerService
from services.history_service    import HistoryService
from services.weather_service    import WeatherService
from services.mandi_service      import MandiService

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
    crop:     str        = Form(..., description="Crop type (see /api/disease/classes for supported crops)"),
    district: str        = Form(..., description="Maharashtra district name"),
    N:        Optional[float] = Form(None, description="Optional Soil Nitrogen level   (kg/ha)"),
    P:        Optional[float] = Form(None, description="Optional Soil Phosphorus level (kg/ha)"),
    K:        Optional[float] = Form(None, description="Optional Soil Potassium level  (kg/ha)"),
    plot_id:  Optional[int] = Form(None, description="Optional Plot ID to link this diagnosis to"),
    optional_user: Optional[User] = Depends(get_optional_user),
    db:       AsyncSession = Depends(get_db),
):
    """
    Unified inference endpoint — accepts a leaf image + district (soil NPK optional),
    returns disease diagnosis, fertilizer prescription, and yield forecast.
    If the farmer is logged in, automatically saves the assessment & image to their history.
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
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            crop=crop,
            N=N,
            P=P,
            K=K,
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
    fertilizer_payload = FertilizerService.calculate(crop=crop, soil_N=N, soil_P=P, soil_K=K)

    # ── 6. Mandi price intelligence & revenue forecast ────────────────────────
    mandi_payload = MandiService.get_market_rate(district, crop, yield_t_ha=result["yield_t_ha"])

    # ── 7. Persist to database if authenticated ──────────────────────────────
    saved_record_id = None
    saved_image_url = None

    if optional_user:
        # Authorization check: verify plot belongs to current user
        valid_plot_id = None
        if plot_id:
            plot_res = await db.execute(
                select(FarmPlot).where(FarmPlot.id == plot_id, FarmPlot.user_id == optional_user.id)
            )
            owned_plot = plot_res.scalar_one_or_none()
            if owned_plot:
                valid_plot_id = owned_plot.id
            else:
                logger.warning(
                    "[PredictController] Plot #%d does not belong to user #%d. Omitting plot linkage.",
                    plot_id, optional_user.id
                )

        try:
            saved_record = await HistoryService.save_diagnosis(
                db=db,
                user_id=optional_user.id,
                crop_type=crop,
                district=district,
                disease_class_idx=disease_idx,
                disease_name=disease_payload["name"],
                confidence=disease_payload["confidence"],
                severity=disease_payload["severity"],
                is_healthy=disease_payload["is_healthy"],
                predicted_yield_t_ha=result["yield_t_ha"],
                soil_N=N,
                soil_P=P,
                soil_K=K,
                fertilizer_urea_kg=fertilizer_payload["fertilizers"]["Urea"],
                fertilizer_dap_kg=fertilizer_payload["fertilizers"]["DAP"],
                fertilizer_mop_kg=fertilizer_payload["fertilizers"]["MOP"],
                weather_temp=temperature,
                weather_hum=humidity,
                weather_rain=rainfall,
                mock_mode=result["mock"],
                low_confidence=result.get("low_confidence", False),
                plot_id=valid_plot_id,
                image_bytes=image_bytes,
            )
            saved_record_id = saved_record.id
            saved_image_url = saved_record.image_url
        except Exception as exc:
            logger.warning("[PredictController] Could not persist diagnosis: %s", exc)

    # ── 8. Compose final response ─────────────────────────────────────────────
    return JSONResponse({
        "status":          "success",
        "mock_mode":       result["mock"],
        "low_confidence":  result.get("low_confidence", False),
        "crop":            crop.title(),
        "district":        district.title(),
        "plot_id":         valid_plot_id if optional_user else None,
        "saved_record_id": saved_record_id,
        "image_url":       saved_image_url,
        "weather":         weather,
        "disease":         disease_payload,
        "yield_t_ha":      result["yield_t_ha"],
        "fertilizer":      fertilizer_payload,
        "mandi":           mandi_payload,
    })


@router.get("/disease/classes", summary="List all 38 disease classes")
async def list_diseases():
    """Returns the full 38-class disease taxonomy with treatments."""
    diseases = [
        {
            "class_index":        d.class_idx,
            "name":               d.name,
            "crop":               d.crop,
            "is_healthy":         d.is_healthy,
            "severity":           d.severity,
            "description":        d.description,
            "chemical_treatment": d.chemical_treatment,
            "organic_treatment":  d.organic_treatment,
        }
        for d in DiseaseService.DISEASES
    ]
    return JSONResponse({"count": len(diseases), "diseases": diseases})


@router.post("/model/reload", summary="Hot-reload model weights from disk", tags=["System"])
async def reload_model():
    """
    Reload model weights from disk without restarting the server.
    Useful immediately after a new training run completes.
    """
    import config as _cfg
    svc = _get_inference()
    try:
        svc._load_model()
        return JSONResponse({
            "status":    "reloaded",
            "mock_mode": svc.mock_mode,
            "weights":   str(_cfg.WEIGHTS_PATH),
        })
    except Exception as exc:
        logger.error("Model reload failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(exc)}")
