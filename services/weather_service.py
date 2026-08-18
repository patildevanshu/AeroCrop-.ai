"""
AeroCrop.ai — Weather Service

Fetches real-time weather (temperature, humidity, rainfall) for any of the
36 districts of Maharashtra from the Open-Meteo free API.

API docs: https://open-meteo.com/en/docs
"""

from __future__ import annotations
import httpx
import logging
from typing import Any

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

# ── Maharashtra Districts → (Latitude, Longitude) ────────────────────────────
DISTRICT_COORDINATES: dict[str, tuple[float, float]] = {
    "ahmednagar":   (19.0952, 74.7480),
    "akola":        (20.7002, 77.0082),
    "amravati":     (20.9374, 77.7796),
    "aurangabad":   (19.8762, 75.3433),
    "beed":         (18.9890, 75.7600),
    "bhandara":     (21.1667, 79.6500),
    "buldhana":     (20.5292, 76.1842),
    "chandrapur":   (19.9615, 79.2961),
    "dhule":        (20.9042, 74.7749),
    "gadchiroli":   (20.1809, 80.0000),
    "gondia":       (21.4600, 80.1900),
    "hingoli":      (19.7167, 77.1500),
    "jalgaon":      (21.0077, 75.5626),
    "jalna":        (19.8347, 75.8816),
    "kolhapur":     (16.7050, 74.2433),
    "latur":        (18.4088, 76.5604),
    "mumbai":       (19.0760, 72.8777),
    "nagpur":       (21.1458, 79.0882),
    "nanded":       (19.1383, 77.3210),
    "nandurbar":    (21.3700, 74.2400),
    "nashik":       (19.9975, 73.7898),
    "osmanabad":    (18.1860, 76.0410),
    "palghar":      (19.6967, 72.7650),
    "parbhani":     (19.2609, 76.7760),
    "pune":         (18.5204, 73.8567),
    "raigad":       (18.5158, 73.1228),
    "ratnagiri":    (16.9902, 73.3120),
    "sangli":       (16.8524, 74.5815),
    "satara":       (17.6805, 74.0183),
    "sindhudurg":   (16.3500, 73.6667),
    "solapur":      (17.6868, 75.9064),
    "thane":        (19.2183, 72.9781),
    "wardha":       (20.7453, 78.6022),
    "washim":       (20.1119, 77.1442),
    "yavatmal":     (20.3888, 78.1204),
    "mumbai city":  (18.9667, 72.8333),
}


class WeatherService:

    @staticmethod
    def get_district_list() -> list[str]:
        return sorted(DISTRICT_COORDINATES.keys())

    @staticmethod
    async def fetch_weather(district: str) -> dict[str, Any]:
        """
        Fetch current weather for a Maharashtra district.

        Returns:
            {
                "district"    : str,
                "temperature" : float,   # °C
                "humidity"    : float,   # %
                "rainfall"    : float,   # mm (last hour)
                "source"      : "api" | "mock"
            }
        """
        key = district.lower().strip()
        coords = DISTRICT_COORDINATES.get(key)

        if coords is None:
            logger.warning("Unknown district '%s'; returning mock weather.", district)
            return WeatherService._mock_weather(district)

        lat, lon = coords
        params = {
            "latitude":          lat,
            "longitude":         lon,
            "current":           ",".join(config.WEATHER_PARAMS),
            "timezone":          "Asia/Kolkata",
            "forecast_days":     1,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(config.OPEN_METEO_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            current = data.get("current", {})
            return {
                "district":    district.title(),
                "temperature": round(float(current.get("temperature_2m", 28.0)), 1),
                "humidity":    round(float(current.get("relative_humidity_2m", 65.0)), 1),
                "rainfall":    round(float(current.get("precipitation", 0.0)), 2),
                "latitude":    lat,
                "longitude":   lon,
                "source":      "api",
            }

        except Exception as exc:
            logger.warning("Weather API failed for '%s': %s — using mock.", district, exc)
            return WeatherService._mock_weather(district)

    @staticmethod
    def _mock_weather(district: str) -> dict[str, Any]:
        """Deterministic fallback weather when API is unavailable."""
        import hashlib
        seed = int(hashlib.md5(district.lower().encode()).hexdigest(), 16) % 100
        return {
            "district":    district.title(),
            "temperature": round(25.0 + (seed % 15), 1),
            "humidity":    round(50.0 + (seed % 40), 1),
            "rainfall":    round((seed % 10) * 0.5, 2),
            "latitude":    DISTRICT_COORDINATES.get(district.lower(), (19.0, 75.0))[0],
            "longitude":   DISTRICT_COORDINATES.get(district.lower(), (19.0, 75.0))[1],
            "source":      "mock",
        }
