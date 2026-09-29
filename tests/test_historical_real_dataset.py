"""
Real Historical Dataset Validation Test Suite: SIH26086
Verifies the integrity, temporal continuity, physical ranges,
and chronological partitioning of the downloaded Tenali, AP NASA POWER archive (2015–2025).
"""

import pytest
import json
import csv
from pathlib import Path
import datetime
import pandas as pd
from config import Config

REAL_DATA_DIR = Config.DATA_DIR / "real"
JSON_PATH = REAL_DATA_DIR / "tenali_nasa_power_2015_2025.json"
CSV_PATH = REAL_DATA_DIR / "tenali_nasa_power_2015_2025.csv"

def test_tenali_dataset_files_exist_and_schema():
    """Verifies that the multi-year real historical files exist with valid schema."""
    assert JSON_PATH.exists(), f"Missing JSON archive: {JSON_PATH}"
    assert CSV_PATH.exists(), f"Missing CSV archive: {CSV_PATH}"

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["metadata"]
    assert meta["location_id"] == "ap_gnr_tenali"
    assert meta["is_synthetic"] is False
    assert "gridded" in meta["scientific_nature"].lower()
    assert "validation_summary" in meta

    records = data["records"]
    assert len(records) == 4018
    first = records[0]
    assert "date" in first
    assert "rainfall_mm" in first
    assert "temp_max_c" in first
    assert "humidity_pct" in first
    assert "missing_flag" in first
    assert first["data_source_id"] == "nasa_power_daily"

def test_tenali_dataset_date_continuity():
    """Verifies zero gaps and zero duplicate dates across 11 calendar years (2015-2025)."""
    df = pd.read_csv(CSV_PATH)
    assert len(df) == 4018

    # Verify duplicate dates
    duplicate_count = df["date"].duplicated().sum()
    assert duplicate_count == 0, f"Found {duplicate_count} duplicate dates!"

    # Verify temporal continuity
    dates = pd.to_datetime(df["date"])
    expected_range = pd.date_range(start="2015-01-01", end="2025-12-31", freq="D")
    assert len(dates) == len(expected_range)
    assert (dates.values == expected_range.values).all(), "Temporal gap detected in date series!"

def test_tenali_dataset_physical_ranges():
    """Verifies physical bounding of all meteorological variables."""
    df = pd.read_csv(CSV_PATH)

    # Valid rainfall >= 0 mm
    assert (df["rainfall_mm"] >= 0.0).all()
    assert df["rainfall_mm"].max() < 500.0  # Max in Tenali was 129.4 mm during 2020 cyclone

    # Valid temperature in tropical range
    assert (df["temp_max_c"] >= 15.0).all()
    assert (df["temp_max_c"] <= 50.0).all()

    # Valid relative humidity 0-100%
    assert (df["humidity_pct"] >= 10.0).all()
    assert (df["humidity_pct"] <= 100.0).all()

def test_tenali_chronological_splits_integrity():
    """Verifies chronological train/val/test partitioning with zero data leakage."""
    df = pd.read_csv(CSV_PATH)
    df["dt"] = pd.to_datetime(df["date"])

    train_df = df[df["dt"] < "2022-01-01"]
    val_df = df[(df["dt"] >= "2022-01-01") & (df["dt"] < "2024-01-01")]
    test_df = df[df["dt"] >= "2024-01-01"]

    # 7 years train (2015-2021)
    assert len(train_df) == 2557
    # 2 years val (2022-2023)
    assert len(val_df) == 730
    # 2 years test (2024-2025, 2024 is leap year)
    assert len(test_df) == 731
    # Total equals 4018
    assert len(train_df) + len(val_df) + len(test_df) == 4018

    # Non-overlapping boundary verification
    assert train_df["dt"].max() < val_df["dt"].min()
    assert val_df["dt"].max() < test_df["dt"].min()

def test_tenali_dry_spell_event_label_calculation():
    """Verifies deterministic calculation of dry days and forward break spells on real data."""
    df = pd.read_csv(CSV_PATH)

    # Standard meteorological dry day definition (rain < 2.5 mm)
    is_dry = (df["rainfall_mm"] < 2.5).astype(int)
    wet_days = (df["rainfall_mm"] >= 2.5).sum()
    dry_days = is_dry.sum()
    assert wet_days + dry_days == len(df)
    assert wet_days == 1092
    assert dry_days == 2926

    # Verify forward 7-day break spell calculation (at least 5 dry days in next 7 days)
    # Computed strictly forward in time without future leakage beyond the 7-day window
    fwd_7d_dry = pd.Series(
        [is_dry.iloc[i+1 : i+8].sum() for i in range(len(is_dry) - 7)],
        index=df.index[:-7]
    )
    break_labels = (fwd_7d_dry >= 5)
    assert len(break_labels) == len(df) - 7
    assert set(break_labels.unique()).issubset({True, False})
