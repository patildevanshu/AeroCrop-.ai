"""
AeroCrop.ai — Persistent Diagnosis History & Analytics Service

Manages storage, retrieval, image caching, and statistical summarization of historical
crop diagnoses for registered farmers.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from database.models import DiagnosisRecord, FarmPlot
from services.disease_service import DiseaseService
from services.fertilizer_service import FertilizerService
from services.storage_service import get_storage_provider

logger = logging.getLogger("aerocrop.history")


class HistoryService:
    """Service for persistent diagnostic history management and analytics."""

    @staticmethod
    async def save_diagnosis(
        db: AsyncSession,
        user_id: int,
        crop_type: str,
        district: str,
        disease_class_idx: int,
        disease_name: str,
        confidence: float,
        severity: str,
        is_healthy: bool,
        predicted_yield_t_ha: float = 0.0,
        soil_N: Optional[float] = None,
        soil_P: Optional[float] = None,
        soil_K: Optional[float] = None,
        fertilizer_urea_kg: float = 0.0,
        fertilizer_dap_kg: float = 0.0,
        fertilizer_mop_kg: float = 0.0,
        weather_temp: float = 0.0,
        weather_hum: float = 0.0,
        weather_rain: float = 0.0,
        mock_mode: bool = False,
        low_confidence: bool = False,
        plot_id: Optional[int] = None,
        image_bytes: Optional[bytes] = None,
    ) -> DiagnosisRecord:
        """
        Persist a complete diagnosis assessment, save leaf image if provided,
        and link to farmer's profile and plot.
        """
        image_filename = None
        image_url = None

        if image_bytes:
            try:
                storage = get_storage_provider()
                image_filename, image_url = await storage.save_image(image_bytes, user_id)
            except Exception as exc:
                logger.warning("[HistoryService] Failed to save image via storage provider: %s", exc)

        record = DiagnosisRecord(
            user_id=user_id,
            plot_id=plot_id,
            crop_type=crop_type.strip().lower(),
            district=district.strip().lower(),
            image_filename=image_filename,
            image_url=image_url,
            disease_class_idx=disease_class_idx,
            disease_name=disease_name,
            confidence=float(confidence),
            severity=severity,
            is_healthy=is_healthy,
            predicted_yield_t_ha=float(predicted_yield_t_ha),
            soil_N=float(soil_N),
            soil_P=float(soil_P),
            soil_K=float(soil_K),
            fertilizer_urea_kg=float(fertilizer_urea_kg),
            fertilizer_dap_kg=float(fertilizer_dap_kg),
            fertilizer_mop_kg=float(fertilizer_mop_kg),
            weather_temp=float(weather_temp),
            weather_hum=float(weather_hum),
            weather_rain=float(weather_rain),
            mock_mode=mock_mode,
            low_confidence=low_confidence,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        logger.info("[HistoryService] Stored diagnosis #%d (%s) for user %d", record.id, record.disease_name, user_id)
        return record

    @staticmethod
    async def list_history(
        db: AsyncSession,
        user_id: int,
        plot_id: Optional[int] = None,
        crop_type: Optional[str] = None,
        severity: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Fetch paginated diagnostic records for a user with optional filters.
        """
        query = select(DiagnosisRecord).where(DiagnosisRecord.user_id == user_id)

        if plot_id is not None:
            query = query.where(DiagnosisRecord.plot_id == plot_id)
        if crop_type is not None and crop_type.strip():
            query = query.where(DiagnosisRecord.crop_type == crop_type.strip().lower())
        if severity is not None and severity.strip() and severity != "All":
            query = query.where(DiagnosisRecord.severity == severity.strip())

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await db.execute(count_query)).scalar_one() or 0

        # Paginate
        offset = max(0, (page - 1) * page_size)
        query = query.order_by(DiagnosisRecord.created_at.desc()).offset(offset).limit(page_size)
        
        result = await db.execute(query)
        records = result.scalars().all()

        items = []
        for r in records:
            # Query plot name if linked
            plot_name = None
            if r.plot_id:
                plot_res = await db.execute(select(FarmPlot.plot_name).where(FarmPlot.id == r.plot_id))
                plot_name = plot_res.scalar_one_or_none()

            items.append({
                "id": r.id,
                "plot_id": r.plot_id,
                "plot_name": plot_name,
                "crop_type": r.crop_type,
                "district": r.district,
                "image_url": r.image_url,
                "disease_class_idx": r.disease_class_idx,
                "disease_name": r.disease_name,
                "confidence": r.confidence,
                "severity": r.severity,
                "is_healthy": r.is_healthy,
                "predicted_yield_t_ha": r.predicted_yield_t_ha,
                "soil": {"N": r.soil_N, "P": r.soil_P, "K": r.soil_K},
                "fertilizers": {
                    "Urea": r.fertilizer_urea_kg,
                    "DAP": r.fertilizer_dap_kg,
                    "MOP": r.fertilizer_mop_kg,
                },
                "weather": {
                    "temperature": r.weather_temp,
                    "humidity": r.weather_hum,
                    "rainfall": r.weather_rain,
                },
                "low_confidence": r.low_confidence,
                "mock_mode": r.mock_mode,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
            "records": items,
        }

    @staticmethod
    async def get_diagnosis_detail(
        db: AsyncSession,
        record_id: int,
        user_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch full details of a specific diagnosis record, including
        re-hydrated disease treatments and fertilizer dosage advisory.
        """
        query = select(DiagnosisRecord).where(
            DiagnosisRecord.id == record_id,
            DiagnosisRecord.user_id == user_id,
        )
        result = await db.execute(query)
        record = result.scalar_one_or_none()
        if not record:
            return None

        # Fetch disease details from knowledge base
        disease_info = DiseaseService.get_by_index(record.disease_class_idx)
        # Fetch fertilizer calculations & interpretations
        fert_calc = FertilizerService.calculate(
            record.crop_type,
            record.soil_N,
            record.soil_P,
            record.soil_K,
        )

        plot_name = None
        if record.plot_id:
            plot_res = await db.execute(select(FarmPlot.plot_name).where(FarmPlot.id == record.plot_id))
            plot_name = plot_res.scalar_one_or_none()

        return {
            "id": record.id,
            "plot_id": record.plot_id,
            "plot_name": plot_name,
            "crop": record.crop_type.title(),
            "district": record.district.title(),
            "image_url": record.image_url,
            "disease": {
                "class_index": record.disease_class_idx,
                "name": record.disease_name,
                "crop": disease_info.crop if disease_info else record.crop_type.title(),
                "is_healthy": record.is_healthy,
                "severity": record.severity,
                "description": disease_info.description if disease_info else "",
                "chemical_treatment": disease_info.chemical_treatment if disease_info else [],
                "organic_treatment": disease_info.organic_treatment if disease_info else [],
                "confidence": record.confidence,
            },
            "yield_t_ha": record.predicted_yield_t_ha,
            "fertilizer": fert_calc,
            "weather": {
                "temperature": record.weather_temp,
                "humidity": record.weather_hum,
                "rainfall": record.weather_rain,
                "source": "Recorded Telemetry",
            },
            "low_confidence": record.low_confidence,
            "mock_mode": record.mock_mode,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }

    @staticmethod
    async def delete_diagnosis(
        db: AsyncSession,
        record_id: int,
        user_id: int,
    ) -> bool:
        """Delete a single diagnosis history record and clean up image file if present."""
        query = select(DiagnosisRecord).where(
            DiagnosisRecord.id == record_id,
            DiagnosisRecord.user_id == user_id,
        )
        result = await db.execute(query)
        record = result.scalar_one_or_none()
        if not record:
            return False

        # Delete stored image file via storage provider
        if record.image_filename:
            storage = get_storage_provider()
            await storage.delete_image(user_id, record.image_filename)

        await db.delete(record)
        await db.flush()
        return True

    @staticmethod
    async def get_farmer_analytics(
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Calculate aggregate summary metrics for a farmer's dashboard:
        - Total plots & acreage
        - Total diagnostics performed
        - Overall crop health rate (% healthy)
        - Top diagnosed diseases
        - Average predicted yield
        """
        # Plots summary
        plots_res = await db.execute(
            select(
                func.count(FarmPlot.id),
                func.sum(FarmPlot.area_acres),
            ).where(FarmPlot.user_id == user_id)
        )
        total_plots, total_acres = plots_res.one()
        total_plots = total_plots or 0
        total_acres = round(total_acres or 0.0, 1)

        # Diagnoses summary
        diag_res = await db.execute(
            select(
                func.count(DiagnosisRecord.id),
                func.sum(case((DiagnosisRecord.is_healthy == True, 1), else_=0)),
                func.avg(DiagnosisRecord.predicted_yield_t_ha),
            ).where(DiagnosisRecord.user_id == user_id)
        )
        total_diags, total_healthy, avg_yield = diag_res.one()
        total_diags = total_diags or 0
        total_healthy = total_healthy or 0
        health_rate = round((total_healthy / total_diags) * 100, 1) if total_diags > 0 else 100.0
        avg_yield = round(avg_yield or 0.0, 2)

        # Most frequent diseases
        freq_res = await db.execute(
            select(DiagnosisRecord.disease_name, func.count(DiagnosisRecord.id))
            .where(DiagnosisRecord.user_id == user_id, DiagnosisRecord.is_healthy == False)
            .group_by(DiagnosisRecord.disease_name)
            .order_by(func.count(DiagnosisRecord.id).desc())
            .limit(3)
        )
        top_diseases = [{"name": row[0], "count": row[1]} for row in freq_res.all()]

        return {
            "total_plots": total_plots,
            "total_acres": total_acres,
            "total_diagnoses": total_diags,
            "health_rate_percent": health_rate,
            "avg_yield_t_ha": avg_yield,
            "top_diseases": top_diseases,
        }
