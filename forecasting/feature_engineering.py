import pandas as pd
import numpy as np
from typing import List

FEATURE_COLUMNS = [
    "rain_lag_1",
    "rain_lag_2",
    "rain_lag_3",
    "rain_roll_7d",
    "rain_roll_14d",
    "wet_days_7d",
    "consecutive_dry_days",
    "temp_max_c",
    "humidity_pct",
    "olr_wm2",
    "zonal_wind_850hpa_ms",
    "enso_nino34",
    "iod_dmi",
    "mjo_amplitude",
    "day_of_year",
    "latitude",
    "elevation_m"
]

def engineer_features(df: pd.DataFrame, locations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs leak-free feature vectors for temporal machine-learning models.
    Uses .transform() on groupby to preserve the single-level index across pandas versions.
    """
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values(by=["location_id", "date"]).reset_index(drop=True)

    # Merge location metadata (latitude, elevation)
    loc_meta = locations_df[["id", "latitude", "elevation_m"]].rename(columns={"id": "location_id"})
    data = pd.merge(data, loc_meta, on="location_id", how="left")

    # Time/seasonal features
    data["day_of_year"] = data["date"].dt.dayofyear

    # Lagged rainfall features (strictly preceding days)
    data["rain_lag_1"] = data.groupby("location_id")["rainfall_mm"].shift(1)
    data["rain_lag_2"] = data.groupby("location_id")["rainfall_mm"].shift(2)
    data["rain_lag_3"] = data.groupby("location_id")["rainfall_mm"].shift(3)

    # Rolling statistics over strictly historical window (shifted by 1 to prevent leakage)
    data["rain_roll_7d"] = data.groupby("location_id")["rainfall_mm"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=1).sum()
    )
    data["rain_roll_14d"] = data.groupby("location_id")["rainfall_mm"].transform(
        lambda s: s.shift(1).rolling(14, min_periods=1).sum()
    )

    data["is_wet_lag"] = (data.groupby("location_id")["rainfall_mm"].shift(1) >= 2.5).astype(float)
    data["wet_days_7d"] = data.groupby("location_id")["is_wet_lag"].transform(
        lambda s: s.rolling(7, min_periods=1).sum()
    )

    # Dry streak calculation on historical observations
    def calc_shifted_streak(s: pd.Series) -> pd.Series:
        shifted = s.shift(1).fillna(0)
        streak = []
        count = 0
        for val in shifted:
            if val < 2.5:
                count += 1
            else:
                count = 0
            streak.append(count)
        return pd.Series(streak, index=s.index)

    data["consecutive_dry_days"] = data.groupby("location_id")["rainfall_mm"].transform(calc_shifted_streak)

    # Impute missing climate indices if empty
    for col in ["enso_nino34", "iod_dmi", "mjo_amplitude"]:
        if col not in data.columns:
            data[col] = 0.0
        else:
            data[col] = data[col].fillna(0.0)

    # Impute missing atmospheric readings with seasonal medians
    for col in ["temp_max_c", "humidity_pct", "olr_wm2", "zonal_wind_850hpa_ms"]:
        if col in data.columns:
            median_val = data[col].dropna().median() if not data[col].dropna().empty else 0.0
            data[col] = data[col].fillna(median_val)
        else:
            data[col] = 0.0

    return data
