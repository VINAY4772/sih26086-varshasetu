# Requirements Traceability Matrix (RTM): SIH26086
## Hyperlocal Monsoon Onset & Break Prediction System at Block/Village Scale
### Ministry of Earth Sciences (MoES) | Smart India Hackathon 2026

The following matrix traces every requirement specified in the SIH26086 Master Specification to its implementation file, UI/API touchpoint, verification method, and current verified status.

Only the five approved status values are used:
- **Implemented and tested**
- **Implemented but not fully validated**
- **Partially implemented**
- **Blocked by external dependency**
- **Not implemented**

---

| Req ID | Requirement Description | Implementation Module / File | Relevant UI Section / API Endpoint | Associated Verification / Test Method | Actual Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | **Monsoon onset prediction & confidence** with transparent operational criteria | `forecasting/event_definitions.py`<br>`forecasting/predict.py` | Dashboard Card 1 (`#onset-status-card`)<br>`GET /api/forecast` | `tests/test_event_definitions.py::test_onset_criteria_satisfied`<br>`tests/test_event_definitions.py::test_false_onset_detection` | **Implemented and tested** |
| **REQ-02** | **Monsoon breaks, prolonged dry spells, & revival** prediction | `forecasting/event_definitions.py`<br>`forecasting/train.py`<br>`forecasting/predict.py` | Dashboard Card 2 (`#break-risk-card`)<br>`GET /api/forecast` | `tests/test_event_definitions.py::test_break_spell_critical_detection`<br>`tests/test_forecasting.py::test_probabilities_between_zero_and_one` | **Implemented and tested** |
| **REQ-03** | **Subseasonal horizons (7, 14, 21, 30 days)** with documented validation | `forecasting/predict.py`<br>`backend/routes/api.py` | Horizon selector dropdown (`#horizon-select`)<br>`GET /api/forecast?horizon=...` | `tests/test_forecasting.py::test_forecast_pipeline_horizons`<br>`tests/test_api.py::test_api_forecast_invalid_horizon` | **Implemented and tested** |
| **REQ-04** | **Climate drivers (ENSO, IOD, MJO)** integration in feature pipeline | `forecasting/feature_engineering.py`<br>`forecasting/train.py` | Feature vector columns `enso_nino34`, `iod_dmi`, `mjo_amplitude` | `tests/test_forecasting.py::test_model_evaluation_report_structure` | **Implemented and tested** |
| **REQ-05** | **Regional atmospheric variables & historical observations** ingestion | `forecasting/data_ingestion.py`<br>`forecasting/preprocessing.py` | Telemetry Grid Card 3<br>`GET /api/rainfall-history` | `tests/test_ingestion.py::test_ingestion_valid_csv`<br>`tests/test_ingestion.py::test_ingestion_clamping_and_duplicates` | **Implemented and tested** |
| **REQ-06** | **Block/Village level granularity** with justified resolution | `database/initialise.py`<br>`forecasting/predict.py` | Location selector dropdown (`#location-select`)<br>`GET /api/locations` | `tests/test_database.py::test_database_seed_locations_and_sources`<br>`tests/test_api.py::test_api_locations` | **Implemented and tested** |
| **REQ-07** | **Rainfall anomalies, onset, dry-spell risk, & heavy rainfall risk** display | `forecasting/event_definitions.py`<br>`frontend/js/app.js` | Status Grid 4 cards (`#anomaly-val`, `#heavy-rain-val`) | `tests/test_event_definitions.py::test_rainfall_anomaly_categories`<br>`tests/test_event_definitions.py::test_heavy_rainfall_risk_levels` | **Implemented and tested** |
| **REQ-08** | **Interactive colour-coded risk map & isochrones** with clear legends and non-map alternative | `frontend/js/map.js`<br>`backend/routes/api.py` | Leaflet map (`#map-container`) & Location table (`#location-table-container`)<br>`GET /api/risk-map` | `tests/test_api.py::test_api_risk_map`<br>HTTP 200 static asset & non-map table verification | **Implemented and tested** |
| **REQ-09** | **Crop-specific agricultural guidance** covering sowing, irrigation, fertilizer, and alternatives | `advisories/crop_profiles.py`<br>`advisories/rules.py` | Crop cards grid (`#crops-grid`)<br>`GET /api/advisories` | `tests/test_advisories.py::test_crop_profiles_completeness`<br>`tests/test_advisories.py::test_advisory_sowing_rules_onset`<br>`tests/test_advisories.py::test_advisory_break_spell_suppression` | **Implemented and tested** |
| **REQ-10** | **Mobile-friendly web application** with optional notification sandbox | `frontend/index.html`<br>`frontend/css/style.css`<br>`backend/routes/api.py` | Web app responsive layout<br>`POST /api/notifications/simulate` | `tests/test_api.py::test_api_notification_simulate`<br>Viewport CSS responsiveness checks | **Implemented and tested** |
| **REQ-11** | **Bilingual English and Telugu support** with externalized JSON locales | `frontend/locales/en.json`<br>`frontend/locales/te.json`<br>`advisories/rules.py` | Language switcher dropdown (`#lang-select`)<br>`GET /api/advisories?lang=te` | `tests/test_locales.py::test_locale_files_exist_and_valid`<br>`tests/test_advisories.py::test_advisory_telugu_language` | **Implemented and tested** |
| **REQ-12** | **Data sources, model transparency, uncertainty, and limitations** disclosure | `forecasting/evaluate.py`<br>`docs/model_card.md`<br>`docs/limitations.md` | Data & Model info section (`#model-transparency-content`)<br>`GET /api/model-info`<br>`GET /api/data-sources` | `tests/test_api.py::test_api_model_info`<br>`tests/test_api.py::test_api_data_sources` | **Implemented and tested** |
| **REQ-13** | **Live Real-Time Operational IMD API Direct Feed** (outside local synthetic benchmark) | External MoES/IMD API credentials | Future external service connector | Dependent on official MoES/IMD authorization | **Blocked by external dependency** |
