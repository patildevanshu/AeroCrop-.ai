"""
tests/test_api_endpoints.py — Integration tests for FastAPI endpoints

Uses FastAPI TestClient (httpx-based) to test all API routes:
  GET  /api/health
  GET  /api/weather/districts
  GET  /api/weather/{district}
  GET  /api/disease/classes
  POST /api/predict
  POST /api/model/reload
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Helper ────────────────────────────────────────────────────────────────────
def make_jpeg_file(width: int = 224, height: int = 224) -> bytes:
    img = Image.new("RGB", (width, height), color=(85, 170, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


JPEG_BYTES = make_jpeg_file()


# ── Health Check ──────────────────────────────────────────────────────────────
class TestHealthEndpoint:
    def test_health_200(self):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_status_ok(self):
        r = client.get("/api/health")
        assert r.json()["status"] == "ok"

    def test_health_has_version(self):
        r = client.get("/api/health")
        assert "version" in r.json()

    def test_health_has_crops(self):
        r = client.get("/api/health")
        data = r.json()
        assert "crops" in data
        assert len(data["crops"]) >= 17


# ── Weather ───────────────────────────────────────────────────────────────────
class TestWeatherEndpoints:
    def test_districts_200(self):
        r = client.get("/api/weather/districts")
        assert r.status_code == 200

    def test_districts_returns_36(self):
        r = client.get("/api/weather/districts")
        data = r.json()
        assert "districts" in data
        assert len(data["districts"]) == 36

    def test_weather_pune_200(self):
        r = client.get("/api/weather/pune")
        assert r.status_code == 200

    def test_weather_pune_fields(self):
        r = client.get("/api/weather/pune")
        data = r.json()
        for field in ("temperature", "humidity", "rainfall", "source"):
            assert field in data, f"Missing field '{field}' in weather response"

    def test_weather_unknown_district_200(self):
        """Unknown districts should not 500 — they should fall back to mock."""
        r = client.get("/api/weather/atlantis")
        assert r.status_code == 200


# ── Disease Classes ───────────────────────────────────────────────────────────
class TestDiseaseClassesEndpoint:
    def test_disease_classes_200(self):
        r = client.get("/api/disease/classes")
        assert r.status_code == 200

    def test_disease_classes_count(self):
        r = client.get("/api/disease/classes")
        data = r.json()
        assert data["count"] == 38
        assert len(data["diseases"]) == 38

    def test_each_disease_has_required_fields(self):
        r = client.get("/api/disease/classes")
        diseases = r.json()["diseases"]
        required = {"class_index", "name", "crop", "is_healthy", "severity",
                    "description", "chemical_treatment", "organic_treatment"}
        for d in diseases:
            missing = required - d.keys()
            assert missing == set(), f"Disease idx {d.get('class_index')} missing: {missing}"

    def test_potato_healthy_at_21(self):
        r = client.get("/api/disease/classes")
        diseases = r.json()["diseases"]
        d = diseases[21]
        assert d["class_index"] == 21
        assert d["is_healthy"] is True, f"Index 21 should be healthy potato, got: {d['name']}"

    def test_potato_late_blight_at_22(self):
        r = client.get("/api/disease/classes")
        diseases = r.json()["diseases"]
        d = diseases[22]
        assert d["class_index"] == 22
        assert d["is_healthy"] is False, f"Index 22 should be Potato Late Blight, got: {d['name']}"


# ── Predict ───────────────────────────────────────────────────────────────────
class TestPredictEndpoint:
    @pytest.fixture(scope="class")
    def prediction(self):
        r = client.post(
            "/api/predict",
            data={
                "crop":     "tomato",
                "district": "pune",
                "N":        "60",
                "P":        "30",
                "K":        "30",
            },
            files={"image": ("leaf.jpg", JPEG_BYTES, "image/jpeg")},
        )
        return r

    def test_predict_200(self, prediction):
        assert prediction.status_code == 200

    def test_predict_status_success(self, prediction):
        assert prediction.json()["status"] == "success"

    def test_predict_has_disease(self, prediction):
        data = prediction.json()
        assert "disease" in data
        assert "name" in data["disease"]

    def test_predict_has_yield(self, prediction):
        data = prediction.json()
        assert "yield_t_ha" in data
        assert data["yield_t_ha"] >= 0

    def test_predict_has_fertilizer(self, prediction):
        data = prediction.json()
        assert "fertilizer" in data
        fert = data["fertilizer"]
        assert "Urea" in fert["fertilizers"]
        assert "DAP"  in fert["fertilizers"]
        assert "MOP"  in fert["fertilizers"]

    def test_predict_has_low_confidence_flag(self, prediction):
        data = prediction.json()
        assert "low_confidence" in data
        assert isinstance(data["low_confidence"], bool)

    def test_predict_has_surplus_n_warning(self, prediction):
        data = prediction.json()
        fert = data["fertilizer"]
        assert "surplus_n_warning" in fert

    def test_predict_confidence_is_percentage(self, prediction):
        data = prediction.json()
        conf = data["disease"]["confidence"]
        assert 0.0 <= conf <= 100.0

    def test_predict_bad_image_returns_400(self):
        r = client.post(
            "/api/predict",
            data={"crop": "tomato", "district": "pune", "N": "60", "P": "30", "K": "30"},
            files={"image": ("bad.jpg", b"not_an_image", "image/jpeg")},
        )
        assert r.status_code == 400

    def test_predict_all_17_crops(self):
        """All 17 supported crops should return 200 (not crash on NPK lookup)."""
        crops = [
            "cotton", "wheat", "maize", "rice", "potato",
            "tomato", "pepper", "apple", "grape", "orange",
            "peach", "strawberry", "blueberry", "cherry",
            "raspberry", "soybean", "squash",
        ]
        for crop in crops:
            r = client.post(
                "/api/predict",
                data={"crop": crop, "district": "pune", "N": "50", "P": "25", "K": "25"},
                files={"image": ("leaf.jpg", JPEG_BYTES, "image/jpeg")},
            )
            assert r.status_code == 200, f"Crop '{crop}' returned {r.status_code}: {r.text}"


# ── Model Reload ──────────────────────────────────────────────────────────────
class TestModelReloadEndpoint:
    def test_reload_200(self):
        r = client.post("/api/model/reload")
        assert r.status_code == 200

    def test_reload_has_status(self):
        r = client.post("/api/model/reload")
        assert r.json()["status"] == "reloaded"

    def test_reload_has_mock_mode(self):
        r = client.post("/api/model/reload")
        assert "mock_mode" in r.json()


# ── Frontend Serving ─────────────────────────────────────────────────────────
class TestFrontendServing:
    def test_root_serves_frontend_html(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "AeroCrop.ai" in r.text

