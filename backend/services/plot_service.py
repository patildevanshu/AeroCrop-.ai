"""
AeroCrop.ai — Multi-Crop & Farm Plot Management Service (MongoDB / Motor)

Allows farmers to manage multiple agricultural plots and diverse crops simultaneously
(e.g., Plot 1: 5 Acres Cotton, Plot 2: 2 Acres Tomato, Plot 3: 4 Acres Wheat).
"""

import logging
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

import config
from database.models import FarmPlot
from database.mongodb import get_next_sequence

logger = logging.getLogger("aerocrop.plots")


class PlotService:
    """Service providing multi-crop plot management operations using MongoDB."""

    @staticmethod
    async def list_plots_for_user(db: AsyncIOMotorDatabase, user_id: int) -> List[dict]:
        """
        List all farm plots owned by a user, including total diagnoses count
        and latest diagnosis health status.
        """
        plots_cursor = db.farm_plots.find({"user_id": user_id}).sort("id", -1)
        plots = await plots_cursor.to_list(length=500)

        output = []
        for p in plots:
            plot_id = p.get("id")
            crop_type = p.get("crop_type", "").lower()

            # Query diagnoses for this plot (or matching crop if plot_id was unlinked)
            diag_query = {
                "user_id": user_id,
                "$or": [
                    {"plot_id": plot_id},
                    {"plot_id": None, "crop_type": crop_type},
                ],
            }
            diags_cursor = db.analyses.find(diag_query).sort("created_at", -1)
            all_diags = await diags_cursor.to_list(length=500)

            total_diagnoses = len(all_diags)
            latest_diag = all_diags[0] if total_diagnoses > 0 else None

            # Recent analyses summary
            analyses_summary = []
            for d in all_diags[:5]:
                created_at = d.get("created_at")
                if isinstance(created_at, datetime):
                    created_iso = created_at.isoformat()
                    date_display = created_at.strftime("%d %b %Y")
                elif isinstance(created_at, str):
                    created_iso = created_at
                    date_display = created_at[:10]
                else:
                    created_iso = None
                    date_display = "--"

                disease_doc = d.get("disease", {})
                yield_doc = d.get("yield", d.get("yield_data", {}))

                analyses_summary.append({
                    "id": d.get("id"),
                    "disease_name": disease_doc.get("name", d.get("disease_name", "")),
                    "severity": disease_doc.get("severity", d.get("severity", "None")),
                    "is_healthy": bool(disease_doc.get("is_healthy", d.get("is_healthy", False))),
                    "confidence": round(float(disease_doc.get("confidence", d.get("confidence", 0.0))), 1),
                    "predicted_yield_t_ha": round(float(yield_doc.get("predicted_yield_t_ha", d.get("predicted_yield_t_ha", 0.0))), 2),
                    "image_url": d.get("image_url"),
                    "created_at": created_iso,
                    "date_display": date_display,
                })

            # Health score calculation
            if latest_diag:
                lat_disease = latest_diag.get("disease", {})
                is_healthy = lat_disease.get("is_healthy", latest_diag.get("is_healthy", False))
                severity = lat_disease.get("severity", latest_diag.get("severity", "None"))

                if is_healthy:
                    health_score = 100
                elif severity == "Low":
                    health_score = 75
                elif severity == "Moderate":
                    health_score = 50
                elif severity == "High":
                    health_score = 25
                else:
                    health_score = 10
            else:
                health_score = 100

            lat_diag_created = latest_diag.get("created_at") if latest_diag else None
            if isinstance(lat_diag_created, datetime):
                lat_diag_iso = lat_diag_created.isoformat()
            else:
                lat_diag_iso = lat_diag_created

            p_created = p.get("created_at")
            p_created_iso = p_created.isoformat() if isinstance(p_created, datetime) else p_created

            output.append({
                "id": p.get("id"),
                "plot_name": p.get("plot_name"),
                "crop_type": p.get("crop_type"),
                "area_acres": p.get("area_acres"),
                "sowing_date": p.get("sowing_date"),
                "soil_type": p.get("soil_type"),
                "baseline_N": p.get("baseline_N"),
                "baseline_P": p.get("baseline_P"),
                "baseline_K": p.get("baseline_K"),
                "notes": p.get("notes"),
                "created_at": p_created_iso,
                "total_diagnoses": total_diagnoses,
                "health_score": health_score,
                "recent_analyses": analyses_summary,
                "latest_diagnosis": {
                    "id": latest_diag.get("id"),
                    "disease_name": latest_diag.get("disease", {}).get("name", latest_diag.get("disease_name")),
                    "is_healthy": latest_diag.get("disease", {}).get("is_healthy", latest_diag.get("is_healthy")),
                    "severity": latest_diag.get("disease", {}).get("severity", latest_diag.get("severity")),
                    "confidence": latest_diag.get("disease", {}).get("confidence", latest_diag.get("confidence")),
                    "created_at": lat_diag_iso,
                } if latest_diag else None,
            })

        return output

    @staticmethod
    async def create_plot(
        db: AsyncIOMotorDatabase,
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
        Create a new farm plot for a farmer with a designated crop in MongoDB.
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

        target = config.CROP_NPK_TARGETS[crop_clean]
        b_N = baseline_N if baseline_N is not None else float(target["N"] * 0.5)
        b_P = baseline_P if baseline_P is not None else float(target["P"] * 0.5)
        b_K = baseline_K if baseline_K is not None else float(target["K"] * 0.5)

        new_id = await get_next_sequence("plot_id")
        now = datetime.now(timezone.utc)
        sowing_str = sowing_date.isoformat() if isinstance(sowing_date, date) else sowing_date

        plot_doc = {
            "id": new_id,
            "user_id": user_id,
            "plot_name": name_clean,
            "crop_type": crop_clean,
            "area_acres": float(area_acres),
            "sowing_date": sowing_str,
            "soil_type": soil_type.strip() if soil_type else "Medium Black",
            "baseline_N": float(b_N),
            "baseline_P": float(b_P),
            "baseline_K": float(b_K),
            "notes": notes.strip() if notes else None,
            "created_at": now,
        }

        await db.farm_plots.insert_one(plot_doc)
        new_plot = FarmPlot(**plot_doc)
        logger.info("[PlotService] Created plot '%s' (%s, %.1f acres) for user %d (ID: %d)", new_plot.plot_name, new_plot.crop_type, new_plot.area_acres, user_id, new_plot.id)
        return new_plot, None

    @staticmethod
    async def get_plot(db: AsyncIOMotorDatabase, plot_id: int, user_id: int) -> Optional[FarmPlot]:
        """Fetch a plot by ID ensuring ownership by user_id."""
        doc = await db.farm_plots.find_one({"id": plot_id, "user_id": user_id})
        return FarmPlot(**doc) if doc else None

    @staticmethod
    async def update_plot(
        db: AsyncIOMotorDatabase,
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
        """Update an existing farm plot in MongoDB."""
        plot = await PlotService.get_plot(db, plot_id, user_id)
        if not plot:
            return None, "Farm plot not found."

        updates = {}
        if crop_type is not None:
            crop_clean = crop_type.strip().lower()
            if crop_clean not in config.CROP_NPK_TARGETS:
                return None, f"Crop '{crop_type}' is not supported."
            updates["crop_type"] = crop_clean
            plot.crop_type = crop_clean

        if plot_name is not None and plot_name.strip():
            updates["plot_name"] = plot_name.strip()
            plot.plot_name = updates["plot_name"]

        if area_acres is not None and area_acres > 0:
            updates["area_acres"] = float(area_acres)
            plot.area_acres = updates["area_acres"]

        if sowing_date is not None:
            s_str = sowing_date.isoformat() if isinstance(sowing_date, date) else sowing_date
            updates["sowing_date"] = s_str
            plot.sowing_date = s_str

        if soil_type is not None:
            updates["soil_type"] = soil_type.strip()
            plot.soil_type = updates["soil_type"]

        if baseline_N is not None:
            updates["baseline_N"] = float(baseline_N)
            plot.baseline_N = updates["baseline_N"]
        if baseline_P is not None:
            updates["baseline_P"] = float(baseline_P)
            plot.baseline_P = updates["baseline_P"]
        if baseline_K is not None:
            updates["baseline_K"] = float(baseline_K)
            plot.baseline_K = updates["baseline_K"]

        if notes is not None:
            updates["notes"] = notes.strip() or None
            plot.notes = updates["notes"]

        if updates:
            await db.farm_plots.update_one({"id": plot_id, "user_id": user_id}, {"$set": updates})

        return plot, None

    @staticmethod
    async def delete_plot(db: AsyncIOMotorDatabase, plot_id: int, user_id: int) -> bool:
        """Delete a farm plot and unlink related analyses."""
        res = await db.farm_plots.delete_one({"id": plot_id, "user_id": user_id})
        if res.deleted_count == 0:
            return False

        # Nullify plot_id in linked analyses without deleting diagnostic records
        await db.analyses.update_many({"plot_id": plot_id, "user_id": user_id}, {"$set": {"plot_id": None, "plot_name": None}})
        logger.info("[PlotService] Deleted plot %d for user %d", plot_id, user_id)
        return True
