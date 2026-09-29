from app.services.weather_service import weather_service
from app.forecasting.onset_model import onset_engine
from app.forecasting.break_model import break_engine
from app.models.schemas import MonsoonPhase, BreakSpellRiskLevel

def test_onset_detection_active_scenario():
    loc = weather_service.get_location_by_id("tel_wgl_dharmasagar")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="onset_active")
    
    result = onset_engine.predict_onset(loc, data["history"], data["forecast"])
    assert result.current_phase in [MonsoonPhase.ONSET_ACTIVE, MonsoonPhase.ONSET_WATCH]
    assert result.criteria.rainfall_threshold_met is True
    assert result.confidence_score > 70.0

def test_false_onset_warning_premonsoon():
    loc = weather_service.get_location_by_id("mh_ltr_ausa")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="pre_monsoon")
    
    result = onset_engine.predict_onset(loc, data["history"], data["forecast"])
    # Should identify pre-monsoon stage or flag false onset warning
    assert result.current_phase == MonsoonPhase.PRE_MONSOON
    assert any("FALSE ONSET" in s or "Pre-Monsoon" in s for s in result.synoptic_features)

def test_break_spell_prediction_scenario():
    loc = weather_service.get_location_by_id("mh_amr_chandur")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="break_spell")
    
    result = break_engine.predict_break_spell(loc, data["history"], data["forecast"])
    assert result.risk_level in [BreakSpellRiskLevel.HIGH, BreakSpellRiskLevel.CRITICAL]
    assert result.break_probability_pct >= 50.0
    assert result.estimated_dry_spell_days >= 3
    assert len(result.protective_measures) >= 3
