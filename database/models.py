"""
AeroCrop.ai — SQLAlchemy Declarative Data Models

Models:
  - User: Farmer identity, credentials, default district, preferred language
  - FarmPlot: Farmer's multiple crop plots and acreage with soil baseline
  - DiagnosisRecord: Persistent historical leaf assessment records, NPK & weather snapshots
"""

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for all AeroCrop models."""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(64), nullable=False, default="pune")
    taluka_village: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")  # en, mr, hi
    token_version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    plots: Mapped[List["FarmPlot"]] = relationship(
        "FarmPlot", back_populates="owner", cascade="all, delete-orphan", order_by="FarmPlot.id.desc()"
    )
    diagnoses: Mapped[List["DiagnosisRecord"]] = relationship(
        "DiagnosisRecord", back_populates="user", cascade="all, delete-orphan", order_by="DiagnosisRecord.id.desc()"
    )


class FarmPlot(Base):
    __tablename__ = "farm_plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_name: Mapped[str] = mapped_column(String(120), nullable=False)  # e.g., "North Field", "Gat No. 12"
    crop_type: Mapped[str] = mapped_column(String(64), nullable=False)  # cotton, tomato, wheat, etc.
    area_acres: Mapped[float] = mapped_column(Float, default=1.0)
    sowing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    soil_type: Mapped[str] = mapped_column(String(64), default="Medium Black")
    baseline_N: Mapped[float] = mapped_column(Float, default=60.0)
    baseline_P: Mapped[float] = mapped_column(Float, default=30.0)
    baseline_K: Mapped[float] = mapped_column(Float, default=30.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="plots")
    diagnoses: Mapped[List["DiagnosisRecord"]] = relationship(
        "DiagnosisRecord", back_populates="plot"
    )


class DiagnosisRecord(Base):
    __tablename__ = "diagnosis_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("farm_plots.id", ondelete="SET NULL"), index=True, nullable=True)
    
    crop_type: Mapped[str] = mapped_column(String(64), nullable=False)
    district: Mapped[str] = mapped_column(String(64), nullable=False)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    disease_class_idx: Mapped[int] = mapped_column(Integer, nullable=False)
    disease_name: Mapped[str] = mapped_column(String(160), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="None")
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=False)
    
    predicted_yield_t_ha: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Soil nutrient state during diagnosis (optional)
    soil_N: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)
    soil_P: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)
    soil_K: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)
    
    # Prescribed fertilizer quantities (kg/ha)
    fertilizer_urea_kg: Mapped[float] = mapped_column(Float, default=0.0)
    fertilizer_dap_kg: Mapped[float] = mapped_column(Float, default=0.0)
    fertilizer_mop_kg: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Weather telemetry at diagnosis time
    weather_temp: Mapped[float] = mapped_column(Float, default=0.0)
    weather_hum: Mapped[float] = mapped_column(Float, default=0.0)
    weather_rain: Mapped[float] = mapped_column(Float, default=0.0)

    mock_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    low_confidence: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="diagnoses")
    plot: Mapped[Optional["FarmPlot"]] = relationship("FarmPlot", back_populates="diagnoses")

# Composite index for querying recent diagnostics by user and date efficiently
Index("ix_user_diagnoses_created_at", DiagnosisRecord.user_id, DiagnosisRecord.created_at.desc())
