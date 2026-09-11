"""
AeroCrop.ai — Weather Controller

Endpoints:
  GET  /api/weather/{district}   → Fetch live weather for a district
  GET  /api/weather/districts    → List all supported Maharashtra districts

MVC Role: Controller — delegates to WeatherService, returns JSON.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.weather_service import WeatherService

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/districts", summary="List all supported Maharashtra districts")
async def list_districts():
    districts = WeatherService.get_district_list()
    return JSONResponse({"count": len(districts), "districts": districts})


@router.get("/{district}", summary="Fetch live weather for a district")
async def get_weather(district: str):
    if not district.strip():
        raise HTTPException(status_code=400, detail="District name is required.")
    data = await WeatherService.fetch_weather(district)
    return JSONResponse(data)
