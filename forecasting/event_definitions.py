"""
Meteorological Event Definitions Module: SIH26086
Implements authoritative operational criteria (India Meteorological Department - IMD)
coupled with configurable research thresholds for block-level agro-meteorology.

Scientific References:
1. Pai et al. (2014) - Operational Criteria for Monsoon Onset over Kerala, IMD Technical Report.
2. Rajeevan et al. (2010) - Active and Break Spells of the Indian Summer Monsoon, J. Earth Syst. Sci.
3. IMD Terminology & Rainfall Classification Guide:
   - Very Light Rain: 0.1 to 2.4 mm
   - Moderate Rain: 15.6 to 64.4 mm
   - Heavy Rain: 64.5 to 115.5 mm
   - Very Heavy Rain: 115.6 to 204.4 mm
   - Extremely Heavy Rain: >= 204.5 mm
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

@dataclass
class EventThresholdConfig:
    # 1. Onset Criteria (IMD Operational Standard)
    onset_min_daily_rainfall_mm: float = 2.5
    onset_consecutive_days_required: int = 2
    onset_zonal_wind_850hpa_min_ms: float = 7.7  # ~15 knots
    onset_olr_max_threshold_wm2: float = 200.0   # Deep convection proxy

    # 2. Active / Wet Spell Criteria
    active_spell_min_rain_mm_day: float = 10.0
    active_spell_min_consecutive_days: int = 3

    # 3. Break Spell & Dry Spell Criteria (IMD Core Monsoon Zone Definition)
    # Consecutive days with spatial rainfall < 2.5mm or deficit > 50%
    break_spell_max_rainfall_mm_day: float = 2.0
    break_spell_min_duration_days: int = 4
    break_spell_critical_duration_days: int = 7

    # 4. Rainfall Revival Criteria
    revival_min_rainfall_mm: float = 10.0
    revival_westerly_wind_min_ms: float = 6.0

    # 5. Heavy Rainfall Warning Thresholds (IMD Standard)
    heavy_rain_threshold_mm: float = 64.5
    very_heavy_rain_threshold_mm: float = 115.6
    extreme_heavy_rain_threshold_mm: float = 204.5

    # 6. Climatological Baseline Daily Normal (Kharif Monsoon Season ~ June to Sept)
    climatological_daily_normal_mm: float = 7.5

class MeteorologicalEventDetector:
    def __init__(self, config: Optional[EventThresholdConfig] = None):
        self.config = config or EventThresholdConfig()

    def evaluate_onset_criteria(
        self,
        recent_daily_rainfall: List[float],
        zonal_wind_850hpa_ms: Optional[float] = None,
        olr_wm2: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates IMD multi-parameter criteria for monsoon onset.
        """
        if len(recent_daily_rainfall) < self.config.onset_consecutive_days_required:
            return {
                "onset_detected": False,
                "confidence_score": 0.0,
                "status": "INSUFFICIENT_OBSERVATION_DAYS",
                "reasons": ["Fewer observation days than required for consecutive verification."]
            }

        last_n = recent_daily_rainfall[-self.config.onset_consecutive_days_required:]
        rain_satisfied = all(r >= self.config.onset_min_daily_rainfall_mm for r in last_n)

        # Wind & OLR criteria
        wind_satisfied = True if zonal_wind_850hpa_ms is None else (zonal_wind_850hpa_ms >= self.config.onset_zonal_wind_850hpa_min_ms)
        olr_satisfied = True if olr_wm2 is None else (olr_wm2 <= self.config.onset_olr_max_threshold_wm2)

        # False onset detection: rain happened, but no synoptic wind or satellite cloud support
        is_false_alarm = False
        reasons = []

        if rain_satisfied:
            if zonal_wind_850hpa_ms is not None and not wind_satisfied:
                is_false_alarm = True
                reasons.append("Pre-monsoon thunderstorm flagged: Surface rain observed without deep tropospheric westerly shear.")
            if olr_wm2 is not None and not olr_satisfied:
                is_false_alarm = True
                reasons.append("High Outgoing Longwave Radiation indicates localized cloudiness rather than synoptic monsoonal surge.")

        if rain_satisfied and wind_satisfied and olr_satisfied and not is_false_alarm:
            return {
                "onset_detected": True,
                "confidence_score": 0.92,
                "status": "ONSET_DECLARED",
                "is_false_alarm": False,
                "reasons": ["Consecutive 48-hr rainfall >= 2.5mm satisfied with supporting synoptic wind and low OLR."]
            }
        elif is_false_alarm:
            return {
                "onset_detected": False,
                "confidence_score": 0.45,
                "status": "FALSE_ONSET_WARNING",
                "is_false_alarm": True,
                "reasons": reasons
            }
        else:
            return {
                "onset_detected": False,
                "confidence_score": 0.60,
                "status": "PRE_MONSOON_OR_PENDING",
                "is_false_alarm": False,
                "reasons": ["Rainfall did not meet consecutive 48-hour operational threshold."]
            }

    def detect_break_spells(self, daily_rainfall: List[float]) -> Dict[str, Any]:
        """
        Detects observed or projected prolonged dry spells / monsoon breaks.
        """
        dry_streaks = []
        current_streak = 0

        for r in daily_rainfall:
            if r <= self.config.break_spell_max_rainfall_mm_day:
                current_streak += 1
            else:
                if current_streak > 0:
                    dry_streaks.append(current_streak)
                current_streak = 0
        if current_streak > 0:
            dry_streaks.append(current_streak)

        max_dry_streak = max(dry_streaks) if dry_streaks else 0
        is_break = max_dry_streak >= self.config.break_spell_min_duration_days
        is_critical = max_dry_streak >= self.config.break_spell_critical_duration_days

        if is_critical:
            risk_level = "CRITICAL"
            prob = 0.90
        elif is_break:
            risk_level = "HIGH"
            prob = 0.75
        elif max_dry_streak >= 2:
            risk_level = "MODERATE"
            prob = 0.40
        else:
            risk_level = "LOW"
            prob = 0.15

        return {
            "is_break_active": is_break,
            "risk_level": risk_level,
            "max_consecutive_dry_days": max_dry_streak,
            "break_probability": prob,
            "threshold_used_mm": self.config.break_spell_max_rainfall_mm_day
        }

    def compute_rainfall_anomaly(self, total_observed_mm: float, period_days: int) -> Dict[str, Any]:
        """
        Calculates rainfall departure percentage from climatological normal.
        Departure % = ((Observed - Normal) / Normal) * 100
        IMD Categorization:
        - Large Excess (LE): +60% or more
        - Excess (E): +20% to +59%
        - Normal (N): -19% to +19%
        - Deficient (D): -20% to -59%
        - Large Deficient (LD): -60% to -99%
        - No Rain (NR): -100%
        """
        normal = self.config.climatological_daily_normal_mm * max(1, period_days)
        dep_pct = ((total_observed_mm - normal) / normal) * 100.0

        if dep_pct >= 60.0:
            cat = "Large Excess"
        elif dep_pct >= 20.0:
            cat = "Excess"
        elif dep_pct >= -19.0:
            cat = "Normal"
        elif dep_pct >= -59.0:
            cat = "Deficient"
        else:
            cat = "Large Deficient"

        return {
            "observed_mm": round(total_observed_mm, 1),
            "normal_mm": round(normal, 1),
            "departure_percentage": round(dep_pct, 1),
            "category": cat
        }

    def evaluate_heavy_rainfall_risk(self, forecast_daily_rain: List[float]) -> Dict[str, Any]:
        """
        Classifies risk of heavy / extreme precipitation events in the forecast window.
        """
        max_rain = max(forecast_daily_rain) if forecast_daily_rain else 0.0

        if max_rain >= self.config.extreme_heavy_rain_threshold_mm:
            risk = "RED_ALERT_EXTREME"
            desc = f"Extremely Heavy Rainfall Expected (≥{self.config.extreme_heavy_rain_threshold_mm} mm)"
        elif max_rain >= self.config.very_heavy_rain_threshold_mm:
            risk = "ORANGE_ALERT_VERY_HEAVY"
            desc = f"Very Heavy Rainfall Expected ({self.config.very_heavy_rain_threshold_mm}–{self.config.extreme_heavy_rain_threshold_mm} mm)"
        elif max_rain >= self.config.heavy_rain_threshold_mm:
            risk = "YELLOW_ALERT_HEAVY"
            desc = f"Heavy Rainfall Expected ({self.config.heavy_rain_threshold_mm}–{self.config.very_heavy_rain_threshold_mm} mm)"
        else:
            risk = "GREEN_NO_HEAVY_RAIN"
            desc = "No heavy rainfall events projected in current horizon."

        return {
            "heavy_rainfall_risk": risk,
            "description": desc,
            "max_projected_daily_mm": max_rain
        }
