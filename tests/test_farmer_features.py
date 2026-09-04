"""
AeroCrop.ai — Automated Tests for Farmer-Centric Features
Tests:
  1. Weather Spray Safety Decision Logic
  2. Commercial 50kg Fertilizer Bags & Cost Math
  3. APMC Mandi Intelligence & Revenue Forecasting
  4. Mandi and Weather API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from services.weather_service import WeatherService
from services.fertilizer_service import FertilizerService
from services.mandi_service import MandiService

client = TestClient(app)


# ── 1. Weather Spray Safety Decision Tree Tests ─────────────────────────────

def test_spray_window_danger_rain():
    """Verify rainfall > 1.0 mm triggers danger status to prevent chemical wash-off."""
    res = WeatherService.calculate_spray_window(temperature=28.0, humidity=70.0, rainfall=2.5, wind_speed=8.0)
    assert res["safe"] is False
    assert res["status"] == "danger"
    assert "पाऊस" in res["reason_mr"]
    assert "rainfall" in res["reason"].lower()


def test_spray_window_danger_high_wind():
    """Verify wind speed > 15.0 km/h triggers drift danger."""
    res = WeatherService.calculate_spray_window(temperature=27.0, humidity=60.0, rainfall=0.0, wind_speed=18.5)
    assert res["safe"] is False
    assert res["status"] == "danger"
    assert "वाऱ्याचा वेग" in res["reason_mr"]


def test_spray_window_warning_humidity():
    """Verify high humidity (> 85%) triggers warning."""
    res = WeatherService.calculate_spray_window(temperature=26.0, humidity=88.0, rainfall=0.0, wind_speed=7.0)
    assert res["safe"] is True
    assert res["status"] == "warning"
    assert "आर्द्रता" in res["reason_mr"]


def test_spray_window_optimal():
    """Verify normal conditions yield safe/success status."""
    res = WeatherService.calculate_spray_window(temperature=25.0, humidity=65.0, rainfall=0.0, wind_speed=8.0)
    assert res["safe"] is True
    assert res["status"] == "success"
    assert "अनुकूल" in res["reason_mr"]


# ── 2. Commercial 50kg Fertilizer Bags & Cost Tests ──────────────────────────

def test_fertilizer_commercial_bags_calculation():
    """Verify deficit is converted into 50kg bags and INR costs."""
    result = FertilizerService.calculate(crop="wheat", soil_N=40.0, soil_P=20.0, soil_K=20.0)
    
    assert "commercial_bags" in result
    assert "total_cost_inr_ha" in result
    
    bags = result["commercial_bags"]
    assert "Urea" in bags
    assert "DAP" in bags
    assert "MOP" in bags
    
    # Check that bags are positive
    assert bags["Urea"]["bags_50kg"] > 0
    assert bags["DAP"]["bags_50kg"] > 0
    assert bags["MOP"]["bags_50kg"] > 0
    
    # Check cost computation
    assert bags["Urea"]["cost_inr"] == round((bags["Urea"]["kg"] / 50.0) * 267.0, 0)
    assert bags["DAP"]["cost_inr"] == round((bags["DAP"]["kg"] / 50.0) * 1350.0, 0)
    assert bags["MOP"]["cost_inr"] == round((bags["MOP"]["kg"] / 50.0) * 1700.0, 0)
    assert result["total_cost_inr_ha"] > 0


# ── 3. Mandi Intelligence & Revenue Forecast Tests ───────────────────────────

def test_mandi_service_rates_and_revenue():
    """Verify APMC price lookup and yield-to-revenue math."""
    data = MandiService.get_market_rate(district="jalgaon", crop="cotton", yield_t_ha=2.5)
    
    assert data["crop"] == "cotton"
    assert data["district"] == "Jalgaon"
    assert data["modal_price_inr"] > 5000
    assert data["min_price_inr"] <= data["modal_price_inr"] <= data["max_price_inr"]
    assert data["trend"] in ["bullish", "bearish", "steady"]
    
    rev = data["revenue_projection"]
    assert rev is not None
    assert rev["yield_t_ha"] == 2.5
    assert rev["yield_quintals_per_ha"] == 25.0
    # 25 q/ha / 2.47105 = ~10.12 q/acre
    assert 10.0 <= rev["yield_quintals_per_acre"] <= 10.5
    assert rev["gross_revenue_ha_inr"] == 25.0 * data["modal_price_inr"]
    assert rev["gross_revenue_acre_inr"] > 0


def test_mandi_district_overview():
    """Verify multi-commodity overview for an APMC hub."""
    overview = MandiService.get_district_overview("nashik")
    assert len(overview) >= 5
    crops = [item["crop"] for item in overview]
    assert "wheat" in crops
    assert "tomato" in crops
    assert "potato" in crops


# ── 4. REST API Endpoint Tests ───────────────────────────────────────────────

def test_api_mandi_endpoint():
    resp = client.get("/api/mandi/pune/wheat?yield_t_ha=3.0")
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data["crop"] == "wheat"
    assert json_data["modal_price_inr"] > 0
    assert json_data["revenue_projection"]["gross_revenue_ha_inr"] > 0


def test_api_mandi_overview_endpoint():
    resp = client.get("/api/mandi/overview/nashik")
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data["count"] >= 5
    assert len(json_data["market_rates"]) >= 5


def test_api_weather_spray_window():
    resp = client.get("/api/weather/pune")
    assert resp.status_code == 200
    data = resp.json()
    assert "spray_window" in data
    assert "wind_speed" in data
    assert "safe" in data["spray_window"]
    assert "badge" in data["spray_window"]


def test_farmer_predict_journey_with_weather_and_mandi():
    """Simulate a complete farmer submission: leaf photo + soil + district."""
    import io
    from PIL import Image

    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/predict",
        data={
            "crop": "cotton",
            "district": "jalgaon",
            "N": 50.0,
            "P": 25.0,
            "K": 25.0,
        },
        files={"image": ("leaf.jpg", buf, "image/jpeg")},
    )

    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "success"
    assert res["crop"] == res["disease"]["crop"]
    assert res["district"] == "Jalgaon"

    # 1. Weather & Spray Window Verification
    weather = res["weather"]
    assert "temperature" in weather
    assert "humidity" in weather
    assert "rainfall" in weather
    assert "wind_speed" in weather
    assert "spray_window" in weather
    assert "safe" in weather["spray_window"]
    assert "status" in weather["spray_window"]

    # 2. Commercial Bags & Fertilizer Verification
    fert = res["fertilizer"]
    assert "commercial_bags" in fert
    assert "Urea" in fert["commercial_bags"]
    assert "DAP" in fert["commercial_bags"]
    assert "MOP" in fert["commercial_bags"]
    assert fert["total_cost_inr_ha"] > 0

    # 3. Mandi Intelligence & Revenue Verification (in the context of the auto-detected crop!)
    mandi = res["mandi"]
    assert mandi is not None
    assert mandi["crop"] == res["crop_key"]
    assert mandi["district"] == "Jalgaon"
    assert mandi["modal_price_inr"] > 0
    assert mandi["revenue_projection"] is not None
    assert mandi["revenue_projection"]["gross_revenue_ha_inr"] > 0
    assert mandi["revenue_projection"]["gross_revenue_acre_inr"] > 0


def test_frictionless_predict_without_npk():
    """Verify that a farmer can diagnose with only a photo, crop, and district without entering NPK."""
    import io
    from PIL import Image

    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/predict",
        data={
            "crop": "soybean",
            "district": "nagpur",
        },
        files={"image": ("leaf.jpg", buf, "image/jpeg")},
    )
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "success"
    assert "disease" in res
    assert "fertilizer" in res
    assert res["fertilizer"]["mode"] == "standard_pop"
    assert "commercial_bags" in res["fertilizer"]
    assert "Urea" in res["fertilizer"]["commercial_bags"]
    assert res["fertilizer"]["total_cost_inr_ha"] > 0
    assert "mandi" in res
    assert res["mandi"]["district"] == "Nagpur"


