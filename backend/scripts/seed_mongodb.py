"""
AeroCrop.ai — MongoDB Clean Database Seeder (Option B)

Seeds the MongoDB database with:
  1. A comprehensive demonstration farmer profile:
     - Phone: 9876543210
     - Email: farmer@aerocrop.ai
     - Password: password123
  2. Three diverse agricultural plots (Cotton, Tomato, Wheat).
  3. Six full-fidelity multi-modal analyses containing ALL analysis data:
     - Disease taxonomy & complete organic/chemical treatments
     - Soil NPK deficiency baselines
     - Commercial fertilizer bag requirements & costs
     - Weather telemetry & spray window safety intelligence
     - Mandi market rates & revenue projections
     - System telemetry & ensemble arbitration logs

Run with:
    python backend/scripts/seed_mongodb.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure project root & backend are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import config
from services.disease_service import DiseaseService
from services.fertilizer_service import FertilizerService
from services.mandi_service import MandiService


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8")[:72], bcrypt.gensalt(12)).decode("utf-8")


async def seed():
    client = AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.MONGODB_DB_NAME]

    print(f"[MongoDB] Connecting to: {config.MONGODB_URL} (db: {config.MONGODB_DB_NAME})")

    # 1. Clear existing test collections
    await db.users.drop()
    await db.farm_plots.drop()
    await db.analyses.drop()
    await db.counters.drop()
    print("[MongoDB] Cleared collections: users, farm_plots, analyses, counters.")

    # 2. Initialize sequence counters
    await db.counters.insert_many([
        {"_id": "user_id", "seq": 1},
        {"_id": "plot_id", "seq": 3},
        {"_id": "analysis_id", "seq": 6},
    ])

    now = datetime.now(timezone.utc)

    # 3. Create demo farmer account
    demo_user = {
        "id": 1,
        "full_name": "Devanshu Patil (Demo Farmer)",
        "phone_number": "9876543210",
        "email": "farmer@aerocrop.ai",
        "hashed_password": hash_pw("password123"),
        "district": "pune",
        "taluka_village": "Baramati",
        "preferred_language": "en",
        "token_version": 1,
        "is_active": True,
        "created_at": now - timedelta(days=60),
        "updated_at": now,
    }
    await db.users.insert_one(demo_user)
    print("[MongoDB] Seeded Demo User: 9876543210 / farmer@aerocrop.ai (password: password123)")

    # 4. Create 3 diverse farm plots
    plots = [
        {
            "id": 1,
            "user_id": 1,
            "plot_name": "North Field",
            "crop_type": "cotton",
            "area_acres": 4.5,
            "sowing_date": (now - timedelta(days=50)).strftime("%Y-%m-%d"),
            "soil_type": "Medium Black",
            "baseline_N": 60.0,
            "baseline_P": 30.0,
            "baseline_K": 30.0,
            "notes": "Drip-irrigated Bt Cotton block, black cotton soil.",
            "created_at": now - timedelta(days=50),
        },
        {
            "id": 2,
            "user_id": 1,
            "plot_name": "Riverside Garden",
            "crop_type": "tomato",
            "area_acres": 2.0,
            "sowing_date": (now - timedelta(days=35)).strftime("%Y-%m-%d"),
            "soil_type": "Red Sandy Loam",
            "baseline_N": 50.0,
            "baseline_P": 25.0,
            "baseline_K": 25.0,
            "notes": "Staked tomato plot, fertigation line active.",
            "created_at": now - timedelta(days=35),
        },
        {
            "id": 3,
            "user_id": 1,
            "plot_name": "Hillside Block",
            "crop_type": "wheat",
            "area_acres": 3.0,
            "sowing_date": (now - timedelta(days=20)).strftime("%Y-%m-%d"),
            "soil_type": "Black Loam",
            "baseline_N": 55.0,
            "baseline_P": 25.0,
            "baseline_K": 20.0,
            "notes": "Lokwan wheat trial, sprinkler irrigation.",
            "created_at": now - timedelta(days=20),
        },
    ]
    await db.farm_plots.insert_many(plots)
    print("[MongoDB] Seeded 3 Farm Plots: North Field (Cotton), Riverside Garden (Tomato), Hillside Block (Wheat)")

    # 5. Create 6 rich multi-modal analyses with ALL info stored
    # Helper to construct full analysis document
    def build_analysis_doc(
        analysis_id: int,
        plot: dict,
        days_ago: int,
        disease_idx: int,
        confidence: float,
        yield_val: float,
        soil_npk: tuple,
        weather_tuple: tuple,
        spray_safe: bool,
    ):
        d_info = DiseaseService.get_by_index(disease_idx)
        fert = FertilizerService.calculate(
            crop=plot["crop_type"],
            soil_N=soil_npk[0],
            soil_P=soil_npk[1],
            soil_K=soil_npk[2],
        )
        mandi = MandiService.get_market_rate(
            district="pune",
            crop=plot["crop_type"],
            yield_t_ha=yield_val,
        )

        analysis_time = now - timedelta(days=days_ago)

        return {
            "id": analysis_id,
            "user_id": 1,
            "plot_id": plot["id"],
            "plot_name": plot["plot_name"],
            "crop_type": plot["crop_type"],
            "district": "Pune",
            "image_filename": f"sample_leaf_{analysis_id}.jpg",
            "image_url": f"/uploads/sample_leaf_{analysis_id}.jpg",
            "disease": {
                "class_index": disease_idx,
                "name": d_info.name if d_info else f"Class {disease_idx}",
                "crop": plot["crop_type"].title(),
                "confidence": confidence,
                "severity": d_info.severity if d_info else "None",
                "is_healthy": d_info.is_healthy if d_info else False,
                "description": d_info.description if d_info else "",
                "chemical_treatment": d_info.chemical_treatment if d_info else [],
                "organic_treatment": d_info.organic_treatment if d_info else [],
                "probabilities": [0.01] * 50,
            },
            "yield": {
                "predicted_yield_t_ha": round(yield_val, 2),
                "quintals_per_ha": round(yield_val * 10.0, 2),
                "quintals_per_acre": round(yield_val * 4.047, 2),
            },
            "soil": {
                "N": soil_npk[0],
                "P": soil_npk[1],
                "K": soil_npk[2],
                "tested": True,
            },
            "fertilizer": fert,
            "weather": {
                "temperature": weather_tuple[0],
                "humidity": weather_tuple[1],
                "rainfall": weather_tuple[2],
                "wind_speed": 11.2,
                "spray_window": {
                    "safe": spray_safe,
                    "status": "success" if spray_safe else "warning",
                    "badge": "Safe to Spray" if spray_safe else "Delay Spraying",
                    "reason": "Optimal wind and no rain forecast." if spray_safe else "High humidity and rain risk.",
                    "reason_mr": "फवारणीसाठी अनुकूल हवामान." if spray_safe else "फवारणी पुढे ढकलावी.",
                    "reason_hi": "छिड़काव के लिए अनुकूल मौसम।" if spray_safe else "छिड़काव स्थगित करें।",
                },
                "source": "live",
            },
            "mandi": mandi,
            "system_telemetry": {
                "mock_mode": False,
                "low_confidence": False,
                "out_of_distribution": False,
                "ood_reason": "",
                "ensemble_verified": True,
                "model_weights": "aerocrop_weights_full_v3.pth",
            },
            "created_at": analysis_time,
            "updated_at": analysis_time,
        }

    analyses = [
        # Plot 1 (Cotton) — Evolution: Critical Bacterial Blight -> Moderate -> Healthy
        build_analysis_doc(
            analysis_id=1,
            plot=plots[0],
            days_ago=40,
            disease_idx=8,  # Cotton Bacterial Blight
            confidence=95.4,
            yield_val=1.85,
            soil_npk=(50.0, 25.0, 30.0),
            weather_tuple=(29.5, 72.0, 2.5),
            spray_safe=False,
        ),
        build_analysis_doc(
            analysis_id=2,
            plot=plots[0],
            days_ago=22,
            disease_idx=8,  # Cotton Bacterial Blight (improving)
            confidence=88.2,
            yield_val=2.10,
            soil_npk=(75.0, 38.0, 42.0),
            weather_tuple=(28.0, 64.0, 0.2),
            spray_safe=True,
        ),
        build_analysis_doc(
            analysis_id=3,
            plot=plots[0],
            days_ago=5,
            disease_idx=9,  # Cotton Healthy
            confidence=98.1,
            yield_val=2.65,
            soil_npk=(105.0, 52.0, 55.0),
            weather_tuple=(27.5, 58.0, 0.0),
            spray_safe=True,
        ),
        # Plot 2 (Tomato) — Evolution: Early Blight -> Healthy
        build_analysis_doc(
            analysis_id=4,
            plot=plots[1],
            days_ago=25,
            disease_idx=26,  # Tomato Early Blight
            confidence=94.8,
            yield_val=22.4,
            soil_npk=(60.0, 40.0, 40.0),
            weather_tuple=(26.2, 78.0, 4.0),
            spray_safe=False,
        ),
        build_analysis_doc(
            analysis_id=5,
            plot=plots[1],
            days_ago=8,
            disease_idx=34,  # Tomato Healthy
            confidence=97.0,
            yield_val=28.5,
            soil_npk=(110.0, 70.0, 75.0),
            weather_tuple=(25.0, 60.0, 0.0),
            spray_safe=True,
        ),
        # Plot 3 (Wheat) — Baseline Healthy
        build_analysis_doc(
            analysis_id=6,
            plot=plots[2],
            days_ago=3,
            disease_idx=49,  # Wheat Healthy
            confidence=96.5,
            yield_val=3.80,
            soil_npk=(65.0, 30.0, 25.0),
            weather_tuple=(24.5, 52.0, 0.0),
            spray_safe=True,
        ),
    ]

    await db.analyses.insert_many(analyses)
    print("[MongoDB] Seeded 6 Full-Fidelity Multi-Modal Analyses across 3 plots.")

    # 6. Re-ensure indexes
    await db.users.create_index([("id", 1)], unique=True)
    await db.users.create_index(
        [("phone_number", 1)],
        unique=True,
        partialFilterExpression={"phone_number": {"$type": "string"}},
    )
    await db.users.create_index(
        [("email", 1)],
        unique=True,
        partialFilterExpression={"email": {"$type": "string"}},
    )
    await db.farm_plots.create_index([("id", 1)], unique=True)
    await db.farm_plots.create_index([("user_id", 1), ("id", -1)])
    await db.analyses.create_index([("id", 1)], unique=True)
    await db.analyses.create_index([("user_id", 1), ("created_at", -1)])
    await db.analyses.create_index([("plot_id", 1)])

    print("\n[SUCCESS] MongoDB clean database seeded and ready!")
    print("=" * 60)
    print("Farmer Login Credentials:")
    print("  Phone    : 9876543210")
    print("  Email    : farmer@aerocrop.ai")
    print("  Password : password123")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
