# SIH26086: Hyperlocal Monsoon Onset & Break Prediction System at Block/Village Scale
### Ministry of Earth Sciences (MoES) | Smart India Hackathon 2026
**Theme:** Agriculture, FoodTech & Rural Development | **Scale:** Block, Mandal & Village Level (~1km–5km)

---

## 🌾 1. Problem Description & Intended Users
The Indian Summer Monsoon dictates the agricultural cycle and livelihood of over 600 million farmers. Standard meteorological forecasts operate at regional or subdivision scales (thousands of sq km), leading to:
- **Premature Sowing Failures**: Isolated pre-monsoon convective thunderstorms mistaken for true monsoon onset, causing seed scorch and replanting expenses.
- **Break-Spell Crop Losses**: Unpredicted 5–15 day dry spells during active vegetative or flowering phases.
- **Information Barrier**: Complex meteorological indices not translated into actionable vernacular guidance for farmers.

### Intended Users
1. **Smallholder Farmers**: Receive simple, localized sowing windows, irrigation alerts, and fertilizer guidance in their regional languages (**English and Telugu**).
2. **Village Agricultural Officers (MAOs / KVK Scientists)**: Access fine-scale rainfall anomaly, soil moisture depletion, and heavy-rainfall risk projections.
3. **Hackathon Evaluators**: Verify an end-to-end, scientifically grounded, reproducible software prototype.

---

## 🏛 2. Architecture & Technology Stack

- **Backend Web Framework:** Python & **Flask REST API** (`app.py`, `backend/routes/api.py`).
- **Data Processing & Analytics:** **Pandas** and **NumPy**.
- **Forecasting & Machine Learning:** **Scikit-learn** (Random Forest Classifier) & **Joblib** model persistence.
- **Database:** **SQLite** (`database/sih26086.sqlite3`) with relational schema and indexing.
- **Frontend User Interface:** **HTML5**, **CSS3 (Vanilla Glassmorphism)**, **Vanilla JavaScript** (Mobile-first, responsive).
- **Mapping & Geospatial:** **Leaflet.js** with GeoJSON monsoon isochrones (Northern Limit of Monsoon) and gridded precipitation radar layers.
- **Data Visualizations:** **Chart.js** for 14-day rainfall and soil moisture trajectory tracking.
- **Accessibility & Localization:** Bilingual interface (**English `en` and Telugu `te`**) and Web Speech API **Text-To-Speech (TTS)** voice readouts.
- **Testing:** **Pytest** with automated unit, integration, and API test coverage.

---

## 📋 3. Requirements Traceability Matrix Summary

All requirements are systematically tracked in [`docs/requirements_traceability.md`](docs/requirements_traceability.md) according to 5 strict verification categories:

| Req ID | Capability | Status | Verified Test Suite |
| :--- | :--- | :--- | :--- |
| **REQ-PRI-1** | 7–30-Day Probabilistic Monsoon Outlook | **Demonstration using synthetic data** | `tests/test_forecasting.py::test_forecast_pipeline_horizons` |
| **REQ-PRI-2** | Climate Drivers (ENSO, IOD, MJO) Telemetry | **Partially implemented** | `tests/test_transparency_and_provenance.py::test_climate_drivers_provenance_labels` |
| **REQ-PRI-3** | Block/Village Spatial Risk Map & Geometry | **Demonstration using synthetic data** | `tests/test_api.py::test_api_risk_map` |
| **REQ-PRI-4** | ICAR-CRIDA Crop Agronomic Advisory Engine | **Implemented and tested** | `tests/test_advisories.py::test_crop_profiles_completeness` |
| **REQ-PRI-5** | Mobile Web App & Messaging Sandbox (Bilingual) | **Implemented and tested** | `tests/test_locales.py::test_locale_files_exist_and_valid` |
| **REQ-SUP-1** | IMD Operational Onset & False-Alarm Filter | **Implemented and tested** | `tests/test_event_definitions.py::test_onset_criteria_satisfied` |
| **REQ-SUP-2** | IMD 5-Tier Rainfall Anomaly Classification | **Implemented and tested** | `tests/test_event_definitions.py::test_rainfall_anomaly_categories` |
| **REQ-SUP-3** | Heavy Rainfall Early Warning Alerts | **Implemented and tested** | `tests/test_event_definitions.py::test_heavy_rainfall_risk_levels` |
| **REQ-SUP-4** | Data Ingestion & Quality Control | **Implemented and tested** | `tests/test_ingestion.py::test_ingestion_valid_csv` |
| **REQ-SUP-5** | Real Data Connectors (NOAA CPC ONI, NASA POWER) | **Implemented and tested** | `tests/test_transparency_and_provenance.py::test_real_data_connectors_structure` |
| **REQ-SUP-6** | Model Transparency & Synthetic Disclaimers | **Implemented and tested** | `tests/test_transparency_and_provenance.py::test_model_info_synthetic_accuracy_disclaimer` |
| **REQ-DEP-1** | Operational IMD 0.25° Gridded Direct Feed | **Dependent on external data or credentials** | Requires MoES institutional MoU & credentials |
| **REQ-DEP-2** | NCMRWF Ensemble GRIB2 Stream Access | **Dependent on external data or credentials** | Requires NCMRWF internal HPC network access |
| **REQ-DEP-3** | Pan-India Cadastral Village Boundaries | **Dependent on external data or credentials** | Survey of India cadastral boundaries restricted |
| **REQ-DEP-4** | Telecom SMS / WhatsApp Production Gateway | **Dependent on external data or credentials** | Requires TRAI DLT registration & SMS gateway |
| **REQ-VAL-1** | Empirical Real-World Ground-Truth Validation | **Not yet validated against real-world observations** | Pending historical multi-year IMD station archive |

---

## ⚡ 4. Quick Start & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Web browser (Chrome, Safari, Firefox, Edge)

### 1. Environment Setup
```bash
# Create Python virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate    # On Windows: backend\venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Database Initialisation & Seeding
```bash
python database/initialise.py
```
*Creates `database/sih26086.sqlite3` and seeds verified locations across Telangana, Andhra Pradesh, Maharashtra, Karnataka, and MP.*

### 3. Ingest Data & Train Forecasting Model
```bash
# Ingest demonstration dataset
python forecasting/data_ingestion.py

# Train Random Forest model on synthetic benchmark
python forecasting/train.py
```

### 4. Start the Application
```bash
PORT=5050 python app.py
```
Open your browser at: **`http://localhost:5050`** (or `http://127.0.0.1:5050`).

---

## 🧪 5. Automated Testing
Run the complete automated test suite (36 tests covering API, ingestion, physics rules, models, real data connectors, and transparency disclaimers):
```bash
pytest tests/ -v
```
All **36 tests pass** with complete reproducibility.

---

## 📂 6. Repository Layout
```
├── app.py                      # Flask Application entry point & static file server
├── config.py                   # Central configuration & paths
├── requirements.txt            # Dependency manifest (Flask, Pandas, NumPy, Scikit-learn, Pytest)
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclude patterns
├── pytest.ini                  # Pytest configuration
├── database/
│   ├── schema.sql              # Relational SQLite schema definition
│   ├── initialise.py           # Database initialisation & location seeder
│   └── sih26086.sqlite3        # SQLite local database
├── forecasting/
│   ├── data_ingestion.py       # CSV validation & database ingestion
│   ├── preprocessing.py        # Rolling rainfall sums & dry streak computation
│   ├── event_definitions.py    # Configurable IMD criteria, break spell, & anomaly logic
│   ├── feature_engineering.py  # Leak-free lagged feature extraction
│   ├── train.py                # Chronological train/test split & model training
│   ├── evaluate.py             # Model card evaluation & Brier score report
│   ├── predict.py              # Multi-horizon inference pipeline (7, 14, 21, 30 days)
│   └── generate_sample_data.py # Sample data generator
├── advisories/
│   ├── crop_profiles.py        # ICAR-CRIDA agronomic parameters (Paddy, Cotton, etc.)
│   └── rules.py                # Decision engine for sowing, irrigation, and fertilizers
├── data/
│   ├── README.md               # Data provenance & synthetic data notice
│   ├── sample/                 # Synthetic demonstration datasets
│   └── processed/              # Uploaded user datasets
├── models/
│   ├── break_model_rf.joblib   # Trained Random Forest classifier
│   └── break_model_metadata.json # Model evaluation metrics & metadata
├── frontend/
│   ├── index.html              # Responsive single-page application
│   ├── css/style.css           # Glassmorphism styling and dark mode
│   ├── js/app.js               # Application logic, Chart.js, and TTS speech
│   ├── js/map.js               # Leaflet GIS integration & overlays
│   └── locales/
│       ├── en.json             # English UI translations
│       └── te.json             # Telugu (తెలుగు) UI translations
├── tests/                      # Automated Pytest suite (30 test cases)
└── docs/                       # Comprehensive documentation
    ├── architecture.md
    ├── data_sources.md
    ├── model_card.md
    ├── api.md
    ├── testing.md
    ├── limitations.md
    └── requirements_traceability.md
```

---

## 🔬 7. Scientific Methodology: Observations to Advisories

```
1. Hyperlocal Ingestion (Rainfall, Westerly Winds 850hPa, Satellite OLR, Soil Moisture)
                          │
                          ▼
2. IMD Operational Verification (Pai et al. 2014 Criteria)
   • 48-hour cumulative rainfall ≥ 2.5mm
   • Zonal wind at 850hPa ≥ 15 knots (Somali Jet)
   • OLR < 200 W/m² (deep convective cloud mass)
   • False Alarm Check (prevents dry-sowing losses from isolated thunderstorms)
                          │
                          ▼
3. Break Spell & Drought Forecaster
   • Northward displacement of monsoon trough toward Himalayan foothills
   • Random Forest model predicts dry streak probability (Brier Skill Score: +0.158)
                          │
                          ▼
4. Agronomic Decision Engine (ICAR-CRIDA Guidelines)
   • Sowing Window: Confirms 50–60mm root saturation before sowing recommendation
   • Break Protection: Strictly suspends urea top-dressing; advises 1.5% KNO3 foliar spray
   • Excess Water Protection: Drainage channel alerts during heavy rain
                          │
                          ▼
5. Vernacular Delivery (English & Telugu with Audio Speech Synthesis)
```

---

## ⚠️ 8. Ethical Use & Demonstration Disclaimer
1. **Demonstration Dataset**: Datasets in `data/sample/` are **SYNTHETIC DEMONSTRATION DATA** created for offline hackathon verification without paid API keys.
2. **Extension Worker Consultation**: Farmers are advised to consult their local **Mandal Agricultural Officer (MAO)** or **Krishi Vigyan Kendra (KVK)** before undertaking non-reversible agricultural investments.
