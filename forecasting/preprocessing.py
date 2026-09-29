import pandas as pd
import numpy as np
from typing import Optional

def compute_rolling_rainfall(df: pd.DataFrame, rain_col: str = "rainfall_mm") -> pd.DataFrame:
    """
    Computes cumulative rolling rainfall aggregations per location.
    Requires df sorted by location_id and date.
    """
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values(by=["location_id", "date"])

    # 3-day, 7-day, and 14-day rolling sums
    out["rain_roll_3d"] = out.groupby("location_id")[rain_col].transform(
        lambda s: s.rolling(window=3, min_periods=1).sum()
    )
    out["rain_roll_7d"] = out.groupby("location_id")[rain_col].transform(
        lambda s: s.rolling(window=7, min_periods=1).sum()
    )
    out["rain_roll_14d"] = out.groupby("location_id")[rain_col].transform(
        lambda s: s.rolling(window=14, min_periods=1).sum()
    )

    # 7-day wet day frequency (count of days >= 2.5mm)
    out["is_wet_day"] = (out[rain_col] >= 2.5).astype(int)
    out["wet_days_7d"] = out.groupby("location_id")["is_wet_day"].transform(
        lambda s: s.rolling(window=7, min_periods=1).sum()
    )

    # Dry day streak tracking
    def calc_dry_streak(series: pd.Series) -> pd.Series:
        streak = []
        count = 0
        for val in series:
            if val < 2.5:
                count += 1
            else:
                count = 0
            streak.append(count)
        return pd.Series(streak, index=series.index)

    out["consecutive_dry_days"] = out.groupby("location_id")[rain_col].transform(calc_dry_streak)

    # Rolling mean soil moisture if present
    if "soil_moisture_pct" in out.columns:
        out["soil_moist_mean_7d"] = out.groupby("location_id")["soil_moisture_pct"].transform(
            lambda s: s.rolling(window=7, min_periods=1).mean()
        )

    return out

def handle_missing_dates(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Identifies missing dates in a time-series per location and re-indexes
    with explicit NaN marking to prevent temporal misalignment.
    """
    out_dfs = []
    for loc_id, group in df.groupby("location_id"):
        group = group.copy()
        group["date"] = pd.to_datetime(group["date"])
        group = group.set_index("date").sort_index()

        # Generate full continuous date range
        full_idx = pd.date_range(start=group.index.min(), end=group.index.max(), freq=freq)
        reindexed = group.reindex(full_idx)
        reindexed["location_id"] = loc_id
        reindexed.index.name = "date"
        reindexed = reindexed.reset_index()
        out_dfs.append(reindexed)

    if not out_dfs:
        return df

    res = pd.concat(out_dfs, ignore_index=True)
    res["date"] = res["date"].dt.strftime("%Y-%m-%d")
    return res
