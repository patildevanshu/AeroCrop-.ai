"""
AeroCrop.ai — Database Package
Provides asynchronous MongoDB client, session management, and document models.
"""

from database.mongodb import (
    get_db,
    init_mongodb,
    close_mongodb,
    get_client,
    get_database,
    get_next_sequence,
)
from database.models import (
    Base,
    User,
    FarmPlot,
    DiagnosisRecord,
    AnalysisRecord,
    DiseasePayload,
    YieldPayload,
    SoilPayload,
    FertilizerPayload,
    WeatherPayload,
    MandiPayload,
    SystemTelemetryPayload,
)

# Alias init_db for backward compatibility
init_db = init_mongodb

__all__ = [
    "get_db",
    "init_mongodb",
    "init_db",
    "close_mongodb",
    "get_client",
    "get_database",
    "get_next_sequence",
    "Base",
    "User",
    "FarmPlot",
    "DiagnosisRecord",
    "AnalysisRecord",
    "DiseasePayload",
    "YieldPayload",
    "SoilPayload",
    "FertilizerPayload",
    "WeatherPayload",
    "MandiPayload",
    "SystemTelemetryPayload",
]
