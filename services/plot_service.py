"""
AeroCrop.ai — Multi-Crop & Farm Plot Management Service

Allows farmers to manage multiple agricultural plots and diverse crops simultaneously
(e.g., Plot 1: 5 Acres Cotton, Plot 2: 2 Acres Tomato, Plot 3: 4 Acres Wheat).
"""

import logging
from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from database.models import DiagnosisRecord, FarmPlot

logger = logging.getLogger("aerocrop.plots")


class PlotService:
    """Service providing multi-crop plot management operations for farmers."""

    @staticmethod
    async def list_plots_for_user(db: AsyncSession, user_id: int) -> List[dict]:
        """
        List all farm plots owned by a user, including total diagnoses count
        and latest diagnosis health status.
        """
        query = (
            select(FarmPlot)
            .where(FarmPlot.user_id == user_id)
            .order_by(FarmPlot.id.desc())
        )
        result = await db.execute(query)
        plots = result.scalars().all()

        output = []
        for p in plots:
            # Query diagnoses for this plot (or matching crop if plot_id was null)
            diag_query = (
                select(DiagnosisRecord)
                .where(
                    DiagnosisRecord.user_id == user_id,
                    (DiagnosisRecord.plot_id == p.id) | (
                        (DiagnosisRecord.plot_id.is_(None)) &
                        (func.lower(DiagnosisRecord.crop_type) == func.lower(p.crop_type))
                    )
                )
                .order_by(DiagnosisRecord.created_at.desc())
            )
            diag_res = await db.execute(diag_query)
            all_diags = diag_res.scalars().all()

            total_diagnoses = len(all_diags)
            latest_diag = all_diags[0] if total_diagnoses > 0 else None

            # Recent analyses list
            analyses_summary = [
                {
                    "id": d.id,
                    "disease_name": d.disease_name,
                    "severity": d.severity or "None",
                    "is_healthy": bool(d.is_healthy),
                    "confidence": round(d.confidence, 1),
                    "predicted_yield_t_ha": round(d.predicted_yield_t_ha, 2),
                    "image_url": d.image_url,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                    "date_display": d.created_at.strftime("%d %b %Y") if d.created_at else "--",
                }
                for d in all_diags[:5]
            ]

            # Health score
            if latest_diag:
                if latest_diag.is_healthy:
                    health_score = 100
                elif latest_diag.severity == "Low":
                    health_score = 75
                elif latest_diag.severity == "Moderate":
                    health_score = 50
                elif latest_diag.severity == "High":
                    health_score = 25
                else:
                    health_score = 10
            else:
                health_score = 100

            output.append({
                "id": p.id,
                "plot_name": p.plot_name,
                "crop_type": p.crop_type,
                "area_acres": p.area_acres,
                "sowing_date": p.sowing_date.isoformat() if p.sowing_date else None,
                "soil_type": p.soil_type,
                "baseline_N": p.baseline_N,
                "baseline_P": p.baseline_P,
                "baseline_K": p.baseline_K,
                "notes": p.notes,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "total_diagnoses": total_diagnoses,
                "health_score": health_score,
                "recent_analyses": analyses_summary,
                "latest_diagnosis": {
                    "id": latest_diag.id,
                    "disease_name": latest_diag.disease_name,
                    "is_healthy": latest_diag.is_healthy,
                    "severity": latest_diag.severity,
                    "confidence": latest_diag.confidence,
                    "created_at": latest_diag.created_at.isoformat() if latest_diag.created_at else None,
                } if latest_diag else None,
            })
        return output

    @staticmethod
    async def create_plot(
        db: AsyncSession,
        user_id: int,
        plot_name: str,
        crop_type: str,
        area_acres: float = 1.0,
        sowing_date: Optional[date] = None,
        soil_type: str = "Medium Black",
        baseline_N: Optional[float] = None,
        baseline_P: Optional[float] = None,
        baseline_K: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Tuple[Optional[FarmPlot], Optional[str]]:
        """
        Create a new farm plot for a farmer with a designated crop.
        """
        crop_clean = crop_type.strip().lower()
        if crop_clean not in config.CROP_NPK_TARGETS:
            supported = ", ".join(config.CROP_NPK_TARGETS.keys())
            return None, f"Crop '{crop_type}' is not supported. Supported crops: {supported}"

        name_clean = plot_name.strip()
        if not name_clean:
            return None, "Plot name is required (e.g. 'North Field', 'Plot A')."

        if area_acres <= 0:
            return None, "Plot area must be greater than 0 acres."

        # Default soil baseline to ICAR targets if not specified
        target = config.CROP_NPK_TARGETS[crop_clean]
        b_N = baseline_N if baseline_N is not None else float(target["N"] * 0.5)
        b_P = baseline_P if baseline_P is not None else float(target["P"] * 0.5)
        b_K = baseline_K if baseline_K is not None else float(target["K"] * 0.5)

        new_plot = FarmPlot(
            user_id=user_id,
            plot_name=name_clean,
            crop_type=crop_clean,
            area_acres=float(area_acres),
            sowing_date=sowing_date,
            soil_type=soil_type.strip() if soil_type else "Medium Black",
            baseline_N=float(b_N),
            baseline_P=float(b_P),
            baseline_K=float(b_K),
            notes=notes.strip() if notes else None,
        )
        db.add(new_plot)
        await db.flush()
        await db.refresh(new_plot)
        logger.info("[PlotService] Created plot '%s' (%s, %.1f acres) for user %d", new_plot.plot_name, new_plot.crop_type, new_plot.area_acres, user_id)
        return new_plot, None

    @staticmethod
    async def get_plot(db: AsyncSession, plot_id: int, user_id: int) -> Optional[FarmPlot]:
        """Fetch a plot by ID ensuring ownership by user_id."""
        query = select(FarmPlot).where(FarmPlot.id == plot_id, FarmPlot.user_id == user_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def update_plot(
        db: AsyncSession,
        plot_id: int,
        user_id: int,
        plot_name: Optional[str] = None,
        crop_type: Optional[str] = None,
        area_acres: Optional[float] = None,
        sowing_date: Optional[date] = None,
        soil_type: Optional[str] = None,
        baseline_N: Optional[float] = None,
        baseline_P: Optional[float] = None,
        baseline_K: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Tuple[Optional[FarmPlot], Optional[str]]:
        """Update an existing farm plot."""
        plot = await PlotService.get_plot(db, plot_id, user_id)
        if not plot:
            return None, "Farm plot not found."

        if crop_type is not None:
            crop_clean = crop_type.strip().lower()
            if crop_clean not in config.CROP_NPK_TARGETS:
                return None, f"Crop '{crop_type}' is not supported."
            plot.crop_type = crop_clean

        if plot_name is not None and plot_name.strip():
            plot.plot_name = plot_name.strip()

        if area_acres is not None and area_acres > 0:
            plot.area_acres = float(area_acres)

        if sowing_date is not None:
            plot.sowing_date = sowing_date

        if soil_type is not None:
            plot.soil_type = soil_type.strip()

        if baseline_N is not None:
            plot.baseline_N = float(baseline_N)
        if baseline_P is not None:
            plot.baseline_P = float(baseline_P)
        if baseline_K is not None:
            plot.baseline_K = float(baseline_K)

        if notes is not None:
            plot.notes = notes.strip() or None

        await db.flush()
        await db.refresh(plot)
        return plot, None

    @staticmethod
    async def delete_plot(db: AsyncSession, plot_id: int, user_id: int) -> bool:
        """Delete a farm plot."""
        plot = await PlotService.get_plot(db, plot_id, user_id)
        if not plot:
            return False
        await db.delete(plot)
        await db.flush()
        logger.info("[PlotService] Deleted plot %d for user %d", plot_id, user_id)
        return True
