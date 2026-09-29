import pytest
from forecasting.event_definitions import MeteorologicalEventDetector, EventThresholdConfig

def test_onset_criteria_satisfied():
    detector = MeteorologicalEventDetector()
    # 2 consecutive days >= 2.5mm with strong westerly wind and low OLR
    res = detector.evaluate_onset_criteria(
        recent_daily_rainfall=[12.0, 18.5],
        zonal_wind_850hpa_ms=10.5,
        olr_wm2=185.0
    )
    assert res["onset_detected"] is True
    assert res["status"] == "ONSET_DECLARED"
    assert res["confidence_score"] > 0.85

def test_false_onset_detection():
    detector = MeteorologicalEventDetector()
    # 2 days of rain, but weak westerly jet (pre-monsoon convective shower)
    res = detector.evaluate_onset_criteria(
        recent_daily_rainfall=[15.0, 20.0],
        zonal_wind_850hpa_ms=3.5,  # Weak wind!
        olr_wm2=235.0             # High OLR!
    )
    assert res["onset_detected"] is False
    assert res["status"] == "FALSE_ONSET_WARNING"
    assert res["is_false_alarm"] is True

def test_break_spell_critical_detection():
    detector = MeteorologicalEventDetector()
    # 8 consecutive dry days (< 2.0 mm)
    dry_series = [0.0, 0.5, 0.0, 0.0, 1.2, 0.0, 0.2, 0.0]
    res = detector.detect_break_spells(dry_series)
    assert res["is_break_active"] is True
    assert res["risk_level"] == "CRITICAL"
    assert res["max_consecutive_dry_days"] == 8
    assert res["break_probability"] >= 0.85

def test_rainfall_anomaly_categories():
    detector = MeteorologicalEventDetector()
    # Normal: 7.5mm * 10 days = 75mm
    # Observed: 150mm (+100% => Large Excess)
    res_excess = detector.compute_rainfall_anomaly(150.0, period_days=10)
    assert res_excess["category"] == "Large Excess"
    assert res_excess["departure_percentage"] == 100.0

    # Deficient: 30mm (-60% => Large Deficient)
    res_def = detector.compute_rainfall_anomaly(30.0, period_days=10)
    assert "Deficient" in res_def["category"]

def test_heavy_rainfall_risk_levels():
    detector = MeteorologicalEventDetector()
    res_green = detector.evaluate_heavy_rainfall_risk([5.0, 12.0, 20.0])
    assert res_green["heavy_rainfall_risk"] == "GREEN_NO_HEAVY_RAIN"

    res_heavy = detector.evaluate_heavy_rainfall_risk([5.0, 75.0, 10.0])
    assert res_heavy["heavy_rainfall_risk"] == "YELLOW_ALERT_HEAVY"

    res_extreme = detector.evaluate_heavy_rainfall_risk([5.0, 215.0, 10.0])
    assert res_extreme["heavy_rainfall_risk"] == "RED_ALERT_EXTREME"

def test_climate_drivers_influence():
    detector = MeteorologicalEventDetector()
    # Test El Nino + Negative IOD + MJO Phase 7 (Dry spell enhancement)
    res_dry = detector.evaluate_climate_drivers_influence(
        enso_nino34=1.2,
        iod_dmi=-0.5,
        mjo_phase=7,
        mjo_amplitude=1.5
    )
    assert res_dry["enso"]["phase"] == "El Niño"
    assert res_dry["iod"]["phase"] == "Negative IOD"
    assert "Suppressed" in res_dry["mjo"]["status"]
    assert res_dry["net_break_risk_modifier"] > 0.0

    # Test La Nina + Positive IOD + MJO Phase 3 (Monsoon active revival)
    res_wet = detector.evaluate_climate_drivers_influence(
        enso_nino34=-1.0,
        iod_dmi=0.6,
        mjo_phase=3,
        mjo_amplitude=1.4
    )
    assert res_wet["enso"]["phase"] == "La Niña"
    assert res_wet["iod"]["phase"] == "Positive IOD"
    assert "Active" in res_wet["mjo"]["status"]
    assert res_wet["net_break_risk_modifier"] < 0.0
