"""
AeroCrop.ai — MongoDB Document Models (Pydantic V2)

Models:
  - User: Farmer identity, credentials, default district, preferred language
  - FarmPlot: Farmer's multiple crop plots and acreage with soil baseline
  - DiagnosisRecord / AnalysisRecord: Full-fidelity multi-modal analysis document
    storing disease taxonomy, complete organic & chemical treatments,
    soil NPK inputs & target deficits, fertilizer commercial bag prescriptions & costs,
    weather telemetry & spray window advisories, mandi market rates & revenue projections,
    and ensemble telemetry.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    id: int
    phone_number: Optional[str] = None
    email: Optional[str] = None
    full_name: str
    hashed_password: str
    district: str = "pune"
    taluka_village: Optional[str] = None
    preferred_language: str = "en"
    token_version: int = 1
    is_active: bool = True
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class FarmPlot(BaseModel):
    id: int
    user_id: int
    plot_name: str
    crop_type: str
    area_acres: float = 1.0
    sowing_date: Optional[str] = None
    soil_type: str = "Medium Black"
    baseline_N: float = 60.0
    baseline_P: float = 30.0
    baseline_K: float = 30.0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)

    model_config = ConfigDict(populate_by_name=True)


class DiseasePayload(BaseModel):
    class_index: int
    name: str
    crop: str
    confidence: float
    severity: str = "None"
    is_healthy: bool = False
    description: str = ""
    chemical_treatment: List[str] = Field(default_factory=list)
    organic_treatment: List[str] = Field(default_factory=list)
    probabilities: Optional[List[float]] = None


class YieldPayload(BaseModel):
    predicted_yield_t_ha: float = 0.0
    quintals_per_ha: float = 0.0
    quintals_per_acre: float = 0.0


class SoilPayload(BaseModel):
    N: Optional[float] = None
    P: Optional[float] = None
    K: Optional[float] = None
    tested: bool = False


class FertilizerPayload(BaseModel):
    mode: str = "soil_test"
    target: Dict[str, float] = Field(default_factory=dict)
    deficit: Dict[str, float] = Field(default_factory=dict)
    fertilizers: Dict[str, float] = Field(default_factory=dict)
    interpretation: str = ""
    surplus_n_warning: Optional[str] = None
    commercial_bags: Optional[Dict[str, Any]] = None
    total_cost_inr_ha: Optional[float] = None


class WeatherPayload(BaseModel):
    temperature: float = 0.0
    humidity: float = 0.0
    rainfall: float = 0.0
    wind_speed: Optional[float] = None
    spray_window: Optional[Dict[str, Any]] = None
    source: str = "live"


class MandiPayload(BaseModel):
    crop: Optional[str] = None
    district: Optional[str] = None
    apmc_market: Optional[str] = None
    commodity_name: Optional[str] = None
    modal_price_inr: Optional[float] = None
    min_price_inr: Optional[float] = None
    max_price_inr: Optional[float] = None
    msp_inr: Optional[float] = None
    unit: Optional[str] = "Rs/Quintal"
    trend: Optional[str] = "steady"
    trend_change_pct: Optional[float] = 0.0
    revenue_projection: Optional[Dict[str, Any]] = None


class SystemTelemetryPayload(BaseModel):
    mock_mode: bool = False
    low_confidence: bool = False
    out_of_distribution: bool = False
    ood_reason: str = ""
    ensemble_verified: bool = False
    model_weights: Optional[str] = None

    model_config = {"protected_namespaces": ()}


class DiagnosisRecord(BaseModel):
    id: int
    user_id: int
    plot_id: Optional[int] = None
    plot_name: Optional[str] = None
    crop_type: str
    district: str
    image_filename: Optional[str] = None
    image_url: Optional[str] = None

    # Full Rich Analysis Payloads
    disease: DiseasePayload
    yield_data: YieldPayload = Field(default_factory=YieldPayload)
    soil: SoilPayload = Field(default_factory=SoilPayload)
    fertilizer: FertilizerPayload = Field(default_factory=FertilizerPayload)
    weather: WeatherPayload = Field(default_factory=WeatherPayload)
    mandi: Optional[MandiPayload] = None
    system_telemetry: SystemTelemetryPayload = Field(default_factory=SystemTelemetryPayload)

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    # Backward compatibility properties
    @property
    def disease_class_idx(self) -> int:
        return self.disease.class_index

    @property
    def disease_name(self) -> str:
        return self.disease.name

    @property
    def confidence(self) -> float:
        return self.disease.confidence

    @property
    def severity(self) -> str:
        return self.disease.severity

    @property
    def is_healthy(self) -> bool:
        return self.disease.is_healthy

    @property
    def predicted_yield_t_ha(self) -> float:
        return self.yield_data.predicted_yield_t_ha

    @property
    def soil_N(self) -> Optional[float]:
        return self.soil.N

    @property
    def soil_P(self) -> Optional[float]:
        return self.soil.P

    @property
    def soil_K(self) -> Optional[float]:
        return self.soil.K

    @property
    def fertilizer_urea_kg(self) -> float:
        return self.fertilizer.fertilizers.get("Urea", 0.0)

    @property
    def fertilizer_dap_kg(self) -> float:
        return self.fertilizer.fertilizers.get("DAP", 0.0)

    @property
    def fertilizer_mop_kg(self) -> float:
        return self.fertilizer.fertilizers.get("MOP", 0.0)

    @property
    def weather_temp(self) -> float:
        return self.weather.temperature

    @property
    def weather_hum(self) -> float:
        return self.weather.humidity

    @property
    def weather_rain(self) -> float:
        return self.weather.rainfall

    @property
    def mock_mode(self) -> bool:
        return self.system_telemetry.mock_mode

    @property
    def low_confidence(self) -> bool:
        return self.system_telemetry.low_confidence

    model_config = ConfigDict(populate_by_name=True)


AnalysisRecord = DiagnosisRecord
Base = None
