"""
schemas.py — Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class SubscriberCreate(BaseModel):
    contact_method: str = Field(..., pattern="^(telegram|email)$")
    contact_value: str
    district: str
    locality: str = "district_wide"

    @field_validator("contact_value")
    @classmethod
    def validate_contact(cls, v, info):
        method = info.data.get("contact_method", "")
        if method == "email":
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
                raise ValueError("Invalid email address")
        elif method == "telegram":
            if not v.strip():
                raise ValueError("Telegram chat ID required")
        return v

class SubscriberRead(BaseModel):
    id: int
    contact_method: str
    contact_value: str
    district: str
    locality: str
    created_at: str

class PredictionInput(BaseModel):
    district: str
    rainfall_mm: float = Field(ge=0, le=500)
    rainfall_3day: float = Field(ge=0, le=1500)
    rainfall_7day: float = Field(ge=0, le=3500)
    reservoir_level: float = Field(ge=0, le=100, default=50.0)
    reservoir_storage_percent: float = Field(ge=0, le=100, default=50.0)
    distance_to_river_km: float = Field(ge=0, default=5.0)
    elevation_m: float = Field(ge=0, default=500.0)
    slope: float = Field(ge=0, default=3.0)
    past_flood_count: int = Field(ge=0, default=0)
    drainage_score: float = Field(ge=0, le=100, default=50.0)

class AlertEventRead(BaseModel):
    id: int
    district: str
    locality: str
    predicted_date: str
    risk_level: str
    triggered_at: str
    notified: bool
