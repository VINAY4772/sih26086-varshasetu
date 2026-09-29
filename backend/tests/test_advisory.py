from app.services.weather_service import weather_service
from app.forecasting.onset_model import onset_engine
from app.forecasting.break_model import break_engine
from app.services.advisory_service import advisory_engine
from app.services.i18n_service import i18n_service
from app.models.schemas import SowingSuitability

def test_sowing_recommendation_onset_active():
    loc = weather_service.get_location_by_id("tel_wgl_dharmasagar")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="onset_active")
    onset_fc = onset_engine.predict_onset(loc, data["history"], data["forecast"])
    break_fc = break_engine.predict_break_spell(loc, data["history"], data["forecast"])
    
    advisory = advisory_engine.generate_advisories(loc, onset_fc, break_fc, language="en")
    assert advisory.alert_level in ["Green", "Yellow"]
    assert len(advisory.crop_advisories) >= 4
    
    paddy_advisory = next(c for c in advisory.crop_advisories if c.crop_code == "paddy")
    assert paddy_advisory.sowing_status == SowingSuitability.OPTIMAL
    assert "nursery" in paddy_advisory.action_item.lower()

def test_sowing_recommendation_break_spell():
    loc = weather_service.get_location_by_id("mh_amr_chandur")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="break_spell")
    onset_fc = onset_engine.predict_onset(loc, data["history"], data["forecast"])
    break_fc = break_engine.predict_break_spell(loc, data["history"], data["forecast"])
    
    advisory = advisory_engine.generate_advisories(loc, onset_fc, break_fc, language="en")
    assert advisory.alert_level in ["Orange", "Red"]
    cotton_advisory = next(c for c in advisory.crop_advisories if c.crop_code == "cotton")
    assert cotton_advisory.sowing_status == SowingSuitability.HIGH_RISK_DRY
    assert "SUSPEND" in cotton_advisory.fertilizer_advice

def test_multilingual_advisories():
    loc = weather_service.get_location_by_id("tel_wgl_dharmasagar")
    data = weather_service.get_hyperlocal_weather_history_and_forecast(loc, scenario="onset_active")
    onset_fc = onset_engine.predict_onset(loc, data["history"], data["forecast"])
    break_fc = break_engine.predict_break_spell(loc, data["history"], data["forecast"])
    base = advisory_engine.generate_advisories(loc, onset_fc, break_fc, language="en")
    
    # Test Telugu
    te_adv = i18n_service.localize_advisory(base, target_lang="te")
    assert te_adv.language == "te"
    assert any("వరి" in c.crop_name for c in te_adv.crop_advisories)
    
    # Test Hindi
    hi_adv = i18n_service.localize_advisory(base, target_lang="hi")
    assert hi_adv.language == "hi"
    assert any("धान" in c.crop_name for c in hi_adv.crop_advisories)
