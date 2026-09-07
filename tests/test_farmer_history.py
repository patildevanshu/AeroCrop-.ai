"""
tests/test_farmer_history.py — Unit and integration tests for Persistent Diagnosis History & Analytics
"""

import io
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def make_test_jpeg() -> bytes:
    img = Image.new("RGB", (224, 224), color=(60, 180, 75))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


JPEG_BYTES = make_test_jpeg()


class TestFarmerDiagnosisHistory:
    @pytest.fixture(scope="class")
    def farmer_session(self):
        uid = uuid.uuid4().hex[:8]
        res = client.post(
            "/api/auth/register",
            json={
                "full_name": f"Kailash Jadhav {uid}",
                "phone_number": f"983{uid[:7]}",
                "password": "Password123",
                "district": "aurangabad",
            },
        )
        assert res.status_code == 200, f"Registration failed: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a plot
        plot_res = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={"plot_name": "Main Orchard", "crop_type": "orange", "area_acres": 3.0},
        )
        assert plot_res.status_code == 201, f"Plot creation failed: {plot_res.text}"
        plot_id = plot_res.json()["plot"]["id"]

        return {"token": token, "headers": headers, "plot_id": plot_id}

    def test_guest_prediction_works_without_auth(self):
        """Guest user can perform diagnosis without token."""
        res = client.post(
            "/api/predict",
            data={"crop": "potato", "district": "pune", "N": "60", "P": "30", "K": "30"},
            files={"image": ("leaf.jpg", JPEG_BYTES, "image/jpeg")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["saved_record_id"] is None

    def test_authenticated_prediction_persists(self, farmer_session):
        headers = farmer_session["headers"]
        plot_id = farmer_session["plot_id"]

        res = client.post(
            "/api/predict",
            headers=headers,
            data={
                "crop": "orange",
                "district": "aurangabad",
                "N": "80",
                "P": "35",
                "K": "45",
                "plot_id": str(plot_id),
            },
            files={"image": ("orange_leaf.jpg", JPEG_BYTES, "image/jpeg")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["saved_record_id"] is not None
        assert data["image_url"] is not None
        assert "uploads/" in data["image_url"]

    def test_list_farmer_history(self, farmer_session):
        headers = farmer_session["headers"]
        res = client.get("/api/farmer/history", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["records"]) >= 1
        record = data["records"][0]
        assert record["crop_type"] == "orange"
        assert record["plot_name"] == "Main Orchard"

    def test_filter_history_by_crop(self, farmer_session):
        headers = farmer_session["headers"]
        res_match = client.get("/api/farmer/history?crop_type=orange", headers=headers)
        assert res_match.status_code == 200
        assert res_match.json()["total"] >= 1

        res_empty = client.get("/api/farmer/history?crop_type=wheat", headers=headers)
        assert res_empty.status_code == 200
        assert res_empty.json()["total"] == 0

    def test_get_diagnosis_detail(self, farmer_session):
        headers = farmer_session["headers"]
        history = client.get("/api/farmer/history", headers=headers).json()
        record_id = history["records"][0]["id"]

        res = client.get(f"/api/farmer/history/{record_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == record_id
        assert "disease" in data
        assert "fertilizer" in data
        assert "weather" in data
        assert "chemical_treatment" in data["disease"]
        assert "organic_treatment" in data["disease"]

    def test_farmer_analytics_endpoint(self, farmer_session):
        headers = farmer_session["headers"]
        res = client.get("/api/farmer/analytics", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_plots" in data
        assert data["total_plots"] >= 1
        assert "total_acres" in data
        assert data["total_acres"] >= 3.0
        assert "total_diagnoses" in data
        assert data["total_diagnoses"] >= 1
        assert "health_rate_percent" in data

    def test_delete_diagnosis_record(self, farmer_session):
        headers = farmer_session["headers"]
        pred = client.post(
            "/api/predict",
            headers=headers,
            data={"crop": "orange", "district": "aurangabad", "N": "80", "P": "35", "K": "45"},
            files={"image": ("temp.jpg", JPEG_BYTES, "image/jpeg")},
        ).json()
        rec_id = pred["saved_record_id"]

        del_res = client.delete(f"/api/farmer/history/{rec_id}", headers=headers)
        assert del_res.status_code == 200

        get_res = client.get(f"/api/farmer/history/{rec_id}", headers=headers)
        assert get_res.status_code == 404

    def test_authenticated_prediction_persists_without_npk_and_auto_links(self, farmer_session):
        """Test photo-only workflow (no NPK provided) persists and auto-links to plot."""
        headers = farmer_session["headers"]
        res = client.post(
            "/api/predict",
            headers=headers,
            data={
                "crop": "orange",
                "district": "aurangabad",
                # Omit N, P, K and omit plot_id
            },
            files={"image": ("orange_photo_only.jpg", JPEG_BYTES, "image/jpeg")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["saved_record_id"] is not None

        # Check detail confirms plot was auto-linked
        detail = client.get(f"/api/farmer/history/{data['saved_record_id']}", headers=headers).json()
        assert detail["plot_id"] == farmer_session["plot_id"]
        assert detail["plot_name"] == "Main Orchard"

    def test_crop_progress_endpoint(self, farmer_session):
        """Test GET /api/farmer/crop-progress returns longitudinal progression."""
        headers = farmer_session["headers"]
        res = client.get("/api/farmer/crop-progress", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "count" in data
        assert data["count"] >= 1
        assert "crops" in data
        crop_progress = next((c for c in data["crops"] if c["plot_id"] == farmer_session["plot_id"]), None)
        assert crop_progress is not None
        assert crop_progress["crop_type"] == "orange"
        assert crop_progress["plot_name"] == "Main Orchard"
        assert crop_progress["total_analyses"] >= 2
        assert "health_score" in crop_progress
        assert "trend" in crop_progress
        assert "analyses" in crop_progress
        assert len(crop_progress["analyses"]) >= 2
        first_an = crop_progress["analyses"][0]
        assert first_an["analysis_number"] == 1
        assert "disease_name" in first_an
        assert "predicted_yield_t_ha" in first_an
        assert "confidence" in first_an

    def test_plots_endpoint_includes_health_score_and_recent_analyses(self, farmer_session):
        """Test GET /api/farmer/plots includes health_score and recent_analyses."""
        headers = farmer_session["headers"]
        res = client.get("/api/farmer/plots", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "plots" in data
        plot = next((p for p in data["plots"] if p["id"] == farmer_session["plot_id"]), None)
        assert plot is not None
        assert "health_score" in plot
        assert "recent_analyses" in plot
        assert len(plot["recent_analyses"]) >= 2

