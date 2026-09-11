"""
tests/test_plots.py — Unit and integration tests for Multi-Crop & Farm Plot Management
"""

import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestPlotManagement:
    @pytest.fixture(scope="class")
    def farmer_a_token(self):
        uid = uuid.uuid4().hex[:8]
        res = client.post(
            "/api/auth/register",
            json={
                "full_name": f"Farmer A {uid}",
                "phone_number": f"981{uid[:7]}",
                "password": "Password123",
                "district": "jalgaon",
            },
        )
        assert res.status_code == 200, f"Registration failed: {res.text}"
        return res.json()["access_token"]

    @pytest.fixture(scope="class")
    def farmer_b_token(self):
        uid = uuid.uuid4().hex[:8]
        res = client.post(
            "/api/auth/register",
            json={
                "full_name": f"Farmer B {uid}",
                "phone_number": f"982{uid[:7]}",
                "password": "Password123",
                "district": "amravati",
            },
        )
        assert res.status_code == 200, f"Registration failed: {res.text}"
        return res.json()["access_token"]

    def test_unauthorized_access_rejected(self):
        res = client.get("/api/farmer/plots")
        assert res.status_code == 401

    def test_create_multiple_plots_farmer_a(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        
        # Plot 1: Cotton
        p1 = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={
                "plot_name": "East Field",
                "crop_type": "cotton",
                "area_acres": 4.5,
                "soil_type": "Deep Black",
                "baseline_N": 60,
                "baseline_P": 30,
                "baseline_K": 30,
            },
        )
        assert p1.status_code == 201
        assert p1.json()["plot"]["plot_name"] == "East Field"
        assert p1.json()["plot"]["crop_type"] == "cotton"

        # Plot 2: Tomato
        p2 = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={
                "plot_name": "Canal Garden",
                "crop_type": "tomato",
                "area_acres": 2.0,
                "soil_type": "Alluvial",
            },
        )
        assert p2.status_code == 201
        assert p2.json()["plot"]["crop_type"] == "tomato"

    def test_list_plots_farmer_a(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        res = client.get("/api/farmer/plots", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 2
        crops = [p["crop_type"] for p in data["plots"]]
        assert "cotton" in crops
        assert "tomato" in crops

    def test_create_plot_invalid_crop_rejected(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        res = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={"plot_name": "Exotic Plot", "crop_type": "dragon_fruit", "area_acres": 1.0},
        )
        assert res.status_code == 400
        assert "not supported" in res.json()["detail"]

    def test_update_plot(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        plots = client.get("/api/farmer/plots", headers=headers).json()["plots"]
        target_id = plots[0]["id"]

        res = client.put(
            f"/api/farmer/plots/{target_id}",
            headers=headers,
            json={"plot_name": "East Field - Irrigated", "area_acres": 5.0},
        )
        assert res.status_code == 200
        assert res.json()["plot"]["plot_name"] == "East Field - Irrigated"
        assert res.json()["plot"]["area_acres"] == 5.0

    def test_plot_isolation_between_farmers(self, farmer_a_token, farmer_b_token):
        headers_a = {"Authorization": f"Bearer {farmer_a_token}"}
        headers_b = {"Authorization": f"Bearer {farmer_b_token}"}

        plots_a = client.get("/api/farmer/plots", headers=headers_a).json()["plots"]
        plot_a_id = plots_a[0]["id"]

        res_get = client.get(f"/api/farmer/plots/{plot_a_id}", headers=headers_b)
        assert res_get.status_code == 404

        res_del = client.delete(f"/api/farmer/plots/{plot_a_id}", headers=headers_b)
        assert res_del.status_code == 404

    def test_delete_plot(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        temp = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={"plot_name": "Temporary Plot", "crop_type": "wheat", "area_acres": 1.0},
        ).json()["plot"]

        del_res = client.delete(f"/api/farmer/plots/{temp['id']}", headers=headers)
        assert del_res.status_code == 200

        get_res = client.get(f"/api/farmer/plots/{temp['id']}", headers=headers)
        assert get_res.status_code == 404

    def test_predict_plot_authorization_isolation(self, farmer_a_token, farmer_b_token):
        from io import BytesIO
        from PIL import Image

        img = Image.new("RGB", (224, 224), color=(85, 170, 34))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        jpeg_bytes = buf.getvalue()

        headers_a = {"Authorization": f"Bearer {farmer_a_token}"}
        headers_b = {"Authorization": f"Bearer {farmer_b_token}"}

        # Farmer A creates a plot
        plot_a = client.post(
            "/api/farmer/plots",
            headers=headers_a,
            json={"plot_name": "Farmer A Secret Plot", "crop_type": "cotton", "area_acres": 2.0},
        ).json()["plot"]

        # Farmer B runs a prediction trying to link to Farmer A's plot
        pred_res = client.post(
            "/api/predict",
            headers=headers_b,
            data={"crop": "cotton", "district": "pune", "N": "60", "P": "30", "K": "30", "plot_id": plot_a["id"]},
            files={"image": ("leaf.jpg", jpeg_bytes, "image/jpeg")},
        )
        assert pred_res.status_code == 200
        # The returned plot_id should be None because Farmer B does not own plot_a
        assert pred_res.json()["plot_id"] is None

        # Farmer A's plot should have 0 diagnoses from Farmer B
        plot_a_check = client.get(f"/api/farmer/plots/{plot_a['id']}", headers=headers_a).json()
        plots_list_a = client.get("/api/farmer/plots", headers=headers_a).json()["plots"]
        target = next(p for p in plots_list_a if p["id"] == plot_a["id"])
        assert target["total_diagnoses"] == 0

    def test_create_and_update_plot_with_sowing_date_string(self, farmer_a_token):
        headers = {"Authorization": f"Bearer {farmer_a_token}"}
        res = client.post(
            "/api/farmer/plots",
            headers=headers,
            json={
                "plot_name": "Sowing Date Test Field",
                "crop_type": "sugarcane",
                "area_acres": 3.0,
                "sowing_date": "2026-02-15",
                "soil_type": "Medium Black",
            },
        )
        assert res.status_code == 201, f"Failed: {res.text}"
        data = res.json()["plot"]
        assert data["sowing_date"] == "2026-02-15"

        # Test GET single plot with sowing_date
        get_res = client.get(f"/api/farmer/plots/{data['id']}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["sowing_date"] == "2026-02-15"

        # Test PUT single plot with sowing_date
        put_res = client.put(
            f"/api/farmer/plots/{data['id']}",
            headers=headers,
            json={"sowing_date": "2026-03-01"},
        )
        assert put_res.status_code == 200
        assert put_res.json()["plot"]["sowing_date"] == "2026-03-01"


