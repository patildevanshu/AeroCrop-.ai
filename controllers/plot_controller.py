"""
AeroCrop.ai — Multi-Crop & Farm Plot Controller

Endpoints:
  GET    /api/farmer/plots      → List farmer's crops/plots with diagnosis statistics
  POST   /api/farmer/plots      → Register a new plot and crop
  GET    /api/farmer/plots/{id} → Get details of a single plot
  PUT    /api/farmer/plots/{id} → Update plot properties
  DELETE /api/farmer/plots/{id} → Remove a farm plot
"""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import User
from services.auth_service import get_current_user
from services.plot_service import PlotService

logger = logging.getLogger("aerocrop.controllers.plots")
router = APIRouter(prefix="/api/farmer/plots", tags=["Farmer Crops & Plots"])


# ── Schemas ──────────────────────────────────────────────────────────────────
class CreatePlotRequest(BaseModel):
    plot_name: str = Field(..., min_length=1, max_length=120, description="Name or identifier for the plot")
    crop_type: str = Field(..., description="Crop type (e.g. cotton, tomato, wheat, etc.)")
    area_acres: float = Field(1.0, gt=0, description="Plot size in acres")
    sowing_date: Optional[date] = Field(None, description="Date of sowing (YYYY-MM-DD)")
    soil_type: str = Field("Medium Black", description="Soil classification")
    baseline_N: Optional[float] = Field(None, ge=0, description="Soil Nitrogen baseline (kg/ha)")
    baseline_P: Optional[float] = Field(None, ge=0, description="Soil Phosphorus baseline (kg/ha)")
    baseline_K: Optional[float] = Field(None, ge=0, description="Soil Potassium baseline (kg/ha)")
    notes: Optional[str] = Field(None, description="Optional notes or irrigation details")


class UpdatePlotRequest(BaseModel):
    plot_name: Optional[str] = None
    crop_type: Optional[str] = None
    area_acres: Optional[float] = Field(None, gt=0)
    sowing_date: Optional[date] = None
    soil_type: Optional[str] = None
    baseline_N: Optional[float] = Field(None, ge=0)
    baseline_P: Optional[float] = Field(None, ge=0)
    baseline_K: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.get("", summary="List all farm plots and crops for current farmer")
async def list_plots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all registered farm plots for the authenticated farmer."""
    plots = await PlotService.list_plots_for_user(db, current_user.id)
    return {"count": len(plots), "plots": plots}


@router.post("", summary="Register a new crop plot", status_code=status.HTTP_201_CREATED)
async def create_plot(
    req: CreatePlotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new farm plot / crop for the authenticated farmer."""
    plot, err = await PlotService.create_plot(
        db=db,
        user_id=current_user.id,
        plot_name=req.plot_name,
        crop_type=req.crop_type,
        area_acres=req.area_acres,
        sowing_date=req.sowing_date,
        soil_type=req.soil_type,
        baseline_N=req.baseline_N,
        baseline_P=req.baseline_P,
        baseline_K=req.baseline_K,
        notes=req.notes,
    )
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {
        "status": "success",
        "message": f"Plot '{plot.plot_name}' ({plot.crop_type.title()}) registered successfully.",
        "plot": {
            "id": plot.id,
            "plot_name": plot.plot_name,
            "crop_type": plot.crop_type,
            "area_acres": plot.area_acres,
            "sowing_date": plot.sowing_date.isoformat() if plot.sowing_date else None,
            "soil_type": plot.soil_type,
            "baseline_N": plot.baseline_N,
            "baseline_P": plot.baseline_P,
            "baseline_K": plot.baseline_K,
            "notes": plot.notes,
        },
    }


@router.get("/{plot_id}", summary="Get single plot details")
async def get_plot(
    plot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details for a single plot."""
    plot = await PlotService.get_plot(db, plot_id, current_user.id)
    if not plot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found.")

    return {
        "id": plot.id,
        "plot_name": plot.plot_name,
        "crop_type": plot.crop_type,
        "area_acres": plot.area_acres,
        "sowing_date": plot.sowing_date.isoformat() if plot.sowing_date else None,
        "soil_type": plot.soil_type,
        "baseline_N": plot.baseline_N,
        "baseline_P": plot.baseline_P,
        "baseline_K": plot.baseline_K,
        "notes": plot.notes,
        "created_at": plot.created_at.isoformat() if plot.created_at else None,
    }


@router.put("/{plot_id}", summary="Update plot details")
async def update_plot(
    plot_id: int,
    req: UpdatePlotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update properties of an existing plot."""
    plot, err = await PlotService.update_plot(
        db=db,
        plot_id=plot_id,
        user_id=current_user.id,
        plot_name=req.plot_name,
        crop_type=req.crop_type,
        area_acres=req.area_acres,
        sowing_date=req.sowing_date,
        soil_type=req.soil_type,
        baseline_N=req.baseline_N,
        baseline_P=req.baseline_P,
        baseline_K=req.baseline_K,
        notes=req.notes,
    )
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {
        "status": "success",
        "message": "Plot updated successfully.",
        "plot": {
            "id": plot.id,
            "plot_name": plot.plot_name,
            "crop_type": plot.crop_type,
            "area_acres": plot.area_acres,
            "sowing_date": plot.sowing_date.isoformat() if plot.sowing_date else None,
            "soil_type": plot.soil_type,
            "baseline_N": plot.baseline_N,
            "baseline_P": plot.baseline_P,
            "baseline_K": plot.baseline_K,
            "notes": plot.notes,
        },
    }


@router.delete("/{plot_id}", summary="Delete a farm plot")
async def delete_plot(
    plot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a farm plot."""
    deleted = await PlotService.delete_plot(db, plot_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found.")
    return {"status": "success", "message": "Plot deleted successfully."}
