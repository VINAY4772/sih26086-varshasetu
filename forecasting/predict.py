import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import joblib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from database.initialise import get_db_connection
from forecasting.event_definitions import MeteorologicalEventDetector, EventThresholdConfig
from forecasting.feature_engineering import engineer_features, FEATURE_COLUMNS

class MonsoonForecastPipeline:
    def __init__(self, model_path: Optional[str] = None):
        import os
        self.detector = MeteorologicalEventDetector()
        active_model_name = os.environ.get("ACTIVE_MODEL_FILENAME", "break_model_rf.joblib")
        self.model_path = Path(model_path) if model_path else (Config.MODELS_DIR / active_model_name)
        self.rf_model = None
        if self.model_path.exists():
            try:
                self.rf_model = joblib.load(self.model_path)
            except Exception as e:
                print(f"Notice: Could not load RF model ({e}), using analytical baseline detector.")

    def generate_forecast(
        self,
        location_id: str,
        horizon_days: int = 14,
        scenario: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates calibrated forecast outputs for requested location and horizon.
        Supported horizons: 7, 14, 21, 30 days.
        """
        conn = get_db_connection()
        loc_row = conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()
        if not loc_row:
            conn.close()
            raise ValueError(f"Unknown location_id: '{location_id}'")

        # Load recent 30-day observations
        obs_rows = conn.execute(
            """
            SELECT * FROM observations
            WHERE location_id = ?
            ORDER BY date DESC LIMIT 30
            """,
            (location_id,)
        ).fetchall()
        conn.close()

        location_meta = dict(loc_row)
        today = datetime.date.today()
        validity_start = today.strftime("%Y-%m-%d")
        validity_end = (today + datetime.timedelta(days=horizon_days)).strftime("%Y-%m-%d")

        # Synthesize/adjust scenario timeline if requested for demonstration
        timeline = self._generate_horizon_timeline(location_meta, horizon_days, scenario)

        # 1. Onset Prediction & Confidence
        recent_rain = [r["rainfall_mm"] for r in timeline[:7]]
        recent_wind = timeline[0].get("zonal_wind_850hpa_ms", 8.0)
        recent_olr = timeline[0].get("olr_wm2", 195.0)

        onset_res = self.detector.evaluate_onset_criteria(
            recent_daily_rainfall=recent_rain,
            zonal_wind_850hpa_ms=recent_wind,
            olr_wm2=recent_olr
        )

        # 2. Climate Drivers Teleconnection (ENSO, IOD, MJO)
        # Attempt live verified NOAA CPC ONI retrieval with safe fast fallback
        enso_source_status = "CONFIGURED_BENCHMARK"
        enso_provenance = "Configured demonstration parameter (not live ground telemetry)"
        nino34_val = 0.25

        try:
            from forecasting.real_data_connectors import fetch_noaa_cpc_oni
            live_oni = fetch_noaa_cpc_oni(timeout_sec=2)
            if live_oni.get("status") == "LIVE_VERIFIED":
                nino34_val = float(live_oni["nino34_anomaly_c"])
                enso_source_status = "LIVE_VERIFIED_NOAA_CPC"
                enso_provenance = f"Live verified NOAA CPC ONI ({live_oni.get('season')} {live_oni.get('year')})"
        except Exception:
            pass

        iod_val = 0.15
        iod_source_status = "CONFIGURED_BENCHMARK"
        iod_provenance = "Configured demonstration parameter (BOM automated access restricted by CDN policy)"

        mjo_phase_val = 3
        mjo_amp_val = 1.2
        mjo_source_status = "CONFIGURED_BENCHMARK"
        mjo_provenance = "Configured demonstration parameter (CPC RMM daily feed pending institutional parser)"

        climate_res = self.detector.evaluate_climate_drivers_influence(
            enso_nino34=nino34_val,
            iod_dmi=iod_val,
            mjo_phase=mjo_phase_val,
            mjo_amplitude=mjo_amp_val
        )
        climate_res["enso"]["source_status"] = enso_source_status
        climate_res["enso"]["provenance_note"] = enso_provenance
        climate_res["iod"]["source_status"] = iod_source_status
        climate_res["iod"]["provenance_note"] = iod_provenance
        climate_res["mjo"]["source_status"] = mjo_source_status
        climate_res["mjo"]["provenance_note"] = mjo_provenance

        climate_break_mod = climate_res["net_break_risk_modifier"]

        # 3. Break Spell / Dry Spell Probability
        break_res = self.detector.detect_break_spells([r["rainfall_mm"] for r in timeline])
        break_prob = break_res["break_probability"]

        if self.rf_model is not None and len(timeline) >= 3:
            try:
                # Build feature vector strictly from preceding observations (leak-free operational inference)
                obs_list = [dict(r) for r in obs_rows] if obs_rows else []
                if obs_list and scenario is None:
                    # Operational forecasting mode: features derived strictly from historical observations
                    rain_l1 = float(obs_list[0].get("rainfall_mm", 0.0))
                    rain_l2 = float(obs_list[1].get("rainfall_mm", 0.0)) if len(obs_list) > 1 else 0.0
                    rain_l3 = float(obs_list[2].get("rainfall_mm", 0.0)) if len(obs_list) > 2 else 0.0
                    roll_7 = float(sum(r.get("rainfall_mm", 0.0) for r in obs_list[:7]))
                    roll_14 = float(sum(r.get("rainfall_mm", 0.0) for r in obs_list[:min(14, len(obs_list))]))
                    wet_7 = float(sum(1 for r in obs_list[:7] if r.get("rainfall_mm", 0.0) >= 2.5))
                    # Calculate past dry streak
                    c_dry = 0
                    for r in obs_list:
                        if r.get("rainfall_mm", 0.0) < 2.5:
                            c_dry += 1
                        else:
                            break
                    t_max = float(obs_list[0].get("temp_max_c", 32.0))
                    rh = float(obs_list[0].get("humidity_pct", 70.0))
                    olr = float(obs_list[0].get("olr_wm2", 195.0))
                    wind_850 = float(obs_list[0].get("zonal_wind_850hpa_ms", 8.0))
                else:
                    # Scenario demonstration mode: user intentionally testing hypothetical scenario
                    rain_l1 = timeline[0]["rainfall_mm"]
                    rain_l2 = timeline[1]["rainfall_mm"] if len(timeline) > 1 else 0.0
                    rain_l3 = timeline[2]["rainfall_mm"] if len(timeline) > 2 else 0.0
                    roll_7 = sum(r["rainfall_mm"] for r in timeline[:7])
                    roll_14 = sum(r["rainfall_mm"] for r in timeline[:min(14, len(timeline))])
                    wet_7 = sum(1 for r in timeline[:7] if r["rainfall_mm"] >= 2.5)
                    c_dry = break_res["max_consecutive_dry_days"]
                    t_max = timeline[0]["temp_max_c"]
                    rh = timeline[0]["humidity_pct"]
                    olr = timeline[0]["olr_wm2"]
                    wind_850 = timeline[0]["zonal_wind_850hpa_ms"]

                cur_feat = {
                    "rain_lag_1": rain_l1,
                    "rain_lag_2": rain_l2,
                    "rain_lag_3": rain_l3,
                    "rain_roll_7d": roll_7,
                    "rain_roll_14d": roll_14,
                    "wet_days_7d": wet_7,
                    "consecutive_dry_days": c_dry,
                    "temp_max_c": t_max,
                    "humidity_pct": rh,
                    "olr_wm2": olr,
                    "zonal_wind_850hpa_ms": wind_850,
                    "enso_nino34": nino34_val,
                    "iod_dmi": iod_val,
                    "mjo_amplitude": mjo_amp_val,
                    "day_of_year": today.timetuple().tm_yday,
                    "latitude": location_meta["latitude"],
                    "elevation_m": location_meta["elevation_m"]
                }
                feat_df = pd.DataFrame([cur_feat])[FEATURE_COLUMNS]
                rf_prob = float(self.rf_model.predict_proba(feat_df)[0][1])
                # Blend physics rules, machine-learning probability, and climate teleconnection
                blended_prob = 0.45 * break_prob + 0.45 * rf_prob + 0.10 * (break_prob + climate_break_mod)
                break_prob = round(max(0.02, min(0.98, blended_prob)), 3)
            except Exception as e:
                break_prob = round(max(0.02, min(0.98, break_prob + climate_break_mod)), 3)

        # 4. Multi-Horizon Uncertainty Calibration (7, 14, 21, 30 days)
        horizon_uncertainty_bands = {
            7: {
                "uncertainty_pct": 8.0,
                "skill_tier": "High Synoptic Deterministic Skill",
                "model_confidence_score": 0.86,
                "uncertainty_type": "provisional_heuristic_assumption",
                "is_empirically_calibrated": False,
                "disclaimer": "Provisional assumption; not empirically calibrated against real ensemble dispersion."
            },
            14: {
                "uncertainty_pct": 16.0,
                "skill_tier": "Extended-Range Medium Skill (NEPS/MJO)",
                "model_confidence_score": 0.74,
                "uncertainty_type": "provisional_heuristic_assumption",
                "is_empirically_calibrated": False,
                "disclaimer": "Provisional assumption; not empirically calibrated against real ensemble dispersion."
            },
            21: {
                "uncertainty_pct": 24.0,
                "skill_tier": "Subseasonal (S2S) Probabilistic Outlook",
                "model_confidence_score": 0.62,
                "uncertainty_type": "provisional_heuristic_assumption",
                "is_empirically_calibrated": False,
                "disclaimer": "Provisional assumption; not empirically calibrated against real ensemble dispersion."
            },
            30: {
                "uncertainty_pct": 32.0,
                "skill_tier": "Monthly Climate Anomaly Trend (ENSO/IOD Background)",
                "model_confidence_score": 0.54,
                "uncertainty_type": "provisional_heuristic_assumption",
                "is_empirically_calibrated": False,
                "disclaimer": "Provisional assumption; not empirically calibrated against real ensemble dispersion."
            }
        }
        h_info = horizon_uncertainty_bands.get(horizon_days, horizon_uncertainty_bands[14])

        # 5. Spell Duration Analysis (Active & Break Spells)
        spell_analysis = self.detector.analyze_spells_duration(timeline)

        # Expected onset window based on physical criteria
        if onset_res["status"] == "ONSET_DECLARED":
            expected_onset_window = "Within 3–5 Days (Imminent)"
        elif onset_res.get("is_false_alarm"):
            expected_onset_window = "Delayed (Pre-monsoon only; synoptic criteria unmet)"
        elif onset_res["status"] == "INSUFFICIENT_OBSERVATION_DAYS":
            expected_onset_window = "Insufficient data for threshold assessment"
        else:
            expected_onset_window = f"Normal Climatological Window: {location_meta['normal_onset_date']}"

        # Active spell probability
        active_prob = round(max(0.05, min(0.95, 1.0 - break_prob)), 3)
        active_status = (
            "ACTIVE" if (spell_analysis["active_spell"]["expected_duration_days"] or 0) >= 3
            else ("MODERATE" if (spell_analysis["active_spell"]["expected_duration_days"] or 0) >= 1 else "SUBDUED")
        )

        # 6. Rainfall Anomaly Outlook
        total_fc_rain = sum(r["rainfall_mm"] for r in timeline)
        anomaly_res = self.detector.compute_rainfall_anomaly(total_fc_rain, period_days=horizon_days)

        # 7. Heavy Rainfall Risk
        heavy_rain_res = self.detector.evaluate_heavy_rainfall_risk([r["rainfall_mm"] for r in timeline])

        # Record forecast in DB for audit trail
        self._record_forecast_run(
            location_id=location_id,
            horizon_days=horizon_days,
            onset_status=onset_res["status"],
            onset_prob=onset_res["confidence_score"],
            dry_spell_days=break_res["max_consecutive_dry_days"],
            break_prob=break_prob,
            anomaly_pct=anomaly_res["departure_percentage"],
            heavy_risk=heavy_rain_res["heavy_rainfall_risk"],
            validity_start=validity_start,
            validity_end=validity_end
        )

        return {
            "location": location_meta,
            "forecast_horizon_days": horizon_days,
            "horizon_metadata": h_info,
            "generation_timestamp": datetime.datetime.now().isoformat(),
            "validity_period": {"start": validity_start, "end": validity_end},
            "is_demonstration": True,
            "disclaimer": "DEMONSTRATION FORECAST — NOT FOR AGRICULTURAL DECISIONS",
            "accuracy_notice": "Evaluated on synthetic benchmark data; does not establish real-world forecast accuracy.",
            "model_artifact": self.model_path.name,
            "data_provenance": "IMD Operational Criteria + NCMRWF Extended Range Principles + Synthetic Benchmark (SIH26086)",
            "climate_drivers": climate_res,
            "onset_outlook": {
                "status": onset_res["status"],
                "confidence_score": onset_res["confidence_score"],
                "onset_probability_pct": round(onset_res["confidence_score"] * 100, 1),
                "threshold_rule": onset_res.get("threshold_rule", "IMD-referenced monsoon onset criteria adapted within the VarshaSetu hyperlocal forecasting framework: 2 days rain ≥2.5mm + 850hPa wind ≥7.7m/s + OLR ≤200W/m²"),
                "threshold_status": onset_res.get("threshold_status", "NOT MET"),
                "threshold_config": onset_res.get("threshold_config", {}),
                "expected_onset_window": expected_onset_window,
                "is_false_alarm": onset_res.get("is_false_alarm", False),
                "normal_onset_date": location_meta["normal_onset_date"],
                "reasons": onset_res["reasons"],
                "methodology_note": "IMD's operational onset criteria are defined for declaration of southwest monsoon onset over Kerala and its advance. VarshaSetu uses these meteorological indicators as reference features within its hyperlocal probabilistic assessment; this dashboard does not represent an official IMD onset declaration."
            },
            "active_monsoon_outlook": {
                "expected_active_duration_days": spell_analysis["active_spell"]["expected_duration_days"],
                "duration_display": spell_analysis["active_spell"]["duration_display"],
                "expected_window": spell_analysis["active_spell"]["window"],
                "probability": active_prob,
                "probability_pct": round(active_prob * 100, 1),
                "status": active_status,
                "has_duration_estimate": spell_analysis["active_spell"]["has_estimate"]
            },
            "break_spell_outlook": {
                "risk_level": break_res["risk_level"],
                "probability": break_prob,
                "probability_pct": round(break_prob * 100, 1),
                "projected_consecutive_dry_days": break_res["max_consecutive_dry_days"],
                "expected_break_duration_days": spell_analysis["break_spell"]["expected_duration_days"],
                "duration_display": spell_analysis["break_spell"]["duration_display"],
                "expected_window": spell_analysis["break_spell"]["window"],
                "has_duration_estimate": spell_analysis["break_spell"]["has_estimate"],
                "is_break_active": break_res["is_break_active"],
                "uncertainty_interval": [
                    round(max(0.0, break_prob - (h_info["uncertainty_pct"] / 100.0)), 2),
                    round(min(1.0, break_prob + (h_info["uncertainty_pct"] / 100.0)), 2)
                ]
            },
            "rainfall_anomaly_outlook": anomaly_res,
            "heavy_rainfall_risk": heavy_rain_res,
            "timeline": timeline
        }

    def _generate_horizon_timeline(
        self,
        location: Dict[str, Any],
        horizon_days: int,
        scenario: Optional[str]
    ) -> List[Dict[str, Any]]:
        timeline = []
        today = datetime.date.today()

        for d in range(horizon_days):
            day_date = today + datetime.timedelta(days=d)
            if scenario == "break_spell":
                rain = 0.0 if d not in [3, 9] else 0.4
                t_max = 35.5 + min(3.0, d * 0.25)
                humidity = max(38.0, 55.0 - d * 1.5)
                olr = min(265.0, 240.0 + d * 2.0)
                wind = 4.0
                soil = max(18.0, 52.0 - d * 3.2)
            elif scenario == "onset_active":
                rain = round(16.0 + 8.0 * float(np.sin(d)), 1)
                t_max = 28.5
                humidity = 88.0
                olr = 175.0
                wind = 11.5
                soil = min(85.0, 68.0 + d * 2.0)
            elif scenario == "pre_monsoon":
                rain = 25.0 if d == 0 else 0.0
                t_max = 38.0
                humidity = 50.0
                olr = 230.0
                wind = 4.2
                soil = max(20.0, 36.0 - d * 3.0)
            else:
                rain = round(max(0.0, 8.0 + 6.0 * float(np.sin(d * 0.8))), 1)
                t_max = 31.0
                humidity = 72.0
                olr = 195.0
                wind = 8.5
                soil = 64.0

            timeline.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "day_offset": d + 1,
                "rainfall_mm": float(rain),
                "temp_max_c": float(round(t_max, 1)),
                "humidity_pct": float(round(humidity, 1)),
                "olr_wm2": float(round(olr, 1)),
                "zonal_wind_850hpa_ms": float(round(wind, 1)),
                "soil_moisture_pct": float(round(soil, 1)),
                "is_dry_day": bool(rain < 2.5)
            })

        return timeline

    def _record_forecast_run(
        self,
        location_id: str,
        horizon_days: int,
        onset_status: str,
        onset_prob: float,
        dry_spell_days: int,
        break_prob: float,
        anomaly_pct: float,
        heavy_risk: str,
        validity_start: str,
        validity_end: str
    ):
        try:
            conn = get_db_connection()
            conn.execute(
                """
                INSERT INTO forecast_runs
                (location_id, forecast_horizon_days, model_version, onset_status, onset_probability,
                 dry_spell_days, break_probability, rainfall_anomaly_pct, heavy_rain_risk,
                 validity_start, validity_end, data_provenance, is_demonstration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    location_id, horizon_days, "SIH26086-v1.0-Hybrid", onset_status, onset_prob,
                    dry_spell_days, break_prob, anomaly_pct, heavy_risk,
                    validity_start, validity_end, "IMD-Rules+RandomForest"
                )
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

pipeline = MonsoonForecastPipeline()
