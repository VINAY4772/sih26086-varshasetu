"""
Historical Real Weather Data Collector: SIH26086
Retrieves multi-year real gridded meteorological data from NASA POWER Agroclimatology
for the Tenali, Andhra Pradesh demonstration coordinates (2015–2025).

Scientific Constraints & Data Integrity:
1. Distinguishes gridded satellite-reanalysis estimates from direct ground rain-gauges.
2. Does NOT silently convert missing values (-999.0) into genuine 0.0 mm rainfall.
3. Preserves the existing synthetic benchmark in data/sample/ without modification.
4. Stores real data in data/real/ with complete audit metadata.
"""

import urllib.request
import json
import datetime
import ssl
from pathlib import Path
from typing import Dict, Any, List, Optional
import csv
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl.create_default_context()

NASA_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def collect_tenali_historical_data(
    start_date: str = "20150101",
    end_date: str = "20251231",
    latitude: float = 16.2437,
    longitude: float = 80.6400,
    output_dir: Optional[Path] = None,
    timeout_sec: int = 45
) -> Dict[str, Any]:
    """
    Retrieves and validates multi-year daily meteorological data for Tenali, AP.
    Returns:
        Dict with validation metrics, coverage, and record counts.
    """
    output_dir = output_dir or (Config.DATA_DIR / "real")
    output_dir.mkdir(parents=True, exist_ok=True)

    url = (
        f"{NASA_POWER_API_URL}?parameters=PRECTOTCORR,T2M_MAX,RH2M"
        f"&community=AG&longitude={longitude:.4f}&latitude={latitude:.4f}"
        f"&start={start_date}&end={end_date}&format=JSON"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SIH26086-AgroMet-Research/1.0 (MoES SIH Hackathon)"}
    )

    retrieval_time = datetime.datetime.now().isoformat()
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec, context=SSL_CONTEXT) as response:
            if response.status != 200:
                return {
                    "status": "HTTP_ERROR",
                    "http_code": response.status,
                    "message": f"NASA POWER server returned non-200 status: {response.status}",
                    "records_collected": 0
                }
            raw_data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {
            "status": "NETWORK_ERROR",
            "error": str(e),
            "message": f"Failed to retrieve data from NASA POWER API: {str(e)}",
            "records_collected": 0
        }

    # Extract time series parameter dictionaries
    params = raw_data.get("properties", {}).get("parameter", {})
    rain_dict = params.get("PRECTOTCORR", {})
    tmax_dict = params.get("T2M_MAX", {})
    rh_dict = params.get("RH2M", {})

    all_dates = sorted(rain_dict.keys())
    if not all_dates:
        return {
            "status": "EMPTY_PAYLOAD",
            "message": "NASA POWER returned zero date records for requested range.",
            "records_collected": 0
        }

    # Validation counters
    records = []
    seen_dates = set()
    duplicate_dates = []
    missing_rain_count = 0
    missing_tmax_count = 0
    missing_rh_count = 0

    for d_str in all_dates:
        # Check duplicate
        if d_str in seen_dates:
            duplicate_dates.append(d_str)
        seen_dates.add(d_str)

        iso_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:]}"

        raw_rain = rain_dict.get(d_str)
        raw_tmax = tmax_dict.get(d_str)
        raw_rh = rh_dict.get(d_str)

        # Explicit sentinel (-999.0) detection: Do NOT convert missing to 0.0 mm!
        is_rain_missing = (raw_rain is None or raw_rain == -999.0 or raw_rain == -999)
        is_tmax_missing = (raw_tmax is None or raw_tmax == -999.0 or raw_tmax == -999)
        is_rh_missing = (raw_rh is None or raw_rh == -999.0 or raw_rh == -999)

        if is_rain_missing:
            missing_rain_count += 1
            rain_val = None
        else:
            rain_val = round(max(0.0, float(raw_rain)), 2)

        if is_tmax_missing:
            missing_tmax_count += 1
            tmax_val = None
        else:
            tmax_val = round(float(raw_tmax), 1)

        if is_rh_missing:
            missing_rh_count += 1
            rh_val = None
        else:
            rh_val = round(float(raw_rh), 1)

        is_any_missing = is_rain_missing or is_tmax_missing or is_rh_missing

        records.append({
            "location_id": "ap_gnr_tenali",
            "date": iso_date,
            "rainfall_mm": rain_val,
            "temp_max_c": tmax_val,
            "humidity_pct": rh_val,
            "missing_flag": is_any_missing,
            "data_source_id": "nasa_power_daily"
        })

    # Temporal continuity check (check for date gaps)
    start_dt = datetime.date(int(all_dates[0][:4]), int(all_dates[0][4:6]), int(all_dates[0][6:]))
    end_dt = datetime.date(int(all_dates[-1][:4]), int(all_dates[-1][4:6]), int(all_dates[-1][6:]))
    expected_days = (end_dt - start_dt).days + 1
    actual_days = len(records)
    gaps_count = expected_days - actual_days

    # Construct complete JSON document
    json_doc = {
        "metadata": {
            "dataset_name": "Tenali Mandal Multi-Year Real Weather Archive (NASA POWER)",
            "location_id": "ap_gnr_tenali",
            "location_name": "Angalakuduru Village, Tenali Mandal",
            "district": "Guntur",
            "state": "Andhra Pradesh",
            "latitude": latitude,
            "longitude": longitude,
            "requested_range": {"start": start_date, "end": end_date},
            "returned_range": {"start": records[0]["date"], "end": records[-1]["date"]},
            "retrieval_timestamp": retrieval_time,
            "source_url": url,
            "data_source_id": "nasa_power_daily",
            "is_synthetic": False,
            "scientific_nature": (
                "Areal gridded assimilation estimate (0.5° x 0.5° resolution, ~50km) "
                "from NASA Goddard Earth Observing System (GEOS-5) and satellite precipitation analyses. "
                "NOT an in-situ ground rain-gauge observation."
            ),
            "units": {
                "rainfall_mm": "mm/day (PRECTOTCORR)",
                "temp_max_c": "degrees Celsius (T2M_MAX)",
                "humidity_pct": "percent (RH2M)"
            },
            "validation_summary": {
                "total_records": actual_days,
                "expected_calendar_days": expected_days,
                "temporal_gaps": gaps_count,
                "duplicate_dates": len(duplicate_dates),
                "missing_rain_days": missing_rain_count,
                "missing_tmax_days": missing_tmax_count,
                "missing_rh_days": missing_rh_count
            }
        },
        "records": records
    }

    # Save to JSON
    json_path = output_dir / "tenali_nasa_power_2015_2025.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_doc, f, indent=2)

    # Save to CSV for tabular modeling pipelines
    csv_path = output_dir / "tenali_nasa_power_2015_2025.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["location_id", "date", "rainfall_mm", "temp_max_c", "humidity_pct", "missing_flag", "data_source_id"])
        for r in records:
            writer.writerow([
                r["location_id"],
                r["date"],
                "" if r["rainfall_mm"] is None else r["rainfall_mm"],
                "" if r["temp_max_c"] is None else r["temp_max_c"],
                "" if r["humidity_pct"] is None else r["humidity_pct"],
                int(r["missing_flag"]),
                r["data_source_id"]
            ])

    return {
        "status": "SUCCESS",
        "json_path": str(json_path),
        "csv_path": str(csv_path),
        "validation_summary": json_doc["metadata"]["validation_summary"],
        "returned_range": json_doc["metadata"]["returned_range"]
    }

if __name__ == "__main__":
    res = collect_tenali_historical_data()
    print("Historical Real Weather Data Collection Result:")
    print(json.dumps(res, indent=2))
