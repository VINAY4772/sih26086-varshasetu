import pytest
from forecasting.predict import pipeline
from advisories.rules import advisory_rules
from advisories.crop_profiles import CROP_PROFILES

def test_crop_profiles_completeness():
    crops = ["paddy", "cotton", "soybean", "groundnut", "maize", "pulses"]
    for c in crops:
        assert c in CROP_PROFILES
        profile = CROP_PROFILES[c]
        assert "min_sowing_rainfall_mm" in profile
        assert "optimal_soil_moisture_pct" in profile
        assert "authority_source" in profile
        assert len(profile["name_te"]) > 0

def test_advisory_sowing_rules_onset():
    fc = pipeline.generate_forecast("tel_wgl_dharmasagar", horizon_days=14, scenario="onset_active")
    advisories = advisory_rules.generate_all_crop_advisories(fc, language="en")
    assert len(advisories) == 6
    paddy = next(a for a in advisories if a["crop_code"] == "paddy")
    assert "OPTIMAL" in paddy["sowing_status"]
    assert "ICAR" in paddy["guidance_source"]

def test_advisory_break_spell_suppression():
    fc = pipeline.generate_forecast("mh_amr_chandur", horizon_days=14, scenario="break_spell")
    advisories = advisory_rules.generate_all_crop_advisories(fc, language="en")
    cotton = next(a for a in advisories if a["crop_code"] == "cotton")
    assert "POSTPONE" in cotton["sowing_status"]
    assert "SUSPEND" in cotton["fertilizer_advice"]

def test_advisory_telugu_language():
    fc = pipeline.generate_forecast("tel_wgl_dharmasagar", horizon_days=14, scenario="onset_active")
    advisories_te = advisory_rules.generate_all_crop_advisories(fc, language="te")
    paddy_te = next(a for a in advisories_te if a["crop_code"] == "paddy")
    assert "వరి" in paddy_te["crop_name"]
    assert "విత్తుకోండి" in paddy_te["priority_action"]
