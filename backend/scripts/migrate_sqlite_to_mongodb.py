"""
AeroCrop.ai — SQLite to MongoDB Data Migration & Analysis Enrichment Utility

Extracts existing records from SQLite (`data/aerocrop.db`) and migrates them
into MongoDB collections (`users`, `farm_plots`, `analyses`), enriching historical
diagnoses with full treatment recommendations and fertilizer calculations.

Run with:
    python backend/scripts/migrate_sqlite_to_mongodb.py
"""

import asyncio
import os
import sqlite3
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from motor.motor_asyncio import AsyncIOMotorClient
import config
from services.disease_service import DiseaseService
from services.fertilizer_service import FertilizerService
from services.mandi_service import MandiService


async def migrate():
    sqlite_db_path = config.DEFAULT_DB_PATH
    if not os.path.exists(sqlite_db_path):
        print(f"[Error] SQLite database not found at {sqlite_db_path}")
        return

    print(f"[SQLite] Reading database: {sqlite_db_path}")
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    client = AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.MONGODB_DB_NAME]

    # 1. Migrate Users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    user_docs = []
    max_user_id = 0
    for u in users:
        u_dict = dict(u)
        uid = u_dict["id"]
        if uid > max_user_id:
            max_user_id = uid
        u_dict["is_active"] = bool(u_dict.get("is_active", 1))
        # Ensure dates are stored properly
        for date_key in ("created_at", "updated_at"):
            if u_dict.get(date_key) and isinstance(u_dict[date_key], str):
                try:
                    u_dict[date_key] = datetime.fromisoformat(u_dict[date_key])
                except Exception:
                    pass
        user_docs.append(u_dict)

    if user_docs:
        await db.users.delete_many({})
        await db.users.insert_many(user_docs)
        print(f"✅ Migrated {len(user_docs)} users.")

    # 2. Migrate Farm Plots
    cursor.execute("SELECT * FROM farm_plots")
    plots = cursor.fetchall()
    plot_docs = []
    max_plot_id = 0
    for p in plots:
        p_dict = dict(p)
        pid = p_dict["id"]
        if pid > max_plot_id:
            max_plot_id = pid
        if p_dict.get("created_at") and isinstance(p_dict["created_at"], str):
            try:
                p_dict["created_at"] = datetime.fromisoformat(p_dict["created_at"])
            except Exception:
                pass
        plot_docs.append(p_dict)

    if plot_docs:
        await db.farm_plots.delete_many({})
        await db.farm_plots.insert_many(plot_docs)
        print(f"✅ Migrated {len(plot_docs)} farm plots.")

    # 3. Migrate & Enrich Diagnosis Records to Full Analyses
    cursor.execute("SELECT * FROM diagnosis_records")
    diags = cursor.fetchall()
    analysis_docs = []
    max_analysis_id = 0
    for d in diags:
        d_dict = dict(d)
        aid = d_dict["id"]
        if aid > max_analysis_id:
            max_analysis_id = aid

        # Rehydrate enriched analysis payloads
        crop = d_dict.get("crop_type", "tomato").lower()
        class_idx = d_dict.get("disease_class_idx", 0)
        d_info = DiseaseService.get_by_index(class_idx)

        disease_doc = {
            "class_index": class_idx,
            "name": d_dict.get("disease_name") or (d_info.name if d_info else f"Class {class_idx}"),
            "crop": crop.title(),
            "confidence": float(d_dict.get("confidence", 0.0)),
            "severity": d_dict.get("severity") or (d_info.severity if d_info else "None"),
            "is_healthy": bool(d_dict.get("is_healthy", False)),
            "description": d_info.description if d_info else "",
            "chemical_treatment": d_info.chemical_treatment if d_info else [],
            "organic_treatment": d_info.organic_treatment if d_info else [],
            "probabilities": None,
        }

        yield_val = float(d_dict.get("predicted_yield_t_ha", 0.0))
        yield_doc = {
            "predicted_yield_t_ha": round(yield_val, 2),
            "quintals_per_ha": round(yield_val * 10.0, 2),
            "quintals_per_acre": round(yield_val * 4.047, 2),
        }

        soil_doc = {
            "N": d_dict.get("soil_N"),
            "P": d_dict.get("soil_P"),
            "K": d_dict.get("soil_K"),
            "tested": d_dict.get("soil_N") is not None,
        }

        fertilizer_doc = FertilizerService.calculate(
            crop=crop,
            soil_N=d_dict.get("soil_N"),
            soil_P=d_dict.get("soil_P"),
            soil_K=d_dict.get("soil_K"),
        )

        weather_doc = {
            "temperature": float(d_dict.get("weather_temp", 0.0)),
            "humidity": float(d_dict.get("weather_hum", 0.0)),
            "rainfall": float(d_dict.get("weather_rain", 0.0)),
            "wind_speed": 10.0,
            "spray_window": {
                "safe": True,
                "status": "success",
                "badge": "Historical",
                "reason": "Recorded historical analysis telemetry",
                "reason_mr": "ऐतिहासिक विश्लेषणाची नोंद",
                "reason_hi": "ऐतिहासिक विश्लेषण डेटा",
            },
            "source": "migrated",
        }

        created_dt = d_dict.get("created_at")
        if created_dt and isinstance(created_dt, str):
            try:
                created_dt = datetime.fromisoformat(created_dt)
            except Exception:
                created_dt = datetime.now(timezone.utc)

        full_analysis = {
            "id": aid,
            "user_id": d_dict.get("user_id"),
            "plot_id": d_dict.get("plot_id"),
            "crop_type": crop,
            "district": d_dict.get("district", "Pune").title(),
            "image_filename": d_dict.get("image_filename"),
            "image_url": d_dict.get("image_url"),
            "disease": disease_doc,
            "yield": yield_doc,
            "yield_data": yield_doc,
            "soil": soil_doc,
            "fertilizer": fertilizer_doc,
            "weather": weather_doc,
            "mandi": None,
            "system_telemetry": {
                "mock_mode": bool(d_dict.get("mock_mode", False)),
                "low_confidence": bool(d_dict.get("low_confidence", False)),
                "out_of_distribution": False,
                "ood_reason": "",
                "ensemble_verified": False,
                "model_weights": config.DEFAULT_WEIGHTS_FILE,
            },
            "created_at": created_dt,
            "updated_at": created_dt,
        }
        analysis_docs.append(full_analysis)

    if analysis_docs:
        await db.analyses.delete_many({})
        await db.analyses.insert_many(analysis_docs)
        print(f"[MongoDB] Migrated & enriched {len(analysis_docs)} analyses.")

    # 4. Update sequence counters to max + 1
    await db.counters.delete_many({})
    await db.counters.insert_many([
        {"_id": "user_id", "seq": max_user_id},
        {"_id": "plot_id", "seq": max_plot_id},
        {"_id": "analysis_id", "seq": max_analysis_id},
    ])
    print(f"[MongoDB] Sequence counters set: user_id={max_user_id}, plot_id={max_plot_id}, analysis_id={max_analysis_id}")

    client.close()
    conn.close()
    print("[SUCCESS] Migration complete successfully!")


if __name__ == "__main__":
    asyncio.run(migrate())
