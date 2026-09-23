"""
AeroCrop.ai — Predict Controller

Endpoints:
  POST /api/predict         → Full multi-modal inference
                              (disease + yield + weather combined)
                              + Persistent saving when user is authenticated
  GET  /api/disease/classes → 134-class disease knowledge base
  POST /api/model/reload    → Hot-reload weights without server restart

MVC Role: Controller — orchestrates Model + Services, returns structured JSON.
"""

from __future__ import annotations
import logging
from io import BytesIO
from typing import Optional

import re
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from PIL import Image
from motor.motor_asyncio import AsyncIOMotorDatabase

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.mongodb import get_db
from database.models import User, FarmPlot
from model.inference             import InferenceService, normalize_crop_name, AGRONOMIC_YIELD_BOUNDS
from services.auth_service       import get_optional_user
from services.disease_service    import DiseaseService
from services.history_service    import HistoryService
from services.weather_service    import WeatherService
from services.mandi_service      import MandiService
from services.email_service      import EmailService
from services.ensemble_service   import EnsembleService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Prediction"])

MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
Image.MAX_IMAGE_PIXELS = 25_000_000       # Prevent Decompression Bomb DoS attacks
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def is_valid_email(email_str: Optional[str]) -> bool:
    """Validate email address format."""
    if not email_str or not isinstance(email_str, str):
        return False
    return bool(EMAIL_REGEX.match(email_str.strip()))


class EmailReportRequest(BaseModel):
    email: str
    name: Optional[str] = "Farmer"
    crop: str
    district: str
    disease: dict
    yield_t_ha: Optional[float] = None
    weather: Optional[dict] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        cleaned = v.strip()
        if not is_valid_email(cleaned):
            raise ValueError(f"Invalid email address format: '{v}'")
        return cleaned


# Lazy-loaded singleton
_inference: InferenceService | None = None


def _get_inference() -> InferenceService:
    global _inference
    if _inference is None:
        _inference = InferenceService()
    return _inference


@router.post("/predict", summary="Multi-modal crop disease + yield inference")
async def predict(
    background_tasks: BackgroundTasks,
    image:    UploadFile = File(..., description="RGB leaf photograph (JPG/PNG)"),
    crop:     str        = Form("auto", description="Crop type (or 'auto' for automatic visual specimen detection)"),
    district: str        = Form(..., description="Maharashtra district name"),
    plot_id:  Optional[int] = Form(None, description="Optional Plot ID to link this diagnosis to"),
    email:    Optional[str] = Form(None, description="Optional Farmer email to receive PDF report"),
    optional_user: Optional[User] = Depends(get_optional_user),
    db:       AsyncIOMotorDatabase = Depends(get_db),
):

    """
    Unified inference endpoint — accepts a leaf image + district,
    returns disease diagnosis and yield forecast.
    If the farmer is logged in, automatically saves the assessment & image to their history.
    """
    # ── 1. Validate image ────────────────────────────────────────────────────
    try:
        image_bytes = await image.read()
        if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Uploaded image is too large ({len(image_bytes) / (1024*1024):.1f} MB). Maximum allowed size is 15 MB.",
            )
        _ = Image.open(BytesIO(image_bytes)).convert("RGB")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file. Upload a valid JPG or PNG.")

    # ── 2. Fetch live weather for the given district ──────────────────────────
    weather = await WeatherService.fetch_weather(district)
    temperature = weather["temperature"]
    humidity    = weather["humidity"]
    rainfall    = weather["rainfall"]

    # ── 3. Run multi-modal inference ─────────────────────────────────────────
    prelim_crop = crop if crop and crop.lower() != "auto" else "auto"
    try:
        inference_svc = _get_inference()
        result = inference_svc.predict(
            image_bytes=image_bytes,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            crop=prelim_crop,
        )
    except Exception as exc:
        logger.error("Inference failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(exc)}")

    # ── 3b. Agronomic Ensemble Cross-Verification (Option A Arbitration) ──────
    try:
        verified = await EnsembleService.verify(
            image_bytes=image_bytes,
            district=district,
            weather=weather,
            local_crop=prelim_crop,
            local_class_idx=result["disease_class"],
            local_confidence=result["confidence"],
        )
        if verified and (verified.get("out_of_distribution") or verified.get("is_supported") is False):
            reason_text = verified.get("reason") or (
                "This plant or disease specimen may not be present in our dataset (this is not guaranteed). "
                "The diagnosis below is based on our internal model's closest estimate."
            )
            logger.info("[PredictController] Specimen flagged as out-of-distribution: %s", reason_text)
            result["low_confidence"] = True
            # Keep internal model's prediction and confidence score intact (do not zero out)
            result["out_of_distribution"] = True
            result["ood_reason"] = reason_text
        elif verified and verified.get("verified") and "class_idx" in verified:
            v_idx = int(verified["class_idx"])
            v_info = DiseaseService.get_by_index(v_idx)
            if v_info:
                logger.info(
                    "[PredictController] Ensemble consensus: class %d -> %d (%s)",
                    result["disease_class"], v_idx, v_info.name
                )
                result["disease_class"] = v_idx
                result["confidence"] = float(verified.get("confidence", 0.96))
                result["mock"] = False
                result["low_confidence"] = False

            # Incorporate agronomic yield estimate from validator microservice if present
            val_yield = verified.get("yield")
            if val_yield and isinstance(val_yield, dict):
                val_pred = val_yield.get("predicted_yield_t_ha")
                if val_pred is not None and float(val_pred) > 0:
                    val_pred = float(val_pred)
                    if result.get("mock"):
                        result["yield_t_ha"] = round(val_pred, 2)
                    else:
                        local_yield = float(result.get("yield_t_ha", val_pred))
                        result["yield_t_ha"] = round(0.6 * val_pred + 0.4 * local_yield, 2)
                    result["yield_loss_pct"] = val_yield.get("yield_loss_pct")
                    result["baseline_yield_t_ha"] = val_yield.get("baseline_yield_t_ha")
                    result["yield_reason"] = val_yield.get("yield_reason")
                    logger.info(
                        "[PredictController] Yield updated via validator: %.2f t/ha (loss: %s%%)",
                        result["yield_t_ha"], result.get("yield_loss_pct")
                    )
    except Exception as exc:
        logger.debug("[PredictController] Ensemble cross-verification bypassed: %s", exc)

    # ── 3c. Local OOD heuristic fallback ──────────────────────────────────────
    # When the validator microservice (port 5005) is offline, `out_of_distribution`
    # is never set, and unsupported crops (e.g. mango) get classified as a random
    # disease from the 134-class taxonomy.  This local fallback catches those:
    #   • crop was auto-detected (user did not explicitly pick a crop)
    #   • model confidence is very low (< 45%), signalling the input doesn't
    #     map cleanly to any trained class.
    if (
        not result.get("out_of_distribution")
        and prelim_crop == "auto"
        and result.get("confidence", 1.0) < 0.45
    ):
        logger.info(
            "[PredictController] Local OOD heuristic triggered — auto-detect "
            "confidence %.2f%% < 45%% threshold. Flagging as out-of-distribution.",
            result["confidence"] * 100,
        )
        result["out_of_distribution"] = True
        result["low_confidence"] = True
        result["ood_reason"] = (
            "The uploaded plant specimen could not be confidently matched to any "
            "crop or disease in our 134-class agricultural dataset. "
            "Please upload a clear photograph of a supported crop leaf."
        )

    # ── 4. Disease knowledge lookup & Automatic Crop Resolution ──────────────
    disease_idx  = result["disease_class"]
    disease_info = DiseaseService.get_by_index(disease_idx)
    is_ood = bool(result.get("out_of_distribution"))

    if is_ood:
        final_crop_name = "Unsupported Crop / No Match"
        effective_crop_key = "unsupported"
        disease_payload = {
            "class_index":  -1,
            "name":         "No Match Found (Specimen Not in Dataset)",
            "crop":         "Unsupported Crop",
            "is_healthy":   False,
            "severity":     "N/A",
            "description":  result.get("ood_reason") or "Uploaded plant or foliage specimen does not match any crop in our 134-disease agricultural dataset.",
            "chemical_treatment": [],
            "organic_treatment": [],
            "chemical_cost": "₹0 / Acre",
            "organic_cost":  "₹0 / Acre",
            "confidence":   round(result.get("confidence", 0.0) * 100, 2),
            "probabilities": [],
            "warning":      result.get("ood_reason"),
        }
        mandi_payload = None
        result["yield_t_ha"] = 0.0
        result["yield_category"] = "unsupported"
        result["yield_category_label"] = "N/A"
    else:
        # Automatically detect crop from visual disease taxonomy or user selection
        if crop and crop.lower() != "auto":
            detected_crop_raw = crop.strip().capitalize()
        else:
            detected_crop_raw = disease_info.crop if disease_info else "Tomato"
        
        # Standardize crop key for mandi lookups & agronomic validation
        det_lower = detected_crop_raw.lower().strip()
        norm_key = normalize_crop_name(det_lower)
        if norm_key in config.SUPPORTED_CROPS:
            effective_crop_key = norm_key
        elif det_lower in config.SUPPORTED_CROPS:
            effective_crop_key = det_lower
        else:
            effective_crop_key = "tomato"

        final_crop_name = detected_crop_raw

        # Final agronomic calibration and clamping against the resolved crop
        bounds = AGRONOMIC_YIELD_BOUNDS.get(effective_crop_key)
        if bounds:
            min_y, max_y = bounds["min"], bounds["max"]
            curr_y = float(result.get("yield_t_ha", bounds["typical"]))
            if curr_y > max_y * 1.25 or curr_y < min_y * 0.65:
                result["yield_t_ha"] = round(min(max_y, max(min_y, bounds["typical"])), 2)
            else:
                result["yield_t_ha"] = round(min(max_y, max(min_y, curr_y)), 2)
            result["yield_category"] = bounds["category"]
            result["yield_category_label"] = bounds["category_label"]
        else:
            result.setdefault("yield_category", "general_crop")
            result.setdefault("yield_category_label", "Crop Yield")

        disease_payload = {
            "class_index":  disease_idx,
            "name":         disease_info.name         if disease_info else f"Class {disease_idx}",
            "crop":         final_crop_name,
            "is_healthy":   disease_info.is_healthy   if disease_info else False,
            "severity":     disease_info.severity     if disease_info else "Unknown",
            "description":  disease_info.description  if disease_info else "",
            "chemical_treatment": disease_info.chemical_treatment if disease_info else [],
            "organic_treatment":  disease_info.organic_treatment  if disease_info else [],
            "chemical_cost": disease_info.chemical_cost_display if disease_info else "₹0 / Acre",
            "organic_cost":  disease_info.organic_cost_display  if disease_info else "₹0 / Acre",
            "confidence":   round(result["confidence"] * 100, 2),
            "probabilities": result["probabilities"],
            "warning":      result.get("ood_reason") if result.get("out_of_distribution") else None,
        }

        # ── 5. Mandi price intelligence & revenue forecast for the AUTO-DETECTED crop
        mandi_payload = MandiService.get_market_rate(district, crop=effective_crop_key, yield_t_ha=result["yield_t_ha"])

    # ── 6. Persist to database if authenticated ──────────────────────────────
    saved_record_id = None
    saved_image_url = None

    if optional_user and not is_ood:
        # Authorization check: verify plot belongs to current user
        valid_plot_id = None
        if plot_id:
            owned_plot = await db.farm_plots.find_one({"id": plot_id, "user_id": optional_user.id})
            if owned_plot:
                valid_plot_id = owned_plot.get("id")
        if not valid_plot_id:
            # Auto-link to matching plot for this crop if user has one
            matched_plot = await db.farm_plots.find_one(
                {
                    "user_id": optional_user.id,
                    "$or": [
                        {"crop_type": final_crop_name.lower()},
                        {"crop_type": effective_crop_key.lower()},
                    ],
                },
                sort=[("id", -1)],
            )
            if matched_plot:
                valid_plot_id = matched_plot.get("id")
                logger.info(
                    "[PredictController] Auto-linked diagnosis to user #%d's plot #%d (%s - %s)",
                    optional_user.id, matched_plot.get("id"), matched_plot.get("plot_name"), matched_plot.get("crop_type")
                )

        try:
            saved_record = await HistoryService.save_diagnosis(
                db=db,
                user_id=optional_user.id,
                crop_type=final_crop_name.lower(),
                district=district,
                disease_class_idx=disease_idx,
                disease_name=disease_payload["name"],
                confidence=disease_payload["confidence"],
                severity=disease_payload["severity"],
                is_healthy=disease_payload["is_healthy"],
                predicted_yield_t_ha=result["yield_t_ha"],
                weather_temp=temperature,
                weather_hum=humidity,
                weather_rain=rainfall,
                mock_mode=result["mock"],
                low_confidence=result.get("low_confidence", False),
                plot_id=valid_plot_id,
                image_bytes=image_bytes,
                # Store all info analyses
                disease_payload=disease_payload,
                weather_payload=weather,
                mandi_payload=mandi_payload,
                system_telemetry={
                    "mock_mode": result["mock"],
                    "low_confidence": result.get("low_confidence", False),
                    "out_of_distribution": result.get("out_of_distribution", False),
                    "ood_reason": result.get("ood_reason", ""),
                    "ensemble_verified": True if "verified" in locals() and verified else False,
                    "model_weights": config.DEFAULT_WEIGHTS_FILE,
                    "yield_loss_pct": result.get("yield_loss_pct"),
                    "baseline_yield_t_ha": result.get("baseline_yield_t_ha"),
                    "yield_reason": result.get("yield_reason"),
                },
            )
            saved_record_id = saved_record.id
            saved_image_url = saved_record.image_url
        except Exception as exc:
            logger.warning("[PredictController] Could not persist diagnosis: %s", exc)

    # ── 7. Email Advisory PDF Dispatch is User-Initiated ───────────────────────
    # Automatic email dispatch on every prediction is disabled per user preference.
    # The farmer can click "Create Report & Send to Email" on-demand whenever needed.
    target_email = email.strip() if email and email.strip() else (optional_user.email if optional_user and optional_user.email else None)
    email_status = None

    # ── 8. Compose final response ─────────────────────────────────────────────
    return JSONResponse({
        "status":              "success",
        "mock_mode":           result["mock"],
        "low_confidence":      result.get("low_confidence", False),
        "out_of_distribution": result.get("out_of_distribution", False),
        "ood_reason":          result.get("ood_reason", ""),
        "crop":                final_crop_name,
        "crop_key":            effective_crop_key,
        "auto_detected":       True,
        "district":            district.title(),
        "plot_id":             valid_plot_id if optional_user else None,
        "saved_record_id":     saved_record_id,
        "image_url":           saved_image_url,
        "weather":             weather,
        "disease":             disease_payload,
        "yield_t_ha":          result["yield_t_ha"],
        "yield_category":      result.get("yield_category", "general_crop"),
        "yield_category_label": result.get("yield_category_label", "Crop Yield"),
        "yield_loss_pct":      result.get("yield_loss_pct"),
        "baseline_yield_t_ha": result.get("baseline_yield_t_ha"),
        "yield_reason":        result.get("yield_reason"),
        "mandi":               mandi_payload,
        "email_status":        email_status,
        "email_recipient":     target_email,
    })


@router.post("/predict/email-report", summary="Email generated advisory PDF report to farmer")
async def email_report(
    req: EmailReportRequest,
    optional_user: Optional[User] = Depends(get_optional_user),
):
    """
    On-demand endpoint to dispatch advisory report PDF directly to any farmer email.
    """
    target_name = req.name if req.name and req.name != "Farmer" else (optional_user.full_name if optional_user else "Farmer")
    report_data = {
        "crop": req.crop,
        "district": req.district,
        "disease": req.disease,
        "yield_t_ha": req.yield_t_ha,
        "weather": req.weather or {},
    }
    res = await EmailService.dispatch_report_email(
        farmer_email=req.email,
        report_data=report_data,
        farmer_name=target_name,
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=502,
            detail=res.get("error", "Failed to dispatch email with advisory PDF.")
        )
    return JSONResponse({
        "status": "success",
        "message": f"Advisory PDF report successfully sent to {req.email}",
        "details": res.get("details"),
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
            "chemical_cost":      d.chemical_cost_display,
            "organic_cost":       d.organic_cost_display,
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
