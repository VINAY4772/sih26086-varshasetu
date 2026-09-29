"""
Offline Mocked Tests for Real Data Connectors: SIH26086
Verifies that real_data_connectors parser and error handling operate correctly
without relying on active internet connectivity.
"""

import pytest
from unittest.mock import patch, MagicMock
import io
import json
from forecasting.real_data_connectors import fetch_noaa_cpc_oni, fetch_nasa_power_daily

SAMPLE_NOAA_ASCII = """ YR   MON  NINO1+2  ANOM   NINO3    ANOM   NINO4    ANOM   NINO3.4  ANOM
2024   5   24.28    0.02   26.92   -0.23   29.01    0.26   27.66   -0.15
2024   6   22.43   -0.58   25.93   -0.57   29.09    0.30   27.39   -0.20
JJA 2024  28.50  0.45
"""

SAMPLE_NASA_JSON = json.dumps({
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [80.64, 16.24, 14.01]},
    "properties": {
        "parameter": {
            "PRECTOTCORR": {"20240801": 3.88, "20240802": -999.0},
            "T2M_MAX": {"20240801": 31.0, "20240802": 32.1},
            "RH2M": {"20240801": 84.3, "20240802": 79.1}
        }
    }
}).encode("utf-8")

def test_fetch_noaa_cpc_oni_mocked_success():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = SAMPLE_NOAA_ASCII.encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = fetch_noaa_cpc_oni()
        assert res["status"] == "LIVE_VERIFIED"
        assert res["season"] == "JJA"
        assert res["year"] == 2024
        assert res["sst_deg_c"] == 28.50
        assert res["nino34_anomaly_c"] == 0.45
        assert res["is_synthetic"] is False

def test_fetch_noaa_cpc_oni_mocked_network_failure():
    with patch("urllib.request.urlopen", side_effect=Exception("Connection timed out")):
        res = fetch_noaa_cpc_oni()
        assert res["status"] == "UNAVAILABLE"
        assert res["fallback_used"] is True
        assert res["nino34_anomaly_c"] == 0.25
        assert "fallback" in res["provenance_note"].lower()

def test_fetch_nasa_power_daily_mocked_success_with_missing_value_handling():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = SAMPLE_NASA_JSON
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = fetch_nasa_power_daily(16.24, 80.64, "20240801", "20240802")
        assert res["status"] == "LIVE_VERIFIED"
        assert res["record_count"] == 2
        records = res["records"]
        # Day 1: valid 3.88 mm
        assert records[0]["date"] == "2024-08-01"
        assert records[0]["rainfall_mm"] == 3.88
        # Day 2: -999 missing value correctly clamped to 0.0 mm
        assert records[1]["date"] == "2024-08-02"
        assert records[1]["rainfall_mm"] == 0.0

def test_fetch_nasa_power_daily_mocked_failure():
    with patch("urllib.request.urlopen", side_effect=Exception("HTTP 500 Internal Error")):
        res = fetch_nasa_power_daily(16.24, 80.64, "20240801", "20240802")
        assert res["status"] == "UNAVAILABLE"
        assert res["records"] == []
