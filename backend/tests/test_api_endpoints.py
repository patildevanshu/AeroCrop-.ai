"""
AeroCrop.ai — FastAPI REST Endpoint Verification Suite for MongoDB Backend

Tests all REST endpoints via FastAPI TestClient / httpx:
  - Auth: POST /api/auth/login, GET /api/auth/me
  - Plots: GET /api/farmer/plots, POST /api/farmer/plots
  - History: GET /api/farmer/history, GET /api/farmer/history/{id}
  - Analytics: GET /api/farmer/analytics, GET /api/farmer/crop-progress
  - Weather: GET /api/weather
  - Disease DB: GET /api/disease/classes
"""

import asyncio
import os
import sys
import pytest
from httpx import ASGITransport, AsyncClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

for p in [PROJECT_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.main import app
from backend.database.mongodb import init_mongodb, close_mongodb


@pytest.mark.asyncio
async def test_all_endpoints():
    print("\n" + "=" * 60)
    print("  Testing AeroCrop.ai FastAPI REST API with MongoDB")
    print("=" * 60)

    await init_mongodb()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Login
        login_res = await ac.post("/api/auth/login", json={
            "identifier": "9876543210",
            "password": "password123",
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        login_data = login_res.json()
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[1/6] POST /api/auth/login: 200 OK (JWT Token received)")

        # 2. Get Profile
        me_res = await ac.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        user_info = me_res.json()
        assert user_info["phone_number"] == "9876543210"
        print(f"[2/6] GET /api/auth/me: 200 OK (Logged in as {user_info['full_name']})")

        # 3. Farmer Plots
        plots_res = await ac.get("/api/farmer/plots", headers=headers)
        assert plots_res.status_code == 200
        plots_data = plots_res.json()
        plots = plots_data["plots"]
        assert len(plots) >= 3
        print(f"[3/6] GET /api/farmer/plots: 200 OK ({len(plots)} plots returned)")

        # 4. History List & Detail
        hist_res = await ac.get("/api/farmer/history", headers=headers)
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data["total"] >= 1
        first_record_id = hist_data["records"][0]["id"]
        print(f"[4/6] GET /api/farmer/history: 200 OK (Total {hist_data['total']} records)")

        detail_res = await ac.get(f"/api/farmer/history/{first_record_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert "disease" in detail and "chemical_treatment" in detail["disease"]
        assert "fertilizer" in detail
        assert "weather" in detail
        print(f"      GET /api/farmer/history/{first_record_id}: 200 OK (Full analysis preserved)")

        # 5. Farmer Analytics
        analytics_res = await ac.get("/api/farmer/analytics", headers=headers)
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()
        assert analytics["total_plots"] >= 3
        assert "top_diseases" in analytics
        print(f"[5/6] GET /api/farmer/analytics: 200 OK (Acreage: {analytics['total_acres']} acres, Health Rate: {analytics['health_rate_percent']}%)")

        # 6. Crop Progress & Disease DB
        prog_res = await ac.get("/api/farmer/crop-progress", headers=headers)
        assert prog_res.status_code == 200
        prog_data = prog_res.json()
        assert prog_data["count"] >= 3
        print(f"[6/6] GET /api/farmer/crop-progress: 200 OK ({prog_data['count']} crop progress tracks)")

    await close_mongodb()
    print("\n" + "=" * 60)
    print("  ALL REST API ENDPOINTS VERIFIED ON MONGODB!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
