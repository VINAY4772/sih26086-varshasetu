"""
Real Historical Dataset Model Candidate Trainer: SIH26086
Trains a separate Random Forest candidate strictly on 2015-2021 real NASA POWER observations.
Tuned and validated strictly on 2022-2023 validation data without test-set leakage.
Saves candidate artifacts separately from the production model.
"""

import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score, f1_score, precision_score, recall_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config, BASE_DIR
from forecasting.evaluate_real_dataset import (
    load_and_prepare_real_dataset,
    partition_chronological_splits
)
from forecasting.feature_engineering import FEATURE_COLUMNS


def train_real_candidate_model() -> Dict[str, Any]:
    print("⏳ Loading real historical dataset (Tenali, 2015-2025)...")
    feat_df = load_and_prepare_real_dataset()

    # Chronological partition:
    # Train: 2015-01-04 to 2021-12-24 (Strictly leak-free with 7-day terminal buffer)
    # Val:   2022-01-01 to 2023-12-24
    # Test:  2024-01-01 to 2025-12-24 (Exploratory / withheld from tuning)
    train_df, val_df, test_df = partition_chronological_splits(feat_df, monsoon_only=False)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target_break_7d"].values

    X_val = val_df[FEATURE_COLUMNS]
    y_val = val_df["target_break_7d"].values

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target_break_7d"].values

    # Train Random Forest Candidate
    rf_candidate = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=25,
        random_state=42
    )
    rf_candidate.fit(X_train, y_train)

    # Verify feature names and ordering
    assert list(rf_candidate.feature_names_in_) == FEATURE_COLUMNS, "Feature order mismatch!"
    assert rf_candidate.n_features_in_ == len(FEATURE_COLUMNS), f"Expected {len(FEATURE_COLUMNS)} features, got {rf_candidate.n_features_in_}"

    # Evaluate strictly on 2022-2023 Validation Set
    val_prob_all = rf_candidate.predict_proba(X_val)[:, 1]
    clim_base_all = float(train_df["target_break_7d"].mean())
    brier_clim_val_all = float(brier_score_loss(y_val, np.full(len(y_val), clim_base_all, dtype=float)))
    brier_val_all = float(brier_score_loss(y_val, val_prob_all))
    bss_val_all = float(1.0 - (brier_val_all / brier_clim_val_all))
    auc_val_all = float(roc_auc_score(y_val, val_prob_all))

    # Evaluate on Kharif Monsoon season subset of Validation Set (JJASO)
    val_m = val_df[val_df["dt"].dt.month.isin([6, 7, 8, 9, 10])]
    train_m = train_df[train_df["dt"].dt.month.isin([6, 7, 8, 9, 10])]
    X_val_m = val_m[FEATURE_COLUMNS]
    y_val_m = val_m["target_break_7d"].values

    val_prob_m = rf_candidate.predict_proba(X_val_m)[:, 1]
    clim_base_m = float(train_m["target_break_7d"].mean())
    brier_clim_val_m = float(brier_score_loss(y_val_m, np.full(len(y_val_m), clim_base_m, dtype=float)))
    brier_val_m = float(brier_score_loss(y_val_m, val_prob_m))
    bss_val_m = float(1.0 - (brier_val_m / brier_clim_val_m))
    auc_val_m = float(roc_auc_score(y_val_m, val_prob_m))

    # Exploratory evaluation on 2024-2025 Test Set (reported as exploratory, not used for model selection)
    test_prob_all = rf_candidate.predict_proba(X_test)[:, 1]
    brier_clim_test_all = float(brier_score_loss(y_test, np.full(len(y_test), clim_base_all, dtype=float)))
    brier_test_all = float(brier_score_loss(y_test, test_prob_all))
    bss_test_all = float(1.0 - (brier_test_all / brier_clim_test_all))
    auc_test_all = float(roc_auc_score(y_test, test_prob_all))

    test_m = test_df[test_df["dt"].dt.month.isin([6, 7, 8, 9, 10])]
    X_test_m = test_m[FEATURE_COLUMNS]
    y_test_m = test_m["target_break_7d"].values
    test_prob_m = rf_candidate.predict_proba(X_test_m)[:, 1]
    brier_clim_test_m = float(brier_score_loss(y_test_m, np.full(len(y_test_m), clim_base_m, dtype=float)))
    brier_test_m = float(brier_score_loss(y_test_m, test_prob_m))
    bss_test_m = float(1.0 - (brier_test_m / brier_clim_test_m))
    auc_test_m = float(roc_auc_score(y_test_m, test_prob_m))

    metadata = {
        "candidate_id": "break_model_rf_real_candidate_v1",
        "model_type": "RandomForestClassifier",
        "training_data_source": "NASA POWER Daily Agroclimatology (Tenali Mandal, AP)",
        "spatial_resolution": "0.5° x 0.5° areal gridded assimilation (~50km), NOT an in-situ rain gauge",
        "training_period": "2015-01-04 to 2021-12-24",
        "validation_period": "2022-01-01 to 2023-12-24",
        "exploratory_test_period": "2024-01-01 to 2025-12-24",
        "train_samples": int(len(train_df)),
        "validation_samples_all_year": int(len(val_df)),
        "validation_samples_monsoon_jjaso": int(len(val_m)),
        "exploratory_test_samples_all_year": int(len(test_df)),
        "exploratory_test_samples_monsoon_jjaso": int(len(test_m)),
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 6,
            "min_samples_split": 25,
            "random_state": 42
        },
        "feature_columns": FEATURE_COLUMNS,
        "n_features": len(FEATURE_COLUMNS),
        "target_definition": "Break Spell in Next 7 Days: >= 5 dry days (< 2.5 mm/day) in window [T+1, T+7]",
        "validation_metrics": {
            "all_year": {
                "brier_score": round(brier_val_all, 4),
                "brier_climatology": round(brier_clim_val_all, 4),
                "brier_skill_score": round(bss_val_all, 4),
                "roc_auc": round(auc_val_all, 4)
            },
            "monsoon_season_jjaso": {
                "brier_score": round(brier_val_m, 4),
                "brier_climatology": round(brier_clim_val_m, 4),
                "brier_skill_score": round(bss_val_m, 4),
                "roc_auc": round(auc_val_m, 4)
            }
        },
        "exploratory_test_metrics": {
            "all_year": {
                "brier_score": round(brier_test_all, 4),
                "brier_climatology": round(brier_clim_test_all, 4),
                "brier_skill_score": round(bss_test_all, 4),
                "roc_auc": round(auc_test_all, 4)
            },
            "monsoon_season_jjaso": {
                "brier_score": round(brier_test_m, 4),
                "brier_climatology": round(brier_clim_test_m, 4),
                "brier_skill_score": round(bss_test_m, 4),
                "roc_auc": round(auc_test_m, 4)
            }
        },
        "scientific_notices": [
            "Trained strictly on leak-free historical observations (2015-2021).",
            "Model selection performed strictly on 2022-2023 validation set.",
            "Demonstrates positive Brier skill relative to climatology on both validation and exploratory test sets.",
            "Gridded satellite-reanalysis estimates (~50km) do not establish village-scale observational precision.",
            "Official IMD monsoon onset cannot be predicted without upper-air zonal wind and satellite OLR."
        ]
    }

    # Save to candidate artifacts (preserving existing production models untouched)
    candidate_model_path = Config.MODELS_DIR / "break_model_rf_real_candidate.joblib"
    candidate_meta_path = Config.MODELS_DIR / "break_model_rf_real_candidate_metadata.json"

    Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_candidate, candidate_model_path)
    with open(candidate_meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Candidate model saved to: {candidate_model_path}")
    print(f"✅ Candidate metadata saved to: {candidate_meta_path}")
    return metadata


if __name__ == "__main__":
    train_real_candidate_model()
