# REST API Specification: SIH26086

Base URL: `http://localhost:5000/api`

---

## 1. System Health
### `GET /api/health`
Returns service availability, server timestamp, and database connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "SIH26086 Flask Backend",
  "database_connected": true,
  "version": "1.0.0",
  "timestamp": "2026-09-29T23:15:00.000000"
}
```

---

## 2. Locations Directory
### `GET /api/locations`
Returns registered agricultural blocks, mandals, and villages.

**Query Parameters:**
- `q` (optional): Filter by name, block, district, or state.

**Response (200 OK):**
```json
[
  {
    "id": "tel_wgl_dharmasagar",
    "name": "Dharmasagar Village",
    "block_or_mandal": "Dharmasagar Mandal",
    "district": "Hanamkonda / Warangal",
    "state": "Telangana",
    "latitude": 17.9944,
    "longitude": 79.4892,
    "elevation_m": 280.0,
    "primary_soil": "Red Sandy Loam & Black Soil",
    "normal_onset_date": "June 08"
  }
]
```

---

## 3. Multi-Horizon Forecast
### `GET /api/forecast`
Generates probabilistic forecast outlook.

**Query Parameters:**
- `location_id` (string, required): e.g., `tel_wgl_dharmasagar`
- `horizon` (integer, optional): `7`, `14`, `21`, or `30` (default: `14`)
- `scenario` (string, optional): `'onset_active'`, `'break_spell'`, `'pre_monsoon'`

**Response (200 OK):**
```json
{
  "location": { "id": "tel_wgl_dharmasagar", "name": "Dharmasagar Village", ... },
  "forecast_horizon_days": 14,
  "generation_timestamp": "2026-09-29T23:15:00",
  "onset_outlook": {
    "status": "ONSET_DECLARED",
    "confidence_score": 0.92,
    "is_false_alarm": false,
    "normal_onset_date": "June 08",
    "reasons": ["Consecutive 48-hr rainfall >= 2.5mm satisfied with supporting synoptic wind and low OLR."]
  },
  "break_spell_outlook": {
    "risk_level": "LOW",
    "probability": 0.15,
    "projected_consecutive_dry_days": 1,
    "is_break_active": false
  },
  "rainfall_anomaly_outlook": {
    "observed_mm": 115.5,
    "normal_mm": 105.0,
    "departure_percentage": 10.0,
    "category": "Normal"
  },
  "heavy_rainfall_risk": {
    "heavy_rainfall_risk": "GREEN_NO_HEAVY_RAIN",
    "description": "No heavy rainfall events projected in current horizon."
  },
  "timeline": [ ... ]
}
```

---

## 4. Agricultural Advisories
### `GET /api/advisories`
Returns crop-specific actionable guidance.

**Query Parameters:**
- `location_id` (string, required)
- `lang` (string, optional): `'en'` or `'te'` (default: `'en'`)
- `crop` (string, optional): `'paddy'`, `'cotton'`, `'soybean'`, `'groundnut'`, `'maize'`, `'pulses'`
- `scenario` (string, optional)

---

## 5. GIS Layers
### `GET /api/risk-map`
Returns GeoJSON isochrones and gridded radar precipitation points.

---

## 6. Secure Data Upload
### `POST /api/data/upload`
Accepts `multipart/form-data` with key `file` (.csv). Validates size (max 16 MB) and schema columns.
