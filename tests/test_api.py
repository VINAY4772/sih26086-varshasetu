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
