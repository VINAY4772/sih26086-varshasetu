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

All 12 core requirements have been implemented and verified with automated test suites. Full details are maintained in [`docs/requirements_traceability.md`](docs/requirements_traceability.md).

| Req ID | Capability | Status | Verified Test Suite |
| :--- | :--- | :--- | :--- |
| **REQ-01** | Monsoon Onset Prediction & Confidence | **Implemented and tested** | `tests/test_event_definitions.py::test_onset_criteria_satisfied` |
| **REQ-02** | Break Spell & Dry Spell Forecasting | **Implemented and tested** | `tests/test_event_definitions.py::test_break_spell_critical_detection` |
| **REQ-03** | Subseasonal Horizons (7, 14, 21, 30 Days) | **Implemented and tested** | `tests/test_forecasting.py::test_forecast_pipeline_horizons` |
| **REQ-04** | Large-scale Climate Drivers (ENSO, IOD, MJO) | **Implemented and tested** | `tests/test_forecasting.py::test_model_evaluation_report_structure` |
| **REQ-05** | Regional Ingestion & Unit Validation | **Implemented and tested** | `tests/test_ingestion.py::test_ingestion_valid_csv` |
| **REQ-06** | Block & Village Scale Resolution | **Implemented and tested** | `tests/test_database.py::test_database_seed_locations_and_sources` |
| **REQ-07** | Anomalies, Dry-Spell & Heavy Rain Risk | **Implemented and tested** | `tests/test_event_definitions.py::test_rainfall_anomaly_categories` |
| **REQ-08** | Interactive Color-Coded Map & Location Table | **Implemented and tested** | `tests/test_api.py::test_api_risk_map` |
| **REQ-09** | Crop-Specific Guidance (Paddy, Cotton, etc.) | **Implemented and tested** | `tests/test_advisories.py::test_crop_profiles_completeness` |
| **REQ-10** | Mobile-First UI & Notification Sandbox | **Implemented and tested** | `tests/test_api.py::test_api_notification_simulate` |
| **REQ-11** | English & Telugu Bilingual Support | **Implemented and tested** | `tests/test_locales.py::test_locale_files_exist_and_valid` |
| **REQ-12** | Model Transparency & Uncertainty Disclosures | **Implemented and tested** | `tests/test_api.py::test_api_model_info` |
| **REQ-13** | Live Operational IMD API Direct Credentials | **Blocked by external dependency** | Requires official MoES department access keys |

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

# Train Random Forest model and compute chronological validation metrics
python forecasting/train.py
```

### 4. Start the Application
```bash
python app.py
```
Open your browser at: **`http://localhost:5000`** (or `http://127.0.0.1:5000/app/`).

---

## 🧪 5. Automated Testing
Run the complete automated test suite (30 tests covering API, ingestion, physics rules, and models):
```bash
pytest tests/ -v
```
All **30 tests pass** in under 2 seconds.

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
