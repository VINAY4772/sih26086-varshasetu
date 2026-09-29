from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SIH26086" in data["service"]

def test_locations_list():
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    locations = response.json()
    assert len(locations) >= 5
    first = locations[0]
    assert "block" in first
    assert "district" in first
    assert "state" in first

def test_locations_search_filter():
    response = client.get("/api/v1/locations?q=Warangal")
    assert response.status_code == 200
    locations = response.json()
    assert len(locations) >= 1
    assert "Warangal" in locations[0]["district"]

def test_onset_forecast_endpoint():
    response = client.get("/api/v1/forecast/onset?location_id=tel_wgl_dharmasagar")
    assert response.status_code == 200
    data = response.json()
    assert "current_phase" in data
    assert "criteria" in data
    assert "confidence_score" in data
    assert data["location"]["block"] == "Dharmasagar"

def test_break_forecast_endpoint():
    response = client.get("/api/v1/forecast/break?location_id=mh_amr_chandur&scenario=break_spell")
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["high", "critical", "moderate", "low"]
    assert "break_probability_pct" in data
    assert len(data["protective_measures"]) > 0

def test_advisory_multilingual_endpoint():
    for lang in ["en", "hi", "te", "mr"]:
        response = client.get(f"/api/v1/advisory?location_id=tel_wgl_dharmasagar&lang={lang}")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == lang
        assert len(data["crop_advisories"]) >= 4

def test_gis_isochrones_endpoint():
    response = client.get("/api/v1/gis/isochrones")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 4

def test_gis_radar_endpoint():
    response = client.get("/api/v1/gis/rainfall-radar")
    assert response.status_code == 200
    grid = response.json()
    assert len(grid) > 0
    assert "intensity_mm_hr" in grid[0]
