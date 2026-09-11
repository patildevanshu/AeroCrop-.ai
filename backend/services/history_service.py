"""
AeroCrop.ai — Persistent Diagnosis History & Full Analysis Analytics Service (MongoDB / Motor)

Manages storage, retrieval, image caching, and statistical summarization of historical
crop diagnoses for registered farmers.
Stores ALL multi-modal analysis intelligence (disease taxonomy, full treatments,
fertilizer commercial bag dosages and costs, weather telemetry & spray windows,
mandi market intelligence & revenue projections, and ensemble verification).
"""

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

import config
from database.mongodb import get_next_sequence
from database.models import DiagnosisRecord
from services.disease_service import DiseaseService
from services.fertilizer_service import FertilizerService
from services.storage_service import get_storage_provider

logger = logging.getLogger("aerocrop.history")


class HistoryService:
    """Service for full-fidelity diagnostic history management and analytics using MongoDB."""

    @staticmethod
    async def save_diagnosis(
        db: AsyncIOMotorDatabase,
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
        # Extended parameters for full analysis storage:
        disease_payload: Optional[Dict[str, Any]] = None,
        fertilizer_payload: Optional[Dict[str, Any]] = None,
        weather_payload: Optional[Dict[str, Any]] = None,
        mandi_payload: Optional[Dict[str, Any]] = None,
        system_telemetry: Optional[Dict[str, Any]] = None,
    ) -> DiagnosisRecord:
        """
        Persist a complete diagnosis assessment in MongoDB, including all multi-modal
        treatments, fertilizer prescriptions, weather telemetry, and mandi projections.
        """
        image_filename = None
        image_url = None

        if image_bytes:
            try:
                storage = get_storage_provider()
                image_filename, image_url = await storage.save_image(image_bytes, user_id)
            except Exception as exc:
                logger.warning("[HistoryService] Failed to save image via storage provider: %s", exc)

        # Lookup plot name if linked to a plot
        plot_name = None
        if plot_id:
            plot_doc = await db.farm_plots.find_one({"id": plot_id, "user_id": user_id})
            if plot_doc:
                plot_name = plot_doc.get("plot_name")

        # 1. Disease payload construction
        disease_info = DiseaseService.get_by_index(disease_class_idx)
        full_disease = {
            "class_index": int(disease_class_idx),
            "name": disease_name or (disease_info.name if disease_info else f"Class {disease_class_idx}"),
            "crop": crop_type.title(),
            "confidence": float(confidence or 0.0),
            "severity": severity or (disease_info.severity if disease_info else "None"),
            "is_healthy": bool(is_healthy),
            "description": disease_info.description if disease_info else "",
            "chemical_treatment": disease_info.chemical_treatment if disease_info else [],
            "organic_treatment": disease_info.organic_treatment if disease_info else [],
            "probabilities": None,
        }
        if disease_payload:
            full_disease.update({k: v for k, v in disease_payload.items() if v is not None})

        # 2. Yield payload construction
        yield_val = float(predicted_yield_t_ha or 0.0)
        yield_data = {
            "predicted_yield_t_ha": round(yield_val, 2),
            "quintals_per_ha": round(yield_val * 10.0, 2),
            "quintals_per_acre": round(yield_val * 4.047, 2),
        }

        # 3. Soil payload construction
        soil_data = {
            "N": float(soil_N) if soil_N is not None else None,
            "P": float(soil_P) if soil_P is not None else None,
            "K": float(soil_K) if soil_K is not None else None,
            "tested": soil_N is not None,
        }

        # 4. Fertilizer payload construction
        if not fertilizer_payload:
            fertilizer_payload = FertilizerService.calculate(
                crop=crop_type.lower(),
                soil_N=soil_N,
                soil_P=soil_P,
                soil_K=soil_K,
            )
        else:
            # Ensure Urea, DAP, MOP are present
            if "fertilizers" not in fertilizer_payload:
                fertilizer_payload["fertilizers"] = {
                    "Urea": fertilizer_urea_kg,
                    "DAP": fertilizer_dap_kg,
                    "MOP": fertilizer_mop_kg,
                }

        # 5. Weather payload construction
        full_weather = {
            "temperature": float(weather_temp or 0.0),
            "humidity": float(weather_hum or 0.0),
            "rainfall": float(weather_rain or 0.0),
            "wind_speed": 10.0,
            "spray_window": None,
            "source": "live",
        }
        if weather_payload:
            full_weather.update({k: v for k, v in weather_payload.items() if v is not None})

        # 6. Telemetry construction
        full_telemetry = {
            "mock_mode": bool(mock_mode),
            "low_confidence": bool(low_confidence),
            "out_of_distribution": False,
            "ood_reason": "",
            "ensemble_verified": False,
            "model_weights": config.DEFAULT_WEIGHTS_FILE,
        }
        if system_telemetry:
            full_telemetry.update(system_telemetry)

        new_id = await get_next_sequence("analysis_id")
        now = datetime.now(timezone.utc)

        doc = {
            "id": new_id,
            "user_id": user_id,
            "plot_id": plot_id,
            "plot_name": plot_name,
            "crop_type": crop_type.strip().lower(),
            "district": district.strip().title(),
            "image_filename": image_filename,
            "image_url": image_url,
            "disease": full_disease,
            "yield": yield_data,
            "yield_data": yield_data,
            "soil": soil_data,
            "fertilizer": fertilizer_payload,
            "weather": full_weather,
            "mandi": mandi_payload,
            "system_telemetry": full_telemetry,
            "created_at": now,
            "updated_at": now,
        }

        await db.analyses.insert_one(doc)
        record = DiagnosisRecord(**doc)
        logger.info("[HistoryService] Stored rich diagnosis #%d (%s) for user %d in MongoDB", record.id, record.disease_name, user_id)
        return record

    @staticmethod
    async def list_history(
        db: AsyncIOMotorDatabase,
        user_id: int,
        plot_id: Optional[int] = None,
        crop_type: Optional[str] = None,
        severity: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Fetch paginated diagnostic records for a user with optional filters from MongoDB."""
        filter_query: Dict[str, Any] = {"user_id": user_id}

        if plot_id is not None:
            filter_query["plot_id"] = plot_id
        if crop_type is not None and crop_type.strip():
            filter_query["crop_type"] = crop_type.strip().lower()
        if severity is not None and severity.strip() and severity != "All":
            filter_query["$or"] = [
                {"disease.severity": severity.strip()},
                {"severity": severity.strip()},
            ]

        total_count = await db.analyses.count_documents(filter_query)
        offset = max(0, (page - 1) * page_size)

        cursor = db.analyses.find(filter_query).sort("created_at", -1).skip(offset).limit(page_size)
        records = await cursor.to_list(length=page_size)

        items = []
        for r in records:
            d_doc = r.get("disease", {})
            y_doc = r.get("yield", r.get("yield_data", {}))
            s_doc = r.get("soil", {})
            f_doc = r.get("fertilizer", {})
            w_doc = r.get("weather", {})
            t_doc = r.get("system_telemetry", {})

            created_at = r.get("created_at")
            if isinstance(created_at, datetime):
                created_iso = created_at.isoformat()
            else:
                created_iso = created_at

            items.append({
                "id": r.get("id"),
                "plot_id": r.get("plot_id"),
                "plot_name": r.get("plot_name"),
                "crop_type": r.get("crop_type"),
                "district": r.get("district"),
                "image_url": r.get("image_url"),
                "disease_class_idx": d_doc.get("class_index", r.get("disease_class_idx", 0)),
                "disease_name": d_doc.get("name", r.get("disease_name", "")),
                "confidence": d_doc.get("confidence", r.get("confidence", 0.0)),
                "severity": d_doc.get("severity", r.get("severity", "None")),
                "is_healthy": d_doc.get("is_healthy", r.get("is_healthy", False)),
                "predicted_yield_t_ha": y_doc.get("predicted_yield_t_ha", r.get("predicted_yield_t_ha", 0.0)),
                "soil": {
                    "N": s_doc.get("N", r.get("soil_N")),
                    "P": s_doc.get("P", r.get("soil_P")),
                    "K": s_doc.get("K", r.get("soil_K")),
                },
                "fertilizers": f_doc.get("fertilizers", {
                    "Urea": r.get("fertilizer_urea_kg", 0.0),
                    "DAP": r.get("fertilizer_dap_kg", 0.0),
                    "MOP": r.get("fertilizer_mop_kg", 0.0),
                }),
                "weather": {
                    "temperature": w_doc.get("temperature", r.get("weather_temp", 0.0)),
                    "humidity": w_doc.get("humidity", r.get("weather_hum", 0.0)),
                    "rainfall": w_doc.get("rainfall", r.get("weather_rain", 0.0)),
                },
                "low_confidence": t_doc.get("low_confidence", r.get("low_confidence", False)),
                "mock_mode": t_doc.get("mock_mode", r.get("mock_mode", False)),
                "created_at": created_iso,
            })

        return {
            "count": total_count,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
            "records": items,
        }

    @staticmethod
    async def get_diagnosis_detail(
        db: AsyncIOMotorDatabase,
        record_id: int,
        user_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch full details of a specific diagnosis record from MongoDB,
        returning the complete stored analysis document (treatments, fertilizers, weather, mandi).
        """
        record = await db.analyses.find_one({"id": record_id, "user_id": user_id})
        if not record:
            return None

        d_doc = record.get("disease", {})
        y_doc = record.get("yield", record.get("yield_data", {}))
        f_doc = record.get("fertilizer", {})
        w_doc = record.get("weather", {})
        m_doc = record.get("mandi")
        t_doc = record.get("system_telemetry", {})

        # Rehydrate disease treatments if document was created in legacy format
        class_idx = d_doc.get("class_index", record.get("disease_class_idx", 0))
        disease_info = DiseaseService.get_by_index(class_idx)

        disease_detail = {
            "class_index": class_idx,
            "name": d_doc.get("name", record.get("disease_name", "")),
            "crop": d_doc.get("crop", record.get("crop_type", "").title()),
            "is_healthy": d_doc.get("is_healthy", record.get("is_healthy", False)),
            "severity": d_doc.get("severity", record.get("severity", "None")),
            "description": d_doc.get("description") or (disease_info.description if disease_info else ""),
            "chemical_treatment": d_doc.get("chemical_treatment") or (disease_info.chemical_treatment if disease_info else []),
            "organic_treatment": d_doc.get("organic_treatment") or (disease_info.organic_treatment if disease_info else []),
            "confidence": d_doc.get("confidence", record.get("confidence", 0.0)),
        }

        # Rehydrate fertilizer details if not present
        if not f_doc or "mode" not in f_doc:
            soil_data = record.get("soil", {})
            f_doc = FertilizerService.calculate(
                record.get("crop_type", "tomato"),
                soil_data.get("N", record.get("soil_N")),
                soil_data.get("P", record.get("soil_P")),
                soil_data.get("K", record.get("soil_K")),
            )

        created_at = record.get("created_at")
        created_iso = created_at.isoformat() if isinstance(created_at, datetime) else created_at

        return {
            "id": record.get("id"),
            "plot_id": record.get("plot_id"),
            "plot_name": record.get("plot_name"),
            "crop": record.get("crop_type", "").title(),
            "district": record.get("district", "").title(),
            "image_url": record.get("image_url"),
            "disease": disease_detail,
            "yield_t_ha": y_doc.get("predicted_yield_t_ha", record.get("predicted_yield_t_ha", 0.0)),
            "yield": y_doc,
            "fertilizer": f_doc,
            "weather": w_doc or {
                "temperature": record.get("weather_temp", 0.0),
                "humidity": record.get("weather_hum", 0.0),
                "rainfall": record.get("weather_rain", 0.0),
                "source": "Recorded Telemetry",
            },
            "mandi": m_doc,
            "low_confidence": t_doc.get("low_confidence", record.get("low_confidence", False)),
            "mock_mode": t_doc.get("mock_mode", record.get("mock_mode", False)),
            "created_at": created_iso,
        }

    @staticmethod
    async def delete_diagnosis(
        db: AsyncIOMotorDatabase,
        record_id: int,
        user_id: int,
    ) -> bool:
        """Delete a single diagnosis history record and clean up image file if present."""
        record = await db.analyses.find_one({"id": record_id, "user_id": user_id})
        if not record:
            return False

        image_filename = record.get("image_filename")
        if image_filename:
            storage = get_storage_provider()
            await storage.delete_image(user_id, image_filename)

        await db.analyses.delete_one({"id": record_id, "user_id": user_id})
        logger.info("[HistoryService] Deleted analysis record #%d for user %d", record_id, user_id)
        return True

    @staticmethod
    async def get_farmer_analytics(
        db: AsyncIOMotorDatabase,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Calculate aggregate summary metrics for farmer's dashboard using MongoDB aggregations:
        - Total plots & acreage
        - Total diagnostics performed
        - Overall crop health rate (% healthy)
        - Top diagnosed diseases
        - Average predicted yield
        """
        # 1. Plots summary aggregation
        plot_agg = await db.farm_plots.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_plots": {"$sum": 1},
                "total_acres": {"$sum": "$area_acres"},
            }},
        ]).to_list(1)

        total_plots = plot_agg[0]["total_plots"] if plot_agg else 0
        total_acres = round(plot_agg[0]["total_acres"] if plot_agg else 0.0, 1)

        # 2. Diagnoses summary aggregation
        diag_agg = await db.analyses.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_diags": {"$sum": 1},
                "total_healthy": {
                    "$sum": {
                        "$cond": [
                            {"$ifNull": ["$disease.is_healthy", {"$ifNull": ["$is_healthy", False]}]},
                            1,
                            0,
                        ]
                    }
                },
                "avg_yield": {
                    "$avg": {
                        "$ifNull": ["$yield.predicted_yield_t_ha", "$predicted_yield_t_ha"]
                    }
                },
            }},
        ]).to_list(1)

        total_diags = diag_agg[0]["total_diags"] if diag_agg else 0
        total_healthy = diag_agg[0]["total_healthy"] if diag_agg else 0
        avg_yield = round(diag_agg[0]["avg_yield"] or 0.0, 2) if diag_agg else 0.0
        health_rate = round((total_healthy / total_diags) * 100, 1) if total_diags > 0 else 100.0

        # 3. Top diagnosed diseases
        top_diseases_agg = await db.analyses.aggregate([
            {"$match": {
                "user_id": user_id,
                "$or": [
                    {"disease.is_healthy": False},
                    {"is_healthy": False},
                ],
            }},
            {"$group": {
                "_id": {
                    "$ifNull": ["$disease.name", "$disease_name"]
                },
                "count": {"$sum": 1},
            }},
            {"$sort": {"count": -1}},
            {"$limit": 3},
        ]).to_list(3)

        top_diseases = [{"name": item["_id"] or "Unknown Disease", "count": item["count"]} for item in top_diseases_agg]

        return {
            "total_plots": total_plots,
            "total_acres": total_acres,
            "total_diagnoses": total_diags,
            "health_rate_percent": health_rate,
            "avg_yield_t_ha": avg_yield,
            "top_diseases": top_diseases,
        }

    @staticmethod
    async def get_crop_progress_for_user(
        db: AsyncIOMotorDatabase,
        user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Calculates longitudinal crop health, disease evolution, and yield trajectory
        across consecutive analyses for each of the farmer's plots and crops in MongoDB.
        """
        plots_cursor = db.farm_plots.find({"user_id": user_id}).sort("id", -1)
        plots = await plots_cursor.to_list(length=500)

        output: List[Dict[str, Any]] = []
        covered_diag_ids = set()

        for p in plots:
            p_id = p.get("id")
            crop_type = p.get("crop_type", "").lower()

            diag_query = {
                "user_id": user_id,
                "$or": [
                    {"plot_id": p_id},
                    {"plot_id": None, "crop_type": crop_type},
                ],
            }
            diags_cursor = db.analyses.find(diag_query).sort("created_at", 1)
            diags = await diags_cursor.to_list(length=500)

            analyses_list = []
            for idx, d in enumerate(diags):
                covered_diag_ids.add(d.get("id"))
                d_doc = d.get("disease", {})
                y_doc = d.get("yield", d.get("yield_data", {}))
                f_doc = d.get("fertilizer", {})
                w_doc = d.get("weather", {})

                created_at = d.get("created_at")
                if isinstance(created_at, datetime):
                    created_iso = created_at.isoformat()
                    date_display = created_at.strftime("%d %b %Y, %I:%M %p")
                elif isinstance(created_at, str):
                    created_iso = created_at
                    date_display = created_at[:16]
                else:
                    created_iso = None
                    date_display = "--"

                fertilizers = f_doc.get("fertilizers", {})

                analyses_list.append({
                    "id": d.get("id"),
                    "analysis_number": idx + 1,
                    "created_at": created_iso,
                    "date_display": date_display,
                    "disease_name": d_doc.get("name", d.get("disease_name", "")),
                    "severity": d_doc.get("severity", d.get("severity", "None")),
                    "is_healthy": bool(d_doc.get("is_healthy", d.get("is_healthy", False))),
                    "confidence": round(float(d_doc.get("confidence", d.get("confidence", 0.0))), 1),
                    "predicted_yield_t_ha": round(float(y_doc.get("predicted_yield_t_ha", d.get("predicted_yield_t_ha", 0.0))), 2),
                    "image_url": d.get("image_url"),
                    "weather_temp": w_doc.get("temperature", d.get("weather_temp")),
                    "weather_hum": w_doc.get("humidity", d.get("weather_hum")),
                    "weather_rain": w_doc.get("rainfall", d.get("weather_rain")),
                    "fertilizers": {
                        "urea_kg": fertilizers.get("Urea", d.get("fertilizer_urea_kg")),
                        "dap_kg": fertilizers.get("DAP", d.get("fertilizer_dap_kg")),
                        "mop_kg": fertilizers.get("MOP", d.get("fertilizer_mop_kg")),
                    },
                })

            total_an = len(analyses_list)
            if total_an > 0:
                first_diag = analyses_list[0]
                latest_diag = analyses_list[-1]

                if latest_diag["is_healthy"]:
                    health_score = 100
                elif latest_diag["severity"] == "Low":
                    health_score = 75
                elif latest_diag["severity"] == "Moderate":
                    health_score = 50
                elif latest_diag["severity"] == "High":
                    health_score = 25
                else:
                    health_score = 10

                if total_an == 1:
                    trend = "baseline"
                    status_text = "Baseline Recorded"
                elif latest_diag["is_healthy"] and not first_diag["is_healthy"]:
                    trend = "recovered"
                    status_text = "Fully Recovered"
                elif (
                    (latest_diag["severity"] in ("Low", "None") and first_diag["severity"] in ("High", "Critical", "Moderate"))
                    or (latest_diag["predicted_yield_t_ha"] > first_diag["predicted_yield_t_ha"])
                ):
                    trend = "improving"
                    status_text = "Health Improving"
                elif latest_diag["severity"] in ("High", "Critical") and first_diag["severity"] in ("Low", "None"):
                    trend = "deteriorating"
                    status_text = "Action Needed"
                else:
                    trend = "stable"
                    status_text = "Monitoring Stable"
            else:
                health_score = 100
                trend = "no_analyses"
                status_text = "Awaiting First Analysis"
                latest_diag = None

            sowing = p.get("sowing_date")
            sowing_iso = sowing.isoformat() if isinstance(sowing, (date, datetime)) else sowing

            output.append({
                "plot_id": p.get("id"),
                "plot_name": p.get("plot_name"),
                "crop_type": p.get("crop_type"),
                "area_acres": p.get("area_acres"),
                "soil_type": p.get("soil_type"),
                "sowing_date": sowing_iso,
                "total_analyses": total_an,
                "health_score": health_score,
                "trend": trend,
                "status_text": status_text,
                "latest_analysis": latest_diag,
                "analyses": analyses_list,
            })

        # 2. Check for any unassigned diagnoses not tied to a registered plot
        unassigned_query = {"user_id": user_id}
        if covered_diag_ids:
            unassigned_query["id"] = {"$nin": list(covered_diag_ids)}

        unassigned_cursor = db.analyses.find(unassigned_query).sort("created_at", 1)
        unassigned_diags = await unassigned_cursor.to_list(length=500)

        if unassigned_diags:
            from collections import defaultdict
            by_crop = defaultdict(list)
            for d in unassigned_diags:
                by_crop[d.get("crop_type", "crop").lower()].append(d)

            for crop_key, diags in by_crop.items():
                analyses_list = []
                for idx, d in enumerate(diags):
                    d_doc = d.get("disease", {})
                    y_doc = d.get("yield", d.get("yield_data", {}))
                    f_doc = d.get("fertilizer", {})
                    w_doc = d.get("weather", {})

                    created_at = d.get("created_at")
                    if isinstance(created_at, datetime):
                        created_iso = created_at.isoformat()
                        date_display = created_at.strftime("%d %b %Y, %I:%M %p")
                    elif isinstance(created_at, str):
                        created_iso = created_at
                        date_display = created_at[:16]
                    else:
                        created_iso = None
                        date_display = "--"

                    fertilizers = f_doc.get("fertilizers", {})

                    analyses_list.append({
                        "id": d.get("id"),
                        "analysis_number": idx + 1,
                        "created_at": created_iso,
                        "date_display": date_display,
                        "disease_name": d_doc.get("name", d.get("disease_name", "")),
                        "severity": d_doc.get("severity", d.get("severity", "None")),
                        "is_healthy": bool(d_doc.get("is_healthy", d.get("is_healthy", False))),
                        "confidence": round(float(d_doc.get("confidence", d.get("confidence", 0.0))), 1),
                        "predicted_yield_t_ha": round(float(y_doc.get("predicted_yield_t_ha", d.get("predicted_yield_t_ha", 0.0))), 2),
                        "image_url": d.get("image_url"),
                        "weather_temp": w_doc.get("temperature", d.get("weather_temp")),
                        "weather_hum": w_doc.get("humidity", d.get("weather_hum")),
                        "weather_rain": w_doc.get("rainfall", d.get("weather_rain")),
                        "fertilizers": {
                            "urea_kg": fertilizers.get("Urea", d.get("fertilizer_urea_kg")),
                            "dap_kg": fertilizers.get("DAP", d.get("fertilizer_dap_kg")),
                            "mop_kg": fertilizers.get("MOP", d.get("fertilizer_mop_kg")),
                        },
                    })

                latest_diag = analyses_list[-1]
                first_diag = analyses_list[0]
                if latest_diag["is_healthy"]:
                    health_score = 100
                elif latest_diag["severity"] == "Low":
                    health_score = 75
                elif latest_diag["severity"] == "Moderate":
                    health_score = 50
                elif latest_diag["severity"] == "High":
                    health_score = 25
                else:
                    health_score = 10

                output.append({
                    "plot_id": None,
                    "plot_name": f"{crop_key.title()} (Unassigned Plot)",
                    "crop_type": crop_key,
                    "area_acres": 1.0,
                    "soil_type": "Medium Black",
                    "sowing_date": None,
                    "total_analyses": len(analyses_list),
                    "health_score": health_score,
                    "trend": "improving" if latest_diag["is_healthy"] and not first_diag["is_healthy"] else "stable",
                    "status_text": "Active Field",
                    "latest_analysis": latest_diag,
                    "analyses": analyses_list,
                })

        return output
