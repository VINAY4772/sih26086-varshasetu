import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from database.initialise import get_db_connection

REQUIRED_COLUMNS = [
    "location_id",
    "date",
    "rainfall_mm"
]

OPTIONAL_COLUMNS = [
    "temp_max_c",
    "temp_min_c",
    "humidity_pct",
    "wind_speed_ms",
    "wind_dir_deg",
    "olr_wm2",
    "zonal_wind_850hpa_ms",
    "soil_moisture_pct",
    "enso_nino34",
    "iod_dmi",
    "mjo_amplitude",
    "data_source_id"
]

class DataIngestionPipeline:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH

    def load_and_validate_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found at: {file_path}")

        df = pd.read_csv(file_path)
        metadata = {
            "source_file": str(path.name),
            "initial_rows": len(df),
            "dropped_missing_required": 0,
            "dropped_duplicates": 0,
            "clamped_values": 0,
            "valid_rows": 0,
            "warnings": []
        }

        # 1. Validate required columns
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Missing mandatory column: '{col}' in input data.")

        # 2. Date parsing and validation
        try:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        except Exception as e:
            raise ValueError(f"Date parsing failed: {e}")

        # 3. Handle duplicates
        init_len = len(df)
        df = df.drop_duplicates(subset=["location_id", "date"], keep="last")
        metadata["dropped_duplicates"] = init_len - len(df)

        # 4. Handle missing values
        init_len = len(df)
        df = df.dropna(subset=["location_id", "date", "rainfall_mm"])
        metadata["dropped_missing_required"] = init_len - len(df)

        # 5. Unit validation and physical sanity checks
        # Rainfall >= 0
        neg_rain = (df["rainfall_mm"] < 0).sum()
        if neg_rain > 0:
            df["rainfall_mm"] = df["rainfall_mm"].clip(lower=0.0)
            metadata["clamped_values"] += int(neg_rain)
            metadata["warnings"].append(f"Clamped {neg_rain} negative rainfall values to 0.0 mm.")

        # Max extreme rainfall clamp (e.g., > 1200mm/day is likely a sensor error)
        extreme_rain = (df["rainfall_mm"] > 1200.0).sum()
        if extreme_rain > 0:
            df["rainfall_mm"] = df["rainfall_mm"].clip(upper=1200.0)
            metadata["clamped_values"] += int(extreme_rain)
            metadata["warnings"].append(f"Clamped {extreme_rain} extreme rainfall values (>1200mm).")

        # Sanitize optional variables if present
        if "humidity_pct" in df.columns:
            df["humidity_pct"] = df["humidity_pct"].clip(lower=0.0, upper=100.0)

        if "temp_max_c" in df.columns:
            df["temp_max_c"] = df["temp_max_c"].clip(lower=-10.0, upper=60.0)

        if "temp_min_c" in df.columns:
            df["temp_min_c"] = df["temp_min_c"].clip(lower=-20.0, upper=50.0)

        if "olr_wm2" in df.columns:
            df["olr_wm2"] = df["olr_wm2"].clip(lower=60.0, upper=400.0)

        if "soil_moisture_pct" in df.columns:
            df["soil_moisture_pct"] = df["soil_moisture_pct"].clip(lower=0.0, upper=100.0)

        if "data_source_id" not in df.columns:
            df["data_source_id"] = "synthetic_demo_feed"

        # 6. Validate location_id against database
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM locations")
        valid_loc_ids = {row[0] for row in cur.fetchall()}
        conn.close()

        unknown_locs = set(df["location_id"]) - valid_loc_ids
        if unknown_locs:
            metadata["warnings"].append(
                f"Unknown location IDs found: {unknown_locs}. Filtered out."
            )
            df = df[df["location_id"].isin(valid_loc_ids)]

        metadata["valid_rows"] = len(df)
        return df, metadata

    def ingest_csv_to_db(self, file_path: str) -> Dict[str, Any]:
        df, meta = self.load_and_validate_csv(file_path)
        if df.empty:
            return {"status": "error", "message": "No valid rows found after validation.", "metadata": meta}

        conn = get_db_connection(self.db_path)
        cur = conn.cursor()

        # Insert or replace observations
        cols_present = [c for c in df.columns if c in REQUIRED_COLUMNS or c in OPTIONAL_COLUMNS]
        placeholders = ", ".join(["?"] * len(cols_present))
        col_names = ", ".join(cols_present)

        insert_sql = f"""
            INSERT OR REPLACE INTO observations ({col_names})
            VALUES ({placeholders})
        """

        records = df[cols_present].to_records(index=False).tolist()
        cur.executemany(insert_sql, records)
        conn.commit()
        conn.close()

        meta["status"] = "success"
        meta["inserted_records"] = len(records)
        return meta

if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    sample_file = Config.SAMPLE_DATA_DIR / "synthetic_weather_sample.csv"
    res = pipeline.ingest_csv_to_db(str(sample_file))
    print("Ingestion Result:", res)
