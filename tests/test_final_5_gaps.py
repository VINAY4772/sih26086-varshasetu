import json
import pytest
from app import create_app
from forecasting.predict import pipeline as forecast_pipeline
from forecasting.event_definitions import MeteorologicalEventDetector, EventThresholdConfig
from advisories.rules import advisory_rules
from advisories.crop_profiles import CROP_PROFILES

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_gap1_monsoon_onset_thresholds():
    """
    Gap 1: Verify explicit Monsoon Onset Threshold concept, rule definition,
    status (MET, NOT MET, INSUFFICIENT DATA), and expected onset window.
    """
    # 1. Default forecast
    fc = forecast_pipeline.generate_forecast("tel_wgl_dharmasagar", 14)
    onset = fc["onset_outlook"]
    
    assert "threshold_rule" in onset
    assert "IMD-referenced monsoon onset criteria adapted within the VarshaSetu hyperlocal forecasting framework" in onset["threshold_rule"]
    assert "official IMD onset declaration" in onset.get("methodology_note", "")
    assert "threshold_status" in onset
    assert onset["threshold_status"] in ["MET", "NOT MET", "INSUFFICIENT DATA"]
    assert "expected_onset_window" in onset
    assert "onset_probability_pct" in onset
    assert 0.0 <= onset["onset_probability_pct"] <= 100.0

    # 2. Onset Active Scenario (MET)
    fc_active = forecast_pipeline.generate_forecast("tel_wgl_dharmasagar", 14, scenario="onset_active")
    assert fc_active["onset_outlook"]["threshold_status"] == "MET"
    assert "Within 3–5 Days (Imminent)" in fc_active["onset_outlook"]["expected_onset_window"]

    # 3. Insufficient observation days
    detector = MeteorologicalEventDetector()
    res_insufficient = detector.evaluate_onset_criteria(recent_daily_rainfall=[5.0]) # Only 1 day
    assert res_insufficient["threshold_status"] == "INSUFFICIENT DATA"
    assert res_insufficient["status"] == "INSUFFICIENT_OBSERVATION_DAYS"

def test_gap2_active_and_break_duration():
    """
    Gap 2: Verify active monsoon duration and break duration assessments
    with start/end windows and clear distinction from probability.
    """
    # 1. Break spell scenario
    fc_break = forecast_pipeline.generate_forecast("tel_wgl_dharmasagar", 14, scenario="break_spell")
    brk = fc_break["break_spell_outlook"]
    
    assert "expected_break_duration_days" in brk
    assert brk["expected_break_duration_days"] >= 4
    assert "duration_display" in brk
    assert "days" in brk["duration_display"]
    assert "expected_window" in brk
    assert "Day" in brk["expected_window"]
    # Probability must be a distinct float
    assert isinstance(brk["probability"], float)
    assert 0.0 <= brk["probability"] <= 1.0

    # 2. Active spell scenario
    fc_active = forecast_pipeline.generate_forecast("tel_wgl_dharmasagar", 14, scenario="onset_active")
    active = fc_active["active_monsoon_outlook"]
    
    assert "expected_active_duration_days" in active
    assert active["expected_active_duration_days"] >= 3
    assert "duration_display" in active
    assert "days" in active["duration_display"]
    assert "expected_window" in active
    assert "Day" in active["expected_window"]
    assert isinstance(active["probability"], float)
    assert 0.0 <= active["probability"] <= 1.0

def test_gap3_crop_choice_alteration_advisories():
    """
    Gap 3: Verify dedicated CROP CHOICE / VARIETY ALTERNATIVE category,
    5 explicit advisory categories, and alternative crop rules.
    """
    fc_break = forecast_pipeline.generate_forecast("tel_wgl_dharmasagar", 14, scenario="break_spell")
    
    # Test for each crop profile
    for crop_code in ["paddy", "cotton", "soybean", "groundnut", "maize", "pulses"]:
        adv = advisory_rules.generate_crop_advisory(crop_code, fc_break, language="en")
        
        # 5 Explicit advisory categories
        assert "advisory_categories" in adv
        cat_names = [c["category"] for c in adv["advisory_categories"]]
        assert "SOWING" in cat_names
        assert "IRRIGATION" in cat_names
        assert "FERTILIZER" in cat_names
        assert "PEST/WEATHER RISK" in cat_names
        assert "CROP CHOICE" in cat_names
        
        # Crop choice alteration section
        assert "crop_choice_alteration" in adv
        choice = adv["crop_choice_alteration"]
        assert choice["advisory_type"] == "CROP CHOICE"
        assert choice["is_alteration_recommended"] is True
        assert "Delayed onset" in choice["forecast_condition"] or "break" in choice["forecast_condition"].lower()
        assert choice["crop_choice_advisory"] != ""
        assert "Alternative crop recommendation unavailable" not in choice["crop_choice_advisory"]
        assert choice["reason"] != ""
        assert len(choice["recommended_short_duration_varieties"]) > 0

    # Test Telugu language translation
    adv_te = advisory_rules.generate_crop_advisory("paddy", fc_break, language="te")
    assert "ఆలస్యమైన" in adv_te["crop_choice_alteration"]["forecast_condition"]

def test_gap4_farmer_recipient_simulation(client):
    """
    Gap 4: Verify Rural Messaging Gateway with Farmer recipient and SMS/WhatsApp channels.
    """
    for ch in ["sms", "whatsapp"]:
        payload = {
            "recipient_type": "farmer",
            "phone": "+91-9876543210",
            "channel": ch,
            "location_name": "Dharmasagar Village",
            "crop_name": "Paddy / Rice",
            "horizon_days": 14,
            "risk_condition": "Active Southwest Monsoon",
            "action": "Proceed with line sowing using certified seed."
        }
        res = client.post("/api/notifications/simulate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SIMULATED_SUCCESS"
        assert data["delivery_status"] == "DELIVERED (SIMULATED)"
        assert data["recipient_type"] == "farmer"
        assert data["channel"] == ch
        assert "Recipient: Farmer" in data["message"]
        assert "Location: Dharmasagar Village" in data["message"]

def test_gap5_agricultural_extension_officer_simulation(client):
    """
    Gap 5: Verify Agricultural Extension Officer recipient simulation
    with officer-facing directive bulletin for both SMS and WhatsApp.
    """
    for ch in ["sms", "whatsapp"]:
        payload = {
            "recipient_type": "officer",
            "phone": "+91-9123456789",
            "channel": ch,
            "location_name": "Dharmasagar Block / Mandal",
            "crop_name": "Paddy & Cotton",
            "horizon_days": 14,
            "risk_condition": "Elevated prolonged dry-spell probability (64%)",
            "action": "Prepare irrigation contingency; advise farmers regarding delayed sowing / crop alteration."
        }
        res = client.post("/api/notifications/simulate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SIMULATED_SUCCESS"
        assert data["delivery_status"] == "DELIVERED (SIMULATED)"
        assert data["recipient_type"] == "officer"
        assert data["channel"] == ch
        assert "[VarshaSetu AGRI-OFFICER BULLETIN]" in data["message"]
        assert "Recipient: Agricultural Extension Officer" in data["message"]
        assert "Area / Block: Dharmasagar Block / Mandal" in data["message"]
        assert "Mandated Directive:" in data["message"]

def test_notification_audit_history_endpoint(client):
    """
    Verify GET /api/notifications/history returns logged dispatches
    without requiring manual page refresh.
    """
    res = client.get("/api/notifications/history")
    assert res.status_code == 200
    history = res.get_json()
    assert isinstance(history, list)
    assert len(history) > 0
    latest = history[0]
    assert "recipient_type" in latest
    assert "recipient_mask" in latest
    assert "channel" in latest
    assert "status" in latest
