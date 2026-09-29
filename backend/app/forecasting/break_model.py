from typing import List, Dict, Any
from ..models.schemas import (
    Location,
    WeatherDailyPoint,
    BreakSpellRiskLevel,
    BreakSpellForecastResponse
)

class BreakSpellForecastingEngine:
    """
    Forecasting Engine for Monsoon Break Spells & Agricultural Dry Spells.
    Detects northward displacement of monsoon trough, convective lulls,
    and root-zone soil moisture depletion.
    """

    def predict_break_spell(
        self,
        location: Location,
        history: List[WeatherDailyPoint],
        forecast: List[WeatherDailyPoint]
    ) -> BreakSpellForecastResponse:
        timeline: List[Dict[str, Any]] = []
        dry_days_in_forecast = 0
        total_forecast_rain = 0.0
        expected_normal_rain = len(forecast) * 7.5  # ~7.5mm daily normal during active phase

        for idx, pt in enumerate(forecast):
            total_forecast_rain += pt.rainfall_mm
            is_dry = pt.rainfall_mm < 1.5
            if is_dry:
                dry_days_in_forecast += 1

            timeline.append({
                "day_index": idx + 1,
                "date": pt.date,
                "rainfall_mm": pt.rainfall_mm,
                "soil_moisture_pct": pt.soil_moisture_pct,
                "temp_max_c": pt.temp_max_c,
                "dry_condition": is_dry,
                "evapotranspiration_stress": "High" if pt.temp_max_c > 34.0 and pt.humidity_pct < 55 else "Moderate"
            })

        # Calculate rainfall deficit percentage
        if expected_normal_rain > 0:
            deficit_pct = max(0.0, ((expected_normal_rain - total_forecast_rain) / expected_normal_rain) * 100.0)
        else:
            deficit_pct = 0.0

        # Assess Break Spell Risk Level
        # 7+ consecutive dry days with high deficit => Critical/High
        consecutive_dry = 0
        max_consecutive_dry = 0
        for pt in forecast:
            if pt.rainfall_mm < 1.5:
                consecutive_dry += 1
                if consecutive_dry > max_consecutive_dry:
                    max_consecutive_dry = consecutive_dry
            else:
                consecutive_dry = 0

        # Synoptic trough status inference
        # If forecast has high OLR and low zonal wind, trough has migrated to foothills
        avg_fc_olr = sum(p.olr_wm2 for p in forecast[:7]) / max(1, len(forecast[:7]))
        avg_fc_wind = sum(p.zonal_wind_850hpa_ms for p in forecast[:7]) / max(1, len(forecast[:7]))

        if avg_fc_olr > 235.0 and avg_fc_wind < 5.5:
            trough_status = "Foot-hills of Himalayas (Classic Break Synoptic Pattern)"
            break_prob = min(98.0, 50.0 + (max_consecutive_dry * 5.0))
        elif avg_fc_olr > 215.0 or max_consecutive_dry >= 5:
            trough_status = "Weakened & Diffuse Monsoon Trough"
            break_prob = min(80.0, 35.0 + (max_consecutive_dry * 4.5))
        else:
            trough_status = "Normal (Gangetic Plain & Central India Corridor)"
            break_prob = max(10.0, 20.0 - (total_forecast_rain * 0.5))

        # Risk Classification
        if break_prob >= 75.0 or max_consecutive_dry >= 7:
            risk_level = BreakSpellRiskLevel.CRITICAL
            is_break_active = True
            depletion_rate = "Rapid (3.5% to 5.0% loss/day) due to high solar radiation & VPD"
        elif break_prob >= 50.0 or max_consecutive_dry >= 4:
            risk_level = BreakSpellRiskLevel.HIGH
            is_break_active = (max_consecutive_dry >= 5)
            depletion_rate = "Moderate (2.0% to 3.0% loss/day)"
        elif break_prob >= 30.0:
            risk_level = BreakSpellRiskLevel.MODERATE
            is_break_active = False
            depletion_rate = "Gradual (1.0% to 1.8% loss/day)"
        else:
            risk_level = BreakSpellRiskLevel.LOW
            is_break_active = False
            depletion_rate = "Sustained / Stable Soil Moisture Recharge"

        # Protective Agronomic Measures
        protective_measures = []
        if risk_level in [BreakSpellRiskLevel.HIGH, BreakSpellRiskLevel.CRITICAL]:
            protective_measures.extend([
                "Apply organic straw/crop-residue mulch to conserve critical root-zone soil moisture.",
                "Provide protective life-saving irrigation using micro-sprinklers or drip systems during evening hours.",
                "AVOID top-dressing of urea/nitrogen fertilizer during dry spell to prevent physiological leaf scorch.",
                "Spray 2% Potassium Nitrate (KNO3) or 1% Urea solution as foliar spray to alleviate crop moisture stress.",
                "Conduct shallow intercultural operations (hoeing) to create a soil dust-mulch and break soil capillaries."
            ])
        elif risk_level == BreakSpellRiskLevel.MODERATE:
            protective_measures.extend([
                "Prepare field farm ponds and rainwater harvesting structures for supplemental irrigation.",
                "Ensure weed removal to eliminate competition for limited soil moisture reserves.",
                "Monitor for sucking pests (aphids, thrips, jassids) which proliferate during dry spells."
            ])
        else:
            protective_measures.extend([
                "Maintain adequate drainage channels to prevent waterlogging in low-lying clay soil fields.",
                "Proceed with scheduled fertilizer application following uniform rainfall events."
            ])

        return BreakSpellForecastResponse(
            location=location,
            risk_level=risk_level,
            break_probability_pct=round(break_prob, 1),
            is_break_active=is_break_active,
            estimated_dry_spell_days=max_consecutive_dry,
            trough_position_anomaly=trough_status,
            rainfall_deficit_pct=round(deficit_pct, 1),
            soil_moisture_depletion_rate=depletion_rate,
            forecast_timeline=timeline,
            protective_measures=protective_measures
        )

break_engine = BreakSpellForecastingEngine()
