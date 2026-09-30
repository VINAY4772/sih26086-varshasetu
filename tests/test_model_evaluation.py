"""
Automated Test Suite for Historical Real Data Model & Baseline Evaluation: SIH26086
Verifies leak-free chronological partitioning, target computation without forward leakage,
and mathematical properties of Brier Score, Brier Skill Score, and baseline comparators.
"""

import pytest
import json
import numpy as np
import pandas as pd
from pathlib import Path

from config import Config, BASE_DIR
from forecasting.evaluate_real_dataset import (
    load_and_prepare_real_dataset,
    partition_chronological_splits,
    compute_metrics,
    run_full_evaluation
)

REPORT_PATH = BASE_DIR / "docs" / "real_data_evaluation_report.json"
REAL_CSV = Config.DATA_DIR / "real" / "tenali_nasa_power_2015_2025.csv"


def test_real_dataset_chronological_splits_leak_free_boundaries():
    """
    Verifies that the chronological train/val/test splits have non-overlapping boundaries
    with a mandatory 7-day terminal buffer to prevent forward target window leakage.
    """
    feat_df = load_and_prepare_real_dataset()
    train_df, val_df, test_df = partition_chronological_splits(feat_df, monsoon_only=False)

    # Train starts on 2015-01-04 (accounting for 3-day initial lag warm-up: rain_lag_1, 2, 3)
    # and ends on or before 2021-12-24 (7-day buffer before 2022-01-01)
    assert train_df["dt"].min() == pd.Timestamp("2015-01-04")
    assert train_df["dt"].max() <= pd.Timestamp("2021-12-24")

    # Val: 2022-01-01 to 2023-12-24
    assert val_df["dt"].min() >= pd.Timestamp("2022-01-01")
    assert val_df["dt"].max() <= pd.Timestamp("2023-12-24")

    # Test: 2024-01-01 to 2025-12-24
    assert test_df["dt"].min() >= pd.Timestamp("2024-01-01")
    assert test_df["dt"].max() <= pd.Timestamp("2025-12-24")

    # Strict non-overlapping buffer:
    # Train target window (T+1 .. T+7) for last train row (2021-12-24) ends on 2021-12-31,
    # strictly BEFORE the validation period begins on 2022-01-01!
    train_last_fwd_date = train_df["dt"].max() + pd.Timedelta(days=7)
    assert train_last_fwd_date < val_df["dt"].min(), "Target window from Train leaks into Validation split!"

    val_last_fwd_date = val_df["dt"].max() + pd.Timedelta(days=7)
    assert val_last_fwd_date < test_df["dt"].min(), "Target window from Validation leaks into Test split!"


def test_target_break_spell_leak_free_calculation():
    """
    Verifies that target_break_7d is calculated strictly on forward days [T+1, T+7]
    and is undefined (NaN) on the last 7 days of the series.
    """
    feat_df = load_and_prepare_real_dataset()

    # The last 7 days cannot evaluate a full 7-day forward window
    last_7_targets = feat_df["target_break_7d"].iloc[-7:]
    assert last_7_targets.isna().all(), "Trailing rows should have NaN forward targets!"

    # All preceding rows must have valid 0 or 1 labels
    preceding_targets = feat_df["target_break_7d"].iloc[:-7]
    assert preceding_targets.notna().all()
    assert set(preceding_targets.unique()).issubset({0, 1})


def test_baseline_metrics_mathematical_properties():
    """
    Verifies mathematical bounds: Brier Score in [0, 1],
    BSS formula 1 - (BS_model / BS_clim), and ROC-AUC in [0, 1].
    """
    y_true = np.array([1, 1, 0, 0, 1, 0, 0, 0])
    clim_rate = float(y_true.mean())
    y_clim = np.full_like(y_true, fill_value=clim_rate, dtype=float)

    clim_brier = float(np.mean((y_clim - y_true) ** 2))
    assert 0.0 <= clim_brier <= 1.0

    # Perfect forecast: Brier = 0, BSS = 1.0
    perfect_metrics = compute_metrics(y_true, y_true.astype(float), clim_brier)
    assert perfect_metrics["brier_score"] == 0.0
    assert perfect_metrics["brier_skill_score"] == 1.0
    assert perfect_metrics["roc_auc"] == 1.0

    # Constant climatology forecast: BSS = 0.0
    clim_metrics = compute_metrics(y_true, y_clim, clim_brier)
    assert clim_metrics["brier_skill_score"] == 0.0


def test_evaluation_report_json_artifact_and_scientific_provenance():
    """
    Verifies that the evaluation report artifact exists, contains both all-year
    and monsoon season breakdowns, and explicitly declares NASA POWER as gridded reanalysis.
    """
    if not REPORT_PATH.exists():
        run_full_evaluation()

    assert REPORT_PATH.exists()
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert "scientific_nature" in report
    assert "gridded" in report["scientific_nature"].lower()
    assert "not an in-situ" in report["scientific_nature"].lower()

    assert "all_year_evaluation" in report
    assert "monsoon_season_evaluation" in report

    test_eval = report["monsoon_season_evaluation"]["evaluations"]["test_split"]
    assert "climatology_baseline" in test_eval
    assert "persistence_baseline" in test_eval
    assert "production_rf_model" in test_eval
    assert "real_trained_rf_benchmark" in test_eval

    # Climatology baseline Brier Score is positive
    assert test_eval["climatology_baseline"]["brier_score"] > 0.0
