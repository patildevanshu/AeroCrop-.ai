"""
AeroCrop.ai — Mandi Controller

Endpoints:
  GET /api/mandi/{district}/{crop}  → Fetch APMC rates, trends, and projected revenue
  GET /api/mandi/overview/{district} → Overview of all primary crops in district APMC
  GET /api/mandi/crops              → Supported mandi crops

MVC Role: Controller — delegates to MandiService, returns JSON.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.mandi_service import MandiService

router = APIRouter(prefix="/api/mandi", tags=["Mandi"])


@router.get("/crops", summary="List supported commodities for APMC market rates")
async def list_mandi_crops():
    crops = MandiService.get_supported_crops()
    return JSONResponse({"count": len(crops), "crops": crops})


@router.get("/overview/{district}", summary="Get market overview for all crops in a district")
async def get_district_mandi_overview(district: str):
    if not district.strip():
        raise HTTPException(status_code=400, detail="District name is required.")
    data = MandiService.get_district_overview(district)
    return JSONResponse({"district": district.title(), "count": len(data), "market_rates": data})


@router.get("/{district}/{crop}", summary="Fetch APMC rate and projected revenue for a crop")
async def get_crop_mandi_rate(
    district: str,
    crop: str,
    yield_t_ha: Optional[float] = Query(None, description="Optional predicted yield in t/ha to compute gross revenue")
):
    if not district.strip() or not crop.strip():
        raise HTTPException(status_code=400, detail="Both district and crop are required.")
    data = MandiService.get_market_rate(district=district, crop=crop, yield_t_ha=yield_t_ha)
    return JSONResponse(data)
