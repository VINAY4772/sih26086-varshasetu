import pytest
from forecasting.predict import pipeline
from forecasting.evaluate import get_model_evaluation_report

def test_forecast_pipeline_horizons():
    for horizon in [7, 14, 21, 30]:
        fc = pipeline.generate_forecast("tel_wgl_dharmasagar", horizon_days=horizon)
        assert fc["forecast_horizon_days"] == horizon
        assert "onset_outlook" in fc
        assert "break_spell_outlook" in fc
        assert "rainfall_anomaly_outlook" in fc
        assert "heavy_rainfall_risk" in fc
        assert len(fc["timeline"]) == horizon

def test_probabilities_between_zero_and_one():
    fc = pipeline.generate_forecast("mh_amr_chandur", horizon_days=14, scenario="break_spell")
    onset_conf = fc["onset_outlook"]["confidence_score"]
    break_prob = fc["break_spell_outlook"]["probability"]

    assert 0.0 <= onset_conf <= 1.0
    assert 0.0 <= break_prob <= 1.0
    assert fc["break_spell_outlook"]["risk_level"] in ["HIGH", "CRITICAL"]

def test_model_evaluation_report_structure():
    report = get_model_evaluation_report()
    assert report["status"] == "VALIDATED"
    metrics = report["metrics"]
    assert "brier_score" in metrics
    assert "brier_skill_score" in metrics
    assert "roc_auc" in metrics
    assert metrics["brier_skill_score"] > 0.0  # Positive skill over climatology
