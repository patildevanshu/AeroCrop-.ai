"""
AeroCrop.ai — Farmer Diagnosis History & Analytics Controller

Endpoints:
  GET    /api/farmer/history         → Paginated diagnostics history (filtered by plot/crop/severity)
  GET    /api/farmer/history/{id}    → Full details & report view for a diagnosis
  DELETE /api/farmer/history/{id}    → Remove a diagnosis record
  GET    /api/farmer/analytics       → Summary metrics (crop health %, top diseases, acres monitored)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.mongodb import get_db
from database.models import User
from services.auth_service import get_current_user
from services.history_service import HistoryService

logger = logging.getLogger("aerocrop.controllers.history")
router = APIRouter(prefix="/api/farmer", tags=["Farmer History & Analytics"])


@router.get("/history", summary="Get paginated diagnosis history")
async def get_history(
    plot_id: Optional[int] = Query(None, description="Filter by specific plot ID"),
    crop_type: Optional[str] = Query(None, description="Filter by crop (e.g. cotton, tomato)"),
    severity: Optional[str] = Query(None, description="Filter by severity: Low | Moderate | High | Critical"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch paginated historical diagnostics for the authenticated farmer."""
    result = await HistoryService.list_history(
        db=db,
        user_id=current_user.id,
        plot_id=plot_id,
        crop_type=crop_type,
        severity=severity,
        page=page,
        page_size=page_size,
    )
    return result


@router.get("/history/{record_id}", summary="Get full diagnosis details")
async def get_diagnosis_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Retrieve full prescription, NPK, and weather details for a single diagnosis."""
    detail = await HistoryService.get_diagnosis_detail(db, record_id, current_user.id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis record not found.")
    return detail


@router.delete("/history/{record_id}", summary="Delete a diagnosis record")
async def delete_diagnosis(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Delete a diagnosis record and associated image file."""
    success = await HistoryService.delete_diagnosis(db, record_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis record not found.")
    return {"status": "success", "message": "Diagnosis record deleted successfully."}


@router.get("/analytics", summary="Get farmer agricultural analytics summary")
async def get_farmer_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Aggregate health and acreage metrics for the farmer's dashboard."""
    stats = await HistoryService.get_farmer_analytics(db, current_user.id)
    return stats


@router.get("/crop-progress", summary="Get longitudinal crop health progress across analyses")
async def get_crop_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Returns progress tracking for each of the farmer's crops/plots:
    - Chronological list of analyses with pathology, yield, and treatment status
    - Health score (0-100) and trend (baseline, improving, recovered, deteriorating)
    - Comparative progression across consecutive diagnoses
    """
    progress = await HistoryService.get_crop_progress_for_user(db, current_user.id)
    return {"count": len(progress), "crops": progress}

