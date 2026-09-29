import datetime
from typing import List
from ..models.schemas import (
    Location,
    OnsetForecastResponse,
    BreakSpellForecastResponse,
    CropAdvisory,
    FullAdvisoryResponse,
    SowingSuitability,
    BreakSpellRiskLevel
)

class AgriculturalAdvisoryEngine:
    """
    Expert Agronomic Advisory Decision Engine.
    Correlates IMD onset parameters, break spell probability, and soil moisture
    to deliver hyperlocal actionable crop advice for Indian Kharif farmers.
    """

    SUPPORTED_CROPS = [
        {"code": "paddy", "name": "Paddy / Rice (धान / వరి)"},
        {"code": "cotton", "name": "Cotton (कपास / పత్తి)"},
        {"code": "soybean", "name": "Soybean (सोयाबीन / సోయాబీన్)"},
        {"code": "groundnut", "name": "Groundnut (मूंगफली / వేరుశనగ)"},
        {"code": "maize", "name": "Maize / Corn (मक्का / మొక్కజొన్న)"},
        {"code": "pulses", "name": "Redgram / Pigeonpea (अरहर / కంది)"}
    ]

    def generate_advisories(
        self,
        location: Location,
        onset_forecast: OnsetForecastResponse,
        break_forecast: BreakSpellForecastResponse,
        language: str = "en"
    ) -> FullAdvisoryResponse:
        today = datetime.date.today()
        crop_advisories: List[CropAdvisory] = []

        is_break_danger = break_forecast.risk_level in [BreakSpellRiskLevel.HIGH, BreakSpellRiskLevel.CRITICAL]
        is_onset_declared = (onset_forecast.current_phase.value == "onset_active")
        is_onset_watch = (onset_forecast.current_phase.value == "onset_watch")

        # Determine overall alert level
        if is_break_danger:
            alert_level = "Orange" if break_forecast.risk_level == BreakSpellRiskLevel.HIGH else "Red"
            headline = f"⚠️ Monsoon Break Alert: {break_forecast.estimated_dry_spell_days}-Day Dry Spell Projected in {location.block}"
            overall_advice = (
                f"Severe convective lull identified over {location.district}. Conserve existing soil moisture with organic mulch. "
                "Halt chemical nitrogen top-dressing and prepare supplementary irrigation to prevent flower drop."
            )
        elif is_onset_declared:
            alert_level = "Green"
            headline = f"🌧️ Monsoon Onset Active over {location.block}, {location.district}"
            overall_advice = (
                f"Sufficient soil moisture depth achieved in {location.primary_soil}. "
                "Conditions are optimal for main Kharif sowing over the next 4-6 days."
            )
        elif is_onset_watch:
            alert_level = "Yellow"
            headline = f"⏳ Monsoon Onset Expected within 48-72h in {location.block}"
            overall_advice = (
                "Complete summer plowing and finalize seed treatment. Avoid dry sowing until 50-60mm cumulative wetting is confirmed."
            )
        else:
            alert_level = "Green"
            headline = f"☀️ Pre-Monsoon Field Preparation Phase in {location.block}"
            overall_advice = (
                "Procure certified seeds from authorized agriculture depots. Treat seeds with Trichoderma viride or Rhizobium."
            )

        # Generate individual crop advisories
        for crop in self.SUPPORTED_CROPS:
            advisory = self._evaluate_crop(
                crop=crop,
                location=location,
                is_onset_declared=is_onset_declared,
                is_onset_watch=is_onset_watch,
                is_break_danger=is_break_danger,
                break_forecast=break_forecast,
                today=today
            )
            crop_advisories.append(advisory)

        return FullAdvisoryResponse(
            location=location,
            language=language,
            generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            monsoon_headline=headline,
            overall_advice=overall_advice,
            crop_advisories=crop_advisories,
            alert_level=alert_level
        )

    def _evaluate_crop(
        self,
        crop: dict,
        location: Location,
        is_onset_declared: bool,
        is_onset_watch: bool,
        is_break_danger: bool,
        break_forecast: BreakSpellForecastResponse,
        today: datetime.date
    ) -> CropAdvisory:
        code = crop["code"]
        name = crop["name"]

        if is_break_danger:
            sowing_status = SowingSuitability.HIGH_RISK_DRY
            sowing_window = "Postpone New Sowing until Break Spell Concludes"
            soil_moist = "Deficit - High Evapotranspiration Loss"
            irrig = "Provide life-saving light irrigation in evening hours; utilize farm pond / micro-drip."
            fert = "STRICTLY SUSPEND urea top dressing; spray 1.5% KNO3 (potassium nitrate) to boost drought resilience."
            pest = "Scout for red spider mites, thrips, and aphids thriving in hot, dry conditions."
            action = f"Apply paddy straw or bagasse mulch (5 t/ha) across {name} rows to suppress evaporation."

        elif is_onset_declared:
            sowing_status = SowingSuitability.OPTIMAL
            sowing_window = f"{today.strftime('%d %b')} – {(today + datetime.timedelta(days=7)).strftime('%d %b')}"
            soil_moist = "Adequate (>65% Field Capacity)"
            irrig = "No supplementary irrigation required; clear field drainage to prevent seedling damping-off."
            fert = "Apply recommended basal dose of SSP (Phosphorus) and Potash (MOP) at 5 cm below seed depth."
            if code == "cotton":
                pest = "Inspect for sucking pest complex; install 5 yellow sticky traps per acre."
                action = "Maintain 90x60 cm or 120x45 cm spacing; treat seeds with Imidacloprid."
            elif code == "soybean":
                pest = "Watch for tobacco caterpillar; spray bio-pesticide Beauveria bassiana if needed."
                action = "Sow across the slope at 30-45 cm row spacing to optimize rainwater retention."
            elif code == "paddy":
                pest = "Watch for seedling blast; treat seeds with Carbendazim (2g/kg)."
                action = "Prepare raised nursery bed; puddle main field 15 days after nursery emergence."
            else:
                pest = "Monitor for early shoot borer and root grubs."
                action = "Complete sowing with certified treated seeds within current moisture window."

        elif is_onset_watch:
            sowing_status = SowingSuitability.FAVORABLE
            sowing_window = f"Window opens within 3-4 days (Expected {(today + datetime.timedelta(days=3)).strftime('%d %b')})"
            soil_moist = "Moderate - Awaiting Deep Soil Wetting"
            irrig = "Keep irrigation systems primed; do not flood fields."
            fert = "Procure basal DAP / SSP and keep dry in weatherproof storage."
            pest = "Perform seed treatment with Trichoderma viride (10g/kg) to prevent soil-borne damping off."
            action = "Keep tract of IMD block alerts; perform final harrow pass when soil is workable."

        else:
            sowing_status = SowingSuitability.WAIT_FOR_MOISTURE
            sowing_window = "Pre-Monsoon (Awaiting Monsoon Ingress)"
            soil_moist = "Dry (<30% Moisture)"
            irrig = "Not applicable for rainfed plots; prepare ridge-and-furrow layout."
            fert = "Incorporate well-decomposed FYM (Farm Yard Manure) @ 8-10 tonnes/ha during deep summer tillage."
            pest = "Solarize nursery beds; remove perennial stubble and weeds harboring resting pupae."
            action = "Order certified seeds; clean field channels; do NOT sow in dry dust."

        return CropAdvisory(
            crop_name=name,
            crop_code=code,
            sowing_status=sowing_status,
            sowing_window=sowing_window,
            soil_moisture_status=soil_moist,
            irrigation_advice=irrig,
            fertilizer_advice=fert,
            pest_disease_watch=pest,
            action_item=action
        )

advisory_engine = AgriculturalAdvisoryEngine()
