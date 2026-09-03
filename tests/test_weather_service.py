import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from services.weather_service import WeatherService, DISTRICT_COORDINATES

# ── helpers ──────────────────────────────────────────────────────────────────
def run(coro):
    """Run an async coroutine synchronously (pytest doesn't need asyncio mark)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestDistrictRegistry:
    def test_36_districts(self):
        assert len(DISTRICT_COORDINATES) == 36

    def test_pune_in_districts(self):
        assert "pune" in DISTRICT_COORDINATES

    def test_nagpur_in_districts(self):
        assert "nagpur" in DISTRICT_COORDINATES

    def test_coordinates_are_valid(self):
        """All lat/lon should be within Maharashtra's geographic bounds."""
        for district, (lat, lon) in DISTRICT_COORDINATES.items():
            assert 15.0 <= lat <= 23.0, f"{district}: lat={lat} out of Maharashtra range"
            assert 72.0 <= lon <= 81.0, f"{district}: lon={lon} out of Maharashtra range"


class TestMockFallback:
    def test_mock_is_deterministic(self):
        """The same district should always return the same mock temperature."""
        w1 = WeatherService._mock_weather("pune")
        w2 = WeatherService._mock_weather("pune")
        assert w1["temperature"] == w2["temperature"]
        assert w1["humidity"]    == w2["humidity"]
        assert w1["rainfall"]    == w2["rainfall"]

    def test_mock_temperature_in_range(self):
        w = run(WeatherService.fetch_weather("nagpur"))
        assert 15 <= w["temperature"] <= 45, f"Temperature out of range: {w['temperature']}"

    def test_mock_humidity_in_range(self):
        w = run(WeatherService.fetch_weather("nashik"))
        assert 20 <= w["humidity"] <= 100, f"Humidity out of range: {w['humidity']}"

    def test_mock_rainfall_non_negative(self):
        w = run(WeatherService.fetch_weather("kolhapur"))
        assert w["rainfall"] >= 0, f"Rainfall should not be negative: {w['rainfall']}"

    def test_unknown_district_returns_data(self):
        """An unknown district should not raise — should return mock data."""
        w = run(WeatherService.fetch_weather("atlantis"))
        assert "temperature" in w
        assert "humidity" in w
        assert "rainfall" in w


class TestWeatherResponseSchema:
    def test_response_has_required_fields(self):
        w = run(WeatherService.fetch_weather("pune"))
        for key in ("temperature", "humidity", "rainfall", "source"):
            assert key in w, f"Missing field '{key}' in weather response"

    def test_all_values_are_numeric(self):
        w = run(WeatherService.fetch_weather("amravati"))
        assert isinstance(w["temperature"], (int, float))
        assert isinstance(w["humidity"],    (int, float))
        assert isinstance(w["rainfall"],    (int, float))

    def test_source_is_string(self):
        w = run(WeatherService.fetch_weather("solapur"))
        assert isinstance(w["source"], str)


class TestWeatherCache:
    def test_cache_hit_on_subsequent_request(self):
        WeatherService.clear_cache()
        # First request populates cache or uses mock
        w1 = run(WeatherService.fetch_weather("pune"))
        # If w1 was from api, second request must be from cache
        if w1["source"] == "api":
            w2 = run(WeatherService.fetch_weather("pune"))
            assert w2["source"] == "cache"
            assert w2["temperature"] == w1["temperature"]
            assert w2["humidity"] == w1["humidity"]

    def test_clear_cache_empties_storage(self):
        WeatherService.clear_cache()
        assert len(WeatherService._cache) == 0

