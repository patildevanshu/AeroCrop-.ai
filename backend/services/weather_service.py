"""
AeroCrop.ai — Weather Service

Fetches real-time weather (temperature, humidity, rainfall) for any of the
36 districts of Maharashtra from the Open-Meteo free API with 30-minute TTL caching.

API docs: https://open-meteo.com/en/docs
"""

from __future__ import annotations
import httpx
import logging
import time
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
    "gadchiroli":   (20.1849, 79.9948),
    "gondia":       (21.4598, 80.1961),
    "hingoli":      (19.7196, 77.1481),
    "jalgaon":      (21.0077, 75.5626),
    "jalna":        (19.8347, 75.8816),
    "kolhapur":     (16.7050, 74.2433),
    "latur":        (18.4088, 76.5604),
    "mumbai":       (19.0760, 72.8777),
    "nagpur":       (21.1458, 79.0882),
    "nanded":       (19.1383, 77.3210),
    "nandurbar":    (21.3697, 74.2403),
    "nashik":       (19.9975, 73.7898),
    "osmanabad":    (18.1856, 76.0419),
    "palghar":      (19.6967, 72.7699),
    "parbhani":     (19.2610, 76.7767),
    "pune":         (18.5204, 73.8567),
    "raigad":       (18.5158, 73.1822),
    "ratnagiri":    (16.9902, 73.3120),
    "sangli":       (16.8524, 74.5815),
    "satara":       (17.6805, 73.9933),
    "sindhudurg":   (16.1670, 73.6670),
    "solapur":      (17.6599, 75.9064),
    "thane":        (19.2183, 72.9781),
    "wardha":       (20.7453, 78.6022),
    "washim":       (20.1119, 77.1442),
    "yavatmal":     (20.3888, 78.1204),
    "mumbai city":  (18.9667, 72.8333),
}


class WeatherService:

    _cache: dict[str, dict] = {}  # {district_key: {"data": dict, "timestamp": float}}

    @staticmethod
    def get_district_list() -> list[str]:
        return sorted(DISTRICT_COORDINATES.keys())

    @staticmethod
    def clear_cache() -> None:
        """Clear cached weather telemetry (useful for unit tests)."""
        WeatherService._cache.clear()

    @staticmethod
    async def fetch_weather(district: str) -> dict[str, Any]:
        """
        Fetch current weather for a Maharashtra district with 30-minute TTL caching.

        Returns:
            {
                "district"    : str,
                "temperature" : float,   # °C
                "humidity"    : float,   # %
                "rainfall"    : float,   # mm (last hour)
                "source"      : "api" | "mock" | "cache"
            }
        """
        key = district.lower().strip()

        # Check in-memory cache first
        now = time.time()
        if key in WeatherService._cache:
            entry = WeatherService._cache[key]
            if (now - entry["timestamp"]) < config.WEATHER_CACHE_TTL_SECONDS:
                cached_data = dict(entry["data"])
                cached_data["source"] = "cache"
                return cached_data

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
            temp = round(float(current.get("temperature_2m", 28.0)), 1)
            hum = round(float(current.get("relative_humidity_2m", 65.0)), 1)
            rain = round(float(current.get("precipitation", 0.0)), 2)
            wind = round(float(current.get("wind_speed_10m", 8.0)), 1)

            spray_window = WeatherService.calculate_spray_window(temp, hum, rain, wind)

            result = {
                "district":     district.title(),
                "temperature":  temp,
                "humidity":     hum,
                "rainfall":     rain,
                "wind_speed":   wind,
                "spray_window": spray_window,
                "latitude":     lat,
                "longitude":    lon,
                "source":       "api",
            }
            # Cache the successful API response
            WeatherService._cache[key] = {"data": result, "timestamp": now}
            return result

        except Exception as exc:
            logger.warning("Weather API failed for '%s': %s — using mock.", district, exc)
            return WeatherService._mock_weather(district)

    @staticmethod
    def calculate_spray_window(temperature: float, humidity: float, rainfall: float, wind_speed: float) -> dict[str, Any]:
        """
        Agronomic decision logic to determine if current conditions are suitable for foliar spraying.
        - Rainfall > 1.0mm: High risk of pesticide wash-off (Unsafe)
        - Wind speed > 15.0 km/h: Severe spray drift risking non-target areas & loss (Unsafe)
        - Humidity > 85%: Poor evaporation & increased fungal spore germination (Warning)
        - Temp > 35°C: Rapid droplet evaporation & risk of chemical leaf scorch (Warning)
        - Otherwise: Ideal/Safe
        """
        if rainfall > 1.0:
            return {
                "safe": False,
                "status": "danger",
                "badge": "🌧️ फवारणी टाळा / Do Not Spray",
                "reason": f"Active rainfall ({rainfall} mm) detected. Chemical spray will wash off immediately.",
                "reason_mr": f"पाऊस ({rainfall} मिमी) सुरू आहे/संभव आहे. औषध वाहून जाईल, फवारणी करू नका.",
                "reason_hi": f"बारिश ({rainfall} मिमी) के कारण दवा बह जाएगी, छिड़काव न करें।",
            }
        elif wind_speed > 15.0:
            return {
                "safe": False,
                "status": "danger",
                "badge": "💨 जोरदार वारा / High Wind Drift",
                "reason": f"High wind speed ({wind_speed} km/h). Severe pesticide drift risk to non-target areas.",
                "reason_mr": f"वाऱ्याचा वेग जास्त ({wind_speed} किमी/तास) आहे. औषध इतरत्र उडून वाया जाईल.",
                "reason_hi": f"हवा की गति तेज ({wind_speed} किमी/घंटा) है। छिड़काव भटक जाएगा।",
            }
        elif humidity > 85.0:
            return {
                "safe": True,
                "status": "warning",
                "badge": "💧 सावध राहा / High Humidity",
                "reason": f"High relative humidity ({humidity}%). Delayed drying time; spray cautiously.",
                "reason_mr": f"हवेत आर्द्रता जास्त ({humidity}%) आहे. औषध सुकण्यास वेळ लागेल, सावधपणे फवारा.",
                "reason_hi": f"हवा में नमी अधिक ({humidity}%) है। सावधानी से छिड़काव करें।",
            }
        elif temperature > 36.0:
            return {
                "safe": True,
                "status": "warning",
                "badge": "☀️ जास्त तापमान / High Heat",
                "reason": f"High temperature ({temperature}°C). Spray early morning or late evening to prevent leaf scorch.",
                "reason_mr": f"दुपारचे तापमान ({temperature}°से) जास्त आहे. सकाळी किंवा संध्याकाळी फवारणी करा.",
                "reason_hi": f"तापमान अधिक ({temperature}°C) है। सुबह या शाम को ही छिड़काव करें।",
            }
        else:
            return {
                "safe": True,
                "status": "success",
                "badge": "✅ फवारणीसाठी योग्य / Safe to Spray",
                "reason": f"Optimal weather conditions for foliar application. Wind {wind_speed} km/h, Temp {temperature}°C.",
                "reason_mr": f"फवारणीसाठी अनुकूल हवामान. वाऱ्याचा वेग {wind_speed} किमी/तास, तापमान {temperature}°से.",
                "reason_hi": f"छिड़काव के लिए अनुकूल मौसम। हवा {wind_speed} किमी/घंटा, तापमान {temperature}°C।",
            }

    @staticmethod
    def _mock_weather(district: str) -> dict[str, Any]:
        """Deterministic fallback weather when API is unavailable."""
        import hashlib
        seed = int(hashlib.md5(district.lower().encode()).hexdigest(), 16) % 100
        temp = round(25.0 + (seed % 15), 1)
        hum  = round(50.0 + (seed % 40), 1)
        rain = round((seed % 10) * 0.5, 2)
        wind = round(6.0 + (seed % 12), 1)
        spray = WeatherService.calculate_spray_window(temp, hum, rain, wind)

        return {
            "district":     district.title(),
            "temperature":  temp,
            "humidity":     hum,
            "rainfall":     rain,
            "wind_speed":   wind,
            "spray_window": spray,
            "latitude":     DISTRICT_COORDINATES.get(district.lower(), (19.0, 75.0))[0],
            "longitude":    DISTRICT_COORDINATES.get(district.lower(), (19.0, 75.0))[1],
            "source":       "mock",
        }
