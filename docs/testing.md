# Testing & Verification Report: SIH26086

## 1. Automated Test Framework
All test suites are implemented in Python using `pytest` and execute against real SQLite instances, verified data schemas, and mathematical boundary conditions.

Execute tests using:
```bash
pytest tests/ -v
```

---

## 2. Test Execution Results (30 / 30 Passed)

```
tests/test_advisories.py::test_crop_profiles_completeness PASSED         [  3%]
tests/test_advisories.py::test_advisory_sowing_rules_onset PASSED        [  6%]
tests/test_advisories.py::test_advisory_break_spell_suppression PASSED   [ 10%]
tests/test_advisories.py::test_advisory_telugu_language PASSED           [ 13%]
tests/test_api.py::test_api_health PASSED                                [ 16%]
tests/test_api.py::test_api_locations PASSED                             [ 20%]
tests/test_api.py::test_api_locations_filter PASSED                      [ 23%]
tests/test_api.py::test_api_forecast PASSED                              [ 26%]
tests/test_api.py::test_api_forecast_invalid_horizon PASSED              [ 30%]
tests/test_api.py::test_api_risk_map PASSED                              [ 33%]
tests/test_api.py::test_api_rainfall_history PASSED                      [ 36%]
tests/test_api.py::test_api_advisories_multilingual PASSED               [ 40%]
tests/test_api.py::test_api_model_info PASSED                            [ 43%]
tests/test_api.py::test_api_data_sources PASSED                          [ 46%]
tests/test_api.py::test_api_file_upload_security PASSED                  [ 50%]
tests/test_api.py::test_api_notification_simulate PASSED                 [ 53%]
tests/test_database.py::test_database_initialisation_and_tables PASSED   [ 56%]
tests/test_database.py::test_database_seed_locations_and_sources PASSED  [ 60%]
tests/test_event_definitions.py::test_onset_criteria_satisfied PASSED    [ 63%]
tests/test_event_definitions.py::test_false_onset_detection PASSED       [ 66%]
tests/test_event_definitions.py::test_break_spell_critical_detection PASSED [ 70%]
tests/test_event_definitions.py::test_rainfall_anomaly_categories PASSED [ 73%]
tests/test_event_definitions.py::test_heavy_rainfall_risk_levels PASSED  [ 76%]
tests/test_forecasting.py::test_forecast_pipeline_horizons PASSED        [ 80%]
tests/test_forecasting.py::test_probabilities_between_zero_and_one PASSED [ 83%]
tests/test_forecasting.py::test_model_evaluation_report_structure PASSED [ 86%]
tests/test_ingestion.py::test_ingestion_valid_csv PASSED                 [ 90%]
tests/test_ingestion.py::test_ingestion_missing_required_column PASSED   [ 93%]
tests/test_ingestion.py::test_ingestion_clamping_and_duplicates PASSED   [ 96%]
tests/test_locales.py::test_locale_files_exist_and_valid PASSED          [100%]

============================== 30 passed in 1.60s ==============================
```

---

## 3. Test Coverage Breakdown
- **Database Initialisation:** Tests schema creation, constraints, seed data.
- **Ingestion & Preprocessing:** Tests duplicate handling, clamping of negative/extreme values, missing mandatory headers.
- **Event Definition Logic:** Tests IMD 48-hr thresholding, wind shear and OLR criteria, false-onset alarm detection, dry spell streaks, rainfall departure categories, and heavy rain alert grades.
- **Machine Learning & Forecasting:** Tests feature vector alignment, chronological test partition evaluation, probability bounds ($0.0 \le P \le 1.0$), and Brier Skill Score calculation.
- **Agricultural Decision Engine:** Tests sowing windows, nitrogen suspension during break spells, and Telugu text outputs.
- **REST API Endpoints:** Tests status codes (200, 400, 404), JSON structure, and secure upload guards.
- **Localization:** Tests English and Telugu dictionary key symmetry and valid Unicode rendering.
