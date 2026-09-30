"""
Real Historical Dataset Model & Baseline Evaluation Module: SIH26086
Evaluates the existing production Random Forest model and standard meteorological baselines
(Climatology and Persistence) on the verified multi-year NASA POWER archive for Tenali, AP (2015–2025).

Strictly enforces chronological partitioning without cross-split boundary target leakage:
- Train: 2015-01-01 to 2021-12-24 (Target window ends on or before 2021-12-31)
- Validation: 2022-01-01 to 2023-12-24 (Target window ends on or before 2023-12-31)
- Out-of-Time Test: 2024-01-01 to 2025-12-24 (Target window ends on or before 2025-12-31)
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score, f1_score, precision_score, recall_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config, BASE_DIR
from database.initialise import get_db_connection
from forecasting.feature_engineering import engineer_features, FEATURE_COLUMNS


def load_and_prepare_real_dataset(csv_path: str = None) -> pd.DataFrame:
    target_csv = Path(csv_path) if csv_path else (Config.DATA_DIR / "real" / "tenali_nasa_power_2015_2025.csv")
    if not target_csv.exists():
        raise FileNotFoundError(f"Real historical dataset not found at: {target_csv}")

    df = pd.read_csv(target_csv)
    conn = get_db_connection()
    loc_df = pd.read_sql_query("SELECT * FROM locations", conn)
    conn.close()

    feat_df = engineer_features(df, loc_df)
    feat_df["dt"] = pd.to_datetime(feat_df["date"])
    feat_df = feat_df.sort_values("dt").reset_index(drop=True)

    # Deterministic leak-free forward 7-day target (days T+1 to T+7)
    # Target = 1 if at least 5 dry days (< 2.5 mm) in forward 7 days
    is_dry = (feat_df["rainfall_mm"] < 2.5).astype(int)
    fwd_targets = []
    n = len(feat_df)
    for i in range(n):
        if i + 7 < n:
            fwd_window = is_dry.iloc[i + 1 : i + 8]
            fwd_targets.append(int(fwd_window.sum() >= 5))
        else:
            fwd_targets.append(np.nan)
    feat_df["target_break_7d"] = fwd_targets

    return feat_df


def partition_chronological_splits(
    feat_df: pd.DataFrame,
    monsoon_only: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Partitions dataset chronologically.
    To prevent target window leakage across split boundaries,
    the 7-day forward evaluation window for each split must terminate
    strictly on or before the split's end date.
    """
    valid_df = feat_df.dropna(subset=FEATURE_COLUMNS + ["target_break_7d"]).copy()
    valid_df["target_break_7d"] = valid_df["target_break_7d"].astype(int)

    if monsoon_only:
        # Kharif Monsoon Season: June 1 to October 31
        valid_df = valid_df[valid_df["dt"].dt.month.isin([6, 7, 8, 9, 10])].copy()

    # Split boundaries with 7-day buffer to prevent cross-boundary target window leakage:
    train_df = valid_df[(valid_df["dt"] >= "2015-01-01") & (valid_df["dt"] <= "2021-12-24")].copy()
    val_df   = valid_df[(valid_df["dt"] >= "2022-01-01") & (valid_df["dt"] <= "2023-12-24")].copy()
    test_df  = valid_df[(valid_df["dt"] >= "2024-01-01") & (valid_df["dt"] <= "2025-12-24")].copy()

    return train_df, val_df, test_df


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, brier_clim: float) -> Dict[str, Any]:
    y_pred = (y_prob >= 0.5).astype(int)
    brier = float(brier_score_loss(y_true, y_prob))
    bss = float(1.0 - (brier / max(1e-6, brier_clim)))
    auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))

    return {
        "brier_score": round(brier, 4),
        "brier_skill_score": round(bss, 4),
        "roc_auc": round(auc, 4),
        "f1_score": round(f1, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4)
    }


def run_full_evaluation(csv_path: str = None) -> Dict[str, Any]:
    feat_df = load_and_prepare_real_dataset(csv_path)

    # Load existing production model
    prod_model_path = Config.MODELS_DIR / "break_model_rf.joblib"
    prod_model = joblib.load(prod_model_path) if prod_model_path.exists() else None

    report = {
        "dataset_name": "Tenali Mandal Multi-Year Real Weather Archive (NASA POWER)",
        "location": "Tenali Mandal, Guntur District, Andhra Pradesh (16.2437°N, 80.6400°E)",
        "scientific_nature": "Areal gridded assimilation estimate (0.5° x 0.5° resolution, ~50km) from NASA GEOS-5 / MERRA-2. NOT an in-situ rain-gauge observation.",
        "target_definition": "Break Spell in Next 7 Days: >= 5 dry days (< 2.5 mm/day) in window [T+1, T+7]",
        "leakage_safeguard": "Forward 7-day target window truncated 7 days prior to split boundary; past features shifted >= 1 day.",
        "all_year_evaluation": {},
        "monsoon_season_evaluation": {}
    }

    for mode, monsoon_flag in [("all_year_evaluation", False), ("monsoon_season_evaluation", True)]:
        train_df, val_df, test_df = partition_chronological_splits(feat_df, monsoon_only=monsoon_flag)

        clim_rate = float(train_df["target_break_7d"].mean())
        mode_res = {
            "splits": {
                "train_period": "2015-01-01 to 2021-12-24",
                "train_samples": len(train_df),
                "train_prevalence": round(clim_rate, 4),
                "val_period": "2022-01-01 to 2023-12-24",
                "val_samples": len(val_df),
                "val_prevalence": round(float(val_df["target_break_7d"].mean()), 4),
                "test_period": "2024-01-01 to 2025-12-24",
                "test_samples": len(test_df),
                "test_prevalence": round(float(test_df["target_break_7d"].mean()), 4),
            },
            "evaluations": {}
        }

        # Train a benchmark real-data model on train split for comparison
        real_rf = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_split=15, random_state=42)
        real_rf.fit(train_df[FEATURE_COLUMNS], train_df["target_break_7d"])

        for split_label, sdata in [("val_split", val_df), ("test_split", test_df)]:
            y_true = sdata["target_break_7d"].values
            X = sdata[FEATURE_COLUMNS]

            # Climatology Baseline
            clim_brier = float(brier_score_loss(y_true, np.full_like(y_true, fill_value=clim_rate, dtype=float)))
            clim_metrics = {
                "base_rate": round(clim_rate, 4),
                "brier_score": round(clim_brier, 4),
                "brier_skill_score": 0.0,
                "roc_auc": 0.5
            }

            # Persistence Baseline (recent dry streak >= 4 days)
            pers_prob = (sdata["consecutive_dry_days"] >= 4).astype(float).values
            pers_metrics = compute_metrics(y_true, pers_prob, clim_brier)

            # Existing Production Model
            if prod_model:
                prod_prob = prod_model.predict_proba(X)[:, 1]
                prod_metrics = compute_metrics(y_true, prod_prob, clim_brier)
            else:
                prod_metrics = None

            # Real Data Fit Benchmark
            real_prob = real_rf.predict_proba(X)[:, 1]
            real_metrics = compute_metrics(y_true, real_prob, clim_brier)

            mode_res["evaluations"][split_label] = {
                "samples": len(sdata),
                "event_prevalence": round(float(y_true.mean()), 4),
                "climatology_baseline": clim_metrics,
                "persistence_baseline": pers_metrics,
                "production_rf_model": prod_metrics,
                "real_trained_rf_benchmark": real_metrics
            }

        report[mode] = mode_res

    # Save to docs
    out_path = BASE_DIR / "docs" / "real_data_evaluation_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = run_full_evaluation()
    print("✅ Completed Real Historical Dataset Evaluation.")
    print(f"Report saved to: {BASE_DIR / 'docs' / 'real_data_evaluation_report.json'}")
    print("\n--- OUT-OF-TIME TEST SET (2024-2025) SUMMARY (MONSOON JJASO) ---")
    test_eval = rep["monsoon_season_evaluation"]["evaluations"]["test_split"]
    print(f"Samples: {test_eval['samples']} | Event Prevalence: {test_eval['event_prevalence']}")
    print(f"Climatology Baseline Brier: {test_eval['climatology_baseline']['brier_score']}")
    print(f"Persistence Baseline: Brier={test_eval['persistence_baseline']['brier_score']}, BSS={test_eval['persistence_baseline']['brier_skill_score']}, AUC={test_eval['persistence_baseline']['roc_auc']}")
    print(f"Production Model:     Brier={test_eval['production_rf_model']['brier_score']}, BSS={test_eval['production_rf_model']['brier_skill_score']}, AUC={test_eval['production_rf_model']['roc_auc']}")
    print(f"Real Data Fit Model:  Brier={test_eval['real_trained_rf_benchmark']['brier_score']}, BSS={test_eval['real_trained_rf_benchmark']['brier_skill_score']}, AUC={test_eval['real_trained_rf_benchmark']['roc_auc']}")
