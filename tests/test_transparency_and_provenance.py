"""
Transparency, Provenance, and Disclaimers Verification Suite: SIH26086
Verifies that all demonstration forecasts, synthetic metrics, approximate polygons,
and climate index provenance labels are explicitly disclosed.
"""

import pytest
from app import create_app
from forecasting.predict import pipeline
from forecasting.evaluate import get_model_evaluation_report
from forecasting.real_data_connectors import fetch_noaa_cpc_oni, fetch_nasa_power_daily

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_forecast_demonstration_disclaimers():
    fc = pipeline.generate_forecast("ap_gnr_tenali", horizon_days=14)
    assert fc["is_demonstration"] is True
    assert fc["disclaimer"] == "DEMONSTRATION FORECAST — NOT FOR AGRICULTURAL DECISIONS"
    assert "accuracy_notice" in fc
    assert "uncertainty_type" in fc["horizon_metadata"]
    assert fc["horizon_metadata"]["is_empirically_calibrated"] is False
    assert "provisional" in fc["horizon_metadata"]["disclaimer"].lower()

def test_climate_drivers_provenance_labels():
    fc = pipeline.generate_forecast("mh_amr_chandur", horizon_days=7)
    cd = fc["climate_drivers"]
    assert "enso" in cd
    assert "source_status" in cd["enso"]
    assert "provenance_note" in cd["enso"]
    assert cd["enso"]["source_status"] in ["LIVE_VERIFIED_NOAA_CPC", "CONFIGURED_BENCHMARK"]

    assert "iod" in cd
    assert cd["iod"]["source_status"] == "CONFIGURED_BENCHMARK"
    assert "restricted" in cd["iod"]["provenance_note"].lower() or "configured" in cd["iod"]["provenance_note"].lower()

    assert "mjo" in cd
    assert cd["mjo"]["source_status"] == "CONFIGURED_BENCHMARK"

def test_risk_map_demonstration_provenance(client):
    res = client.get("/api/risk-map")
    assert res.status_code == 200
    data = res.get_json()
    assert data["map_type"] == "DEMONSTRATION_RISK_MAP"
    assert "DEMONSTRATION ONLY" in data["disclaimer"]
    assert "isochrones_provenance" in data
    assert "radar_provenance" in data
    assert "polygons_provenance" in data

    polygons = data.get("block_polygons")
    assert polygons is not None
    for feature in polygons["features"]:
        assert "Approximate Demonstration Geometry" in feature["properties"]["data_provenance"]

def test_model_info_synthetic_accuracy_disclaimer(client):
    res = client.get("/api/model-info")
    assert res.status_code == 200
    data = res.get_json()
    assert "SYNTHETIC" in data["validation_dataset"]
    assert data["real_world_validation"] is False
    assert "scientific_interpretation" in data
    assert "synthetic" in data["scientific_interpretation"].lower()

def test_real_data_connectors_structure():
    """
    LIVE NETWORK INTEGRATION TEST:
    Explicitly probes active NOAA CPC and NASA POWER public servers over HTTPS
    to verify live internet connectivity and production endpoint availability.
    (For offline unit tests with mocked responses, see tests/test_connectors_mocked.py)
    """
    # Verify NOAA ONI connector schema
    noaa_res = fetch_noaa_cpc_oni(timeout_sec=3)
    assert isinstance(noaa_res, dict)
    assert "status" in noaa_res
    assert noaa_res["is_synthetic"] is False

    # Verify NASA POWER connector schema
    nasa_res = fetch_nasa_power_daily(16.24, 80.64, "20240801", "20240802", timeout_sec=4)
    assert isinstance(nasa_res, dict)
    assert "status" in nasa_res
    assert nasa_res["is_synthetic"] is False
