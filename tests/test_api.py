import pytest
import io
import json
from app import create_app
from database.initialise import initialise_database

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True

def test_api_locations(client):
    res = client.get("/api/locations")
    assert res.status_code == 200
    locations = res.get_json()
    assert len(locations) >= 8

def test_api_locations_filter(client):
    res = client.get("/api/locations?q=Tenali")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["district"] == "Guntur"

def test_api_forecast(client):
    res = client.get("/api/forecast?location_id=tel_wgl_dharmasagar&horizon=14")
    assert res.status_code == 200
    data = res.get_json()
    assert data["forecast_horizon_days"] == 14
    assert "break_spell_outlook" in data
    assert "onset_outlook" in data

def test_api_forecast_invalid_horizon(client):
    res = client.get("/api/forecast?location_id=tel_wgl_dharmasagar&horizon=45")
    assert res.status_code == 400
    assert "Invalid horizon" in res.get_json()["error"]

def test_api_risk_map(client):
    res = client.get("/api/risk-map")
    assert res.status_code == 200
    data = res.get_json()
    assert "isochrones" in data
    assert "radar_grid" in data
    assert "locations" in data

def test_api_rainfall_history(client):
    res = client.get("/api/rainfall-history?location_id=tel_wgl_dharmasagar&limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["location_id"] == "tel_wgl_dharmasagar"
    assert len(data["history"]) > 0

def test_api_advisories_multilingual(client):
    # English
    res_en = client.get("/api/advisories?location_id=tel_wgl_dharmasagar&lang=en")
    assert res_en.status_code == 200
    data_en = res_en.get_json()
    assert data_en["language"] == "en"

    # Telugu
    res_te = client.get("/api/advisories?location_id=tel_wgl_dharmasagar&lang=te")
    assert res_te.status_code == 200
    data_te = res_te.get_json()
    assert data_te["language"] == "te"
    assert any("వరి" in a["crop_name"] for a in data_te["advisories"])

def test_api_model_info(client):
    res = client.get("/api/model-info")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "VALIDATED"
    assert "brier_score" in data["metrics"]

def test_api_data_sources(client):
    res = client.get("/api/data-sources")
    assert res.status_code == 200
    sources = res.get_json()
    assert len(sources) >= 4

def test_api_file_upload_security(client):
    # Test uploading an invalid file extension (e.g. .exe)
    data = {
        "file": (io.BytesIO(b"malicious script"), "payload.exe")
    }
    res = client.post("/api/data/upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "Only CSV files are allowed" in res.get_json()["error"]

def test_api_notification_simulate(client):
    payload = {
        "phone": "+91-9876543210",
        "channel": "sms",
        "message": "Monsoon alert test"
    }
    res = client.post(
        "/api/notifications/simulate",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SIMULATED_SUCCESS"
    assert "XXXX" in data["recipient_mask"]

def test_api_locations_marker_coordinates_and_schema(client):
    res = client.get("/api/locations")
    assert res.status_code == 200
    locations = res.get_json()
    assert isinstance(locations, list)
    assert len(locations) >= 8

    required_keys = {"id", "name", "block_or_mandal", "district", "state", "latitude", "longitude"}
    for loc in locations:
        assert required_keys.issubset(loc.keys()), f"Missing keys in location: {loc}"
        lat = loc["latitude"]
        lon = loc["longitude"]
        assert isinstance(lat, (int, float)), f"Invalid latitude type in {loc['id']}"
        assert isinstance(lon, (int, float)), f"Invalid longitude type in {loc['id']}"
        # Indian subcontinent bounds
        assert 8.0 <= lat <= 37.0, f"Latitude {lat} out of range for {loc['id']}"
        assert 68.0 <= lon <= 98.0, f"Longitude {lon} out of range for {loc['id']}"

def test_api_risk_map_layers_schema(client):
    res = client.get("/api/risk-map")
    assert res.status_code == 200
    data = res.get_json()
    assert "isochrones" in data
    assert "radar_grid" in data
    assert "block_polygons" in data
    assert "locations" in data

    # Verify isochrones GeoJSON features
    isochrones = data["isochrones"]
    assert isochrones.get("type") == "FeatureCollection"
    assert len(isochrones.get("features", [])) > 0

    # Verify radar grid points
    radar_grid = data["radar_grid"]
    assert isinstance(radar_grid, list)
    assert len(radar_grid) > 0
    for pt in radar_grid:
        assert "lat" in pt and "lon" in pt and "intensity_mm_hr" in pt
        assert 8.0 <= pt["lat"] <= 37.0
        assert 68.0 <= pt["lon"] <= 98.0
        assert pt["intensity_mm_hr"] >= 0.0
