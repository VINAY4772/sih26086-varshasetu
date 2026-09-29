from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class MonsoonPhase(str, Enum):
    PRE_MONSOON = "pre_monsoon"
    ONSET_WATCH = "onset_watch"
    ONSET_ACTIVE = "onset_active"
    ACTIVE_MONSOON = "active_monsoon"
    BREAK_SPELL_WARNING = "break_spell_warning"
    BREAK_SPELL_ACTIVE = "break_spell_active"
    WITHDRAWAL = "withdrawal"

class SowingSuitability(str, Enum):
    OPTIMAL = "optimal"
    FAVORABLE = "favorable"
    WAIT_FOR_MOISTURE = "wait_for_moisture"
    AVOID_EXCESS_WATER = "avoid_excess_water"
    HIGH_RISK_DRY = "high_risk_dry"

class Location(BaseModel):
    id: str
    name: str
    block: str
    district: str
    state: str
    lat: float
    lon: float
    elevation_m: Optional[float] = 150.0
    primary_soil: Optional[str] = "Clay Loam"
    agro_climatic_zone: Optional[str] = "Central Plateau & Hills"

class WeatherDailyPoint(BaseModel):
    date: str
    rainfall_mm: float
    temp_max_c: float
    temp_min_c: float
    humidity_pct: float
    wind_speed_ms: float
    wind_direction_deg: float
    olr_wm2: float  # Outgoing Longwave Radiation (<200 indicates deep convection)
    zonal_wind_850hpa_ms: float  # Westerly wind strength at 850hPa
    soil_moisture_pct: float

class OnsetCriteriaStatus(BaseModel):
    consecutive_rain_days: int
    rainfall_threshold_met: bool
    westerly_wind_depth_met: bool
    olr_convection_met: bool
    surface_wind_persistence_met: bool

class OnsetForecastResponse(BaseModel):
    location: Location
    current_phase: MonsoonPhase
    onset_status: str  # "Not Started", "Imminent (3-5 Days)", "Onset Declared", "Advancing"
    predicted_onset_date: Optional[str]
    normal_onset_date: str
    onset_anomaly_days: int  # Negative = early, Positive = delayed
    confidence_score: float  # 0 to 100%
    criteria: OnsetCriteriaStatus
    synoptic_features: List[str]
    historical_comparison: Dict[str, Any]

class BreakSpellRiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class BreakSpellForecastResponse(BaseModel):
    location: Location
    risk_level: BreakSpellRiskLevel
    break_probability_pct: float
    is_break_active: bool
    estimated_dry_spell_days: int
    trough_position_anomaly: str  # "Normal (Gangetic Plain)", "Foot-hills of Himalayas", "Weakened"
    rainfall_deficit_pct: float
    soil_moisture_depletion_rate: str
    forecast_timeline: List[Dict[str, Any]]
    protective_measures: List[str]

class CropAdvisory(BaseModel):
    crop_name: str
    crop_code: str
    sowing_status: SowingSuitability
    sowing_window: str
    soil_moisture_status: str
    irrigation_advice: str
    fertilizer_advice: str
    pest_disease_watch: str
    action_item: str

class FullAdvisoryResponse(BaseModel):
    location: Location
    language: str
    generated_at: str
    monsoon_headline: str
    overall_advice: str
    crop_advisories: List[CropAdvisory]
    alert_level: str  # "Green", "Yellow", "Orange", "Red"

class IsochroneGeoJSON(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]

class RadarGridPoint(BaseModel):
    lat: float
    lon: float
    intensity_mm_hr: float
    cloud_top_km: float
