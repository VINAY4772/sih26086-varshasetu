-- SIH26086 SQLite Database Schema
-- Ministry of Earth Sciences (MoES) Hyperlocal Monsoon Onset & Break Prediction

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    block_or_mandal TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    elevation_m REAL DEFAULT 150.0,
    primary_soil TEXT DEFAULT 'Clay Loam',
    agro_climatic_zone TEXT,
    normal_onset_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    spatial_resolution TEXT,
    temporal_resolution TEXT,
    update_frequency TEXT,
    license TEXT,
    description TEXT,
    is_synthetic INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    date TEXT NOT NULL,
    rainfall_mm REAL NOT NULL,
    temp_max_c REAL,
    temp_min_c REAL,
    humidity_pct REAL,
    wind_speed_ms REAL,
    wind_dir_deg REAL,
    olr_wm2 REAL,
    zonal_wind_850hpa_ms REAL,
    soil_moisture_pct REAL,
    enso_nino34 REAL,
    iod_dmi REAL,
    mjo_amplitude REAL,
    data_source_id TEXT,
    FOREIGN KEY(location_id) REFERENCES locations(id),
    FOREIGN KEY(data_source_id) REFERENCES data_sources(id),
    UNIQUE(location_id, date)
);

CREATE TABLE IF NOT EXISTS forecast_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id TEXT NOT NULL,
    forecast_horizon_days INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    onset_status TEXT NOT NULL,
    onset_probability REAL,
    dry_spell_days INTEGER,
    break_probability REAL,
    rainfall_anomaly_pct REAL,
    heavy_rain_risk TEXT,
    validity_start TEXT NOT NULL,
    validity_end TEXT NOT NULL,
    data_provenance TEXT,
    is_demonstration INTEGER DEFAULT 1,
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS crop_advisories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_run_id INTEGER,
    location_id TEXT NOT NULL,
    crop_code TEXT NOT NULL,
    crop_name TEXT NOT NULL,
    growth_stage TEXT,
    sowing_status TEXT NOT NULL,
    sowing_window TEXT,
    irrigation_advice TEXT,
    fertilizer_advice TEXT,
    pest_advice TEXT,
    priority_action TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    uncertainty_notes TEXT,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(forecast_run_id) REFERENCES forecast_runs(id),
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_type TEXT DEFAULT 'farmer',
    recipient_mask TEXT NOT NULL,
    channel TEXT NOT NULL,
    message_body TEXT NOT NULL,
    status TEXT NOT NULL,
    simulated INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_loc_date ON observations(location_id, date);
CREATE INDEX IF NOT EXISTS idx_fc_loc_time ON forecast_runs(location_id, run_timestamp);
