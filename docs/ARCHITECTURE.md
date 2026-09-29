# System Architecture: SIH26086
## Hyperlocal Monsoon Onset & Break Prediction System at Block/Village Scale
### Ministry of Earth Sciences (MoES) | Smart India Hackathon 2026

---

## 1. Architectural Overview
The SIH26086 platform is structured as a modular, lightweight, and maintainable end-to-end meteorological intelligence system. It runs locally using free, open-source technologies without requiring paid third-party APIs or complex external cloud infrastructure.

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │                Data Sources & Ingestion                │
                                    │ • IMD Gridded Rainfall (0.25°)                         │
                                    │ • NOAA CPC Niño 3.4 (ENSO)                             │
                                    │ • BOM Dipole Mode Index (IOD)                          │
                                    │ • CPC Wheeler-Hendon RMM (MJO)                         │
                                    │ • SYNTHETIC DEMONSTRATION DATA (Sample / Benchmark)    │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                                                ▼
                                    ┌────────────────────────────────────────────────────────┐
                                    │              Data Ingestion & Validation               │
                                    │             (forecasting/data_ingestion.py)            │
                                    │ • Physical value clamping & sanity verification        │
                                    │ • Duplicate elimination & continuous temporal indexing │
                                    │ • Administrative identifier verification               │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                                                ▼
                                    ┌────────────────────────────────────────────────────────┐
                                    │                 SQLite Persistence Layer               │
                                    │               (database/sih26086.sqlite3)              │
                                    │ • locations & data_sources metadata                    │
                                    │ • observations & forecast_runs audit logs              │
                                    │ • crop_advisories & notification_logs                  │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                                                ▼
        ┌───────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┐
        │                                                                                                               │
        ▼                                                                                                               ▼
┌─────────────────────────────────────────────────┐                                           ┌─────────────────────────────────────────────────┐
│        Hybrid Forecasting Pipeline              │                                           │        Agronomic Advisory Decision Engine       │
│ • Operational IMD Onset Detector (Pai et al.)   │                                           │ • ICAR-CRIDA Phenological Thresholds            │
│ • False-Alarm Thunderstorm Filter               │──────────────────────────────────────────▶│ • Sowing Window Suitability                     │
│ • Break Spell Markov & Random Forest Model      │                                           │ • Nitrogen Urea Suspension During Breaks        │
│ • Climatological Anomaly & Heavy Rainfall Risk  │                                           │ • Protective Irrigation & Pest Scouting         │
│ • 7-, 14-, 21-, and 30-Day Outlook Horizons     │                                           │ • English & Telugu Dynamic Vernacular Output    │
└───────────────────────┬─────────────────────────┘                                           └───────────────────────┬─────────────────────────┘
                        │                                                                                             │
                        └───────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
                                    ┌────────────────────────────────────────────────────────┐
                                    │                   Flask REST API Service               │
                                    │              (app.py / backend/routes/api.py)          │
                                    │ • GET  /api/health            • GET  /api/risk-map     │
                                    │ • GET  /api/locations         • GET  /api/advisories   │
                                    │ • GET  /api/forecast          • GET  /api/model-info   │
                                    │ • GET  /api/rainfall-history  • POST /api/data/upload  │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                                                ▼
                                    ┌────────────────────────────────────────────────────────┐
                                    │         Modern Mobile-First Web Frontend               │
                                    │         (HTML5, CSS3, Vanilla JS, Leaflet, Chart.js)   │
                                    │ • Interactive Geospatial Risk Map & Isochrones         │
                                    │ • Chart.js 14-day rainfall & soil moisture trajectory   │
                                    │ • Bilingual Interface (English & Telugu - en/te)       │
                                    │ • Audio Readout (Web Speech API Text-to-Speech)        │
                                    │ • Accessible Non-Map Location Table Alternative        │
                                    └────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules Description

1. **`database/`**:
   - `schema.sql`: Declarative SQLite schema enforcing foreign keys and indexing.
   - `initialise.py`: Idempotent database bootstrapper with verified location seeding.
2. **`forecasting/`**:
   - `data_ingestion.py`: CSV ingestion engine with missing value, unit, and coordinate validation.
   - `preprocessing.py`: Rolling statistics (3d, 7d, 14d rain), wet day frequencies, dry streaks.
   - `event_definitions.py`: Configurable thresholds for IMD onset, breaks, anomalies, heavy rainfall.
   - `feature_engineering.py`: Lagged and rolling predictors with strict anti-leakage time shifting.
   - `train.py`: Chronological train/validation pipeline with Random Forest and Climatology baseline.
   - `evaluate.py`: Brier score, reliability analysis, and model card generation.
   - `predict.py`: Inference pipeline for 7, 14, 21, and 30-day outlooks.
3. **`advisories/`**:
   - `crop_profiles.py`: Agronomic parameters for Paddy, Cotton, Soybean, Groundnut, Maize, Pulses.
   - `rules.py`: Transparent rules linking meteorological triggers to crop actions in English and Telugu.
4. **`backend/`**:
   - `routes/api.py`: Clean REST API routes with input validation and error handling.
5. **`frontend/`**:
   - `index.html`: Responsive single page application.
   - `css/style.css`: Glassmorphism design tokens, accessible dark mode, mobile responsiveness.
   - `js/app.js`: Client-side logic, API calls, Chart.js graphs, Web Speech TTS narration.
   - `js/map.js`: Leaflet mapping manager with Isochrones and Doppler radar layers.
   - `locales/en.json` & `locales/te.json`: Externalized translations.
