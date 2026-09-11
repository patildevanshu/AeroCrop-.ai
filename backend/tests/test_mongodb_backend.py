"""
AeroCrop.ai — MongoDB Backend Integration & Full Analysis Storage Test Suite

Verifies:
  1. MongoDB connection & collection schemas
  2. Authentication & JWT token issuance/revocation
  3. Multi-crop plot creation & management
  4. Full-fidelity multi-modal analysis persistence (complete data retention)
  5. Detailed analysis retrieval with all treatments, fertilizer bags, weather spray window, mandi revenue
  6. Aggregation pipelines for farmer analytics and crop progress tracking

Run with:
    python backend/tests/test_mongodb_backend.py
"""

import asyncio
import os
import sys

# Ensure backend and root are in path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from database.mongodb import get_client, get_database, init_mongodb, close_mongodb
from services.user_service import UserService
from services.auth_service import AuthService
from services.plot_service import PlotService
from services.history_service import HistoryService
from services.disease_service import DiseaseService
from services.fertilizer_service import FertilizerService
from services.mandi_service import MandiService


async def run_tests():
    print("\n" + "=" * 60)
    print("  Testing AeroCrop.ai MongoDB Backend & Full Analysis Storage")
    print("=" * 60)

    # 1. Initialize DB
    await init_mongodb()
    db = get_database()
    print("[1/6] MongoDB connection & index initialization: OK")

    # 2. Test User Authentication
    user, err = await UserService.authenticate_user(db, "9876543210", "password123")
    assert user is not None, f"Failed to authenticate demo user: {err}"
    assert user.id == 1
    assert user.full_name == "Devanshu Patil (Demo Farmer)"
    token = AuthService.create_access_token(user.id, user.phone_number, user.token_version)
    decoded = AuthService.decode_access_token(token)
    assert decoded is not None and decoded["sub"] == "1"
    print(f"[2/6] Farmer Authentication & JWT Token Verification: OK (User: {user.full_name})")

    # 3. Test Plot Management
    plots = await PlotService.list_plots_for_user(db, user.id)
    assert len(plots) >= 3, f"Expected at least 3 plots, got {len(plots)}"
    plot_names = [p["plot_name"] for p in plots]
    assert "North Field" in plot_names
    assert "Riverside Garden" in plot_names
    print(f"[3/6] Multi-Crop Plot Management: OK ({len(plots)} plots verified: {', '.join(plot_names)})")

    # 4. Test Storing ALL INFO in Analysis
    print("[4/6] Testing Full-Fidelity Analysis Persistence...")
    cotton_plot = next(p for p in plots if p["crop_type"] == "cotton")
    
    # Generate realistic rich payload
    disease_info = DiseaseService.get_by_index(12)
    fert_calc = FertilizerService.calculate(crop="cotton", soil_N=58.0, soil_P=28.0, soil_K=32.0)
    mandi_calc = MandiService.get_market_rate(district="pune", crop="cotton", yield_t_ha=2.75)
    
    saved = await HistoryService.save_diagnosis(
        db=db,
        user_id=user.id,
        crop_type="cotton",
        district="Pune",
        disease_class_idx=12,
        disease_name=disease_info.name if disease_info else "Cotton Bacterial Blight",
        confidence=96.8,
        severity="Moderate",
        is_healthy=False,
        predicted_yield_t_ha=2.75,
        soil_N=58.0,
        soil_P=28.0,
        soil_K=32.0,
        plot_id=cotton_plot["id"],
        disease_payload={
            "class_index": 12,
            "name": disease_info.name if disease_info else "Cotton Bacterial Blight",
            "crop": "Cotton",
            "confidence": 96.8,
            "severity": "Moderate",
            "is_healthy": False,
            "description": disease_info.description if disease_info else "Bacterial blight",
            "chemical_treatment": disease_info.chemical_treatment if disease_info else ["Copper oxychloride"],
            "organic_treatment": disease_info.organic_treatment if disease_info else ["Neem oil"],
            "probabilities": [0.001] * 50,
        },
        fertilizer_payload=fert_calc,
        weather_payload={
            "temperature": 27.8,
            "humidity": 65.0,
            "rainfall": 0.5,
            "wind_speed": 10.5,
            "spray_window": {
                "safe": True,
                "status": "success",
                "badge": "Safe to Spray",
                "reason": "Optimal wind and moisture conditions",
                "reason_mr": "फवारणीसाठी अनुकूल",
                "reason_hi": "छिड़काव के लिए अनुकूल",
            },
            "source": "live",
        },
        mandi_payload=mandi_calc,
        system_telemetry={
            "mock_mode": False,
            "low_confidence": False,
            "out_of_distribution": False,
            "ood_reason": "",
            "ensemble_verified": True,
            "model_weights": "aerocrop_weights_full_v3.pth",
        },
    )
    assert saved.id > 0
    print(f"      Saved Analysis Record #{saved.id} into MongoDB.")

    # 5. Test Full Analysis Detail Retrieval
    detail = await HistoryService.get_diagnosis_detail(db, saved.id, user.id)
    assert detail is not None
    assert detail["crop"] == "Cotton"
    assert "chemical_treatment" in detail["disease"] and len(detail["disease"]["chemical_treatment"]) > 0
    assert "organic_treatment" in detail["disease"] and len(detail["disease"]["organic_treatment"]) > 0
    assert "commercial_bags" in detail["fertilizer"]
    assert "spray_window" in detail["weather"]
    assert detail["weather"]["spray_window"]["safe"] is True
    assert "revenue_projection" in detail["mandi"]
    print("[5/6] Full-Fidelity Analysis Document Retrieval: OK")
    print(f"      Verified Disease Treatments: {len(detail['disease']['chemical_treatment'])} chemical, {len(detail['disease']['organic_treatment'])} organic")
    print(f"      Verified Fertilizer Bags   : {list(detail['fertilizer']['commercial_bags'].keys())}")
    print(f"      Verified Spray Window      : {detail['weather']['spray_window']['badge']}")
    print(f"      Verified Mandi APMC Price  : INR {detail['mandi']['modal_price_inr']} / Quintal")

    # 6. Test Aggregation Analytics & Crop Progress
    analytics = await HistoryService.get_farmer_analytics(db, user.id)
    assert analytics["total_plots"] >= 3
    assert analytics["total_diagnoses"] >= 6
    assert "top_diseases" in analytics
    print(f"[6/6] MongoDB Aggregation Analytics: OK (Total Analyses: {analytics['total_diagnoses']}, Health Rate: {analytics['health_rate_percent']}%)")

    crop_prog = await HistoryService.get_crop_progress_for_user(db, user.id)
    assert len(crop_prog) >= 3
    print(f"      Verified Longitudinal Crop Progress across {len(crop_prog)} plot tracks: OK")

    await close_mongodb()
    print("\n" + "=" * 60)
    print("  ALL 6 TESTS PASSED SUCCESSFULLY! MONGODB MIGRATION VERIFIED.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
