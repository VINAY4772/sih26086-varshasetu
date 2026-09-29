import pytest
import pandas as pd
import tempfile
from pathlib import Path

from forecasting.data_ingestion import DataIngestionPipeline
from database.initialise import initialise_database

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
        db_path = tmp.name
        initialise_database(db_path)
        yield db_path

def test_ingestion_valid_csv(temp_db):
    pipeline = DataIngestionPipeline(temp_db)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("location_id,date,rainfall_mm,temp_max_c\n")
        f.write("tel_wgl_dharmasagar,2025-06-01,15.5,32.0\n")
        f.write("tel_wgl_dharmasagar,2025-06-02,25.0,30.5\n")
        csv_path = f.name

    result = pipeline.ingest_csv_to_db(csv_path)
    assert result["status"] == "success"
    assert result["inserted_records"] == 2
    Path(csv_path).unlink()

def test_ingestion_missing_required_column(temp_db):
    pipeline = DataIngestionPipeline(temp_db)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("location_id,date\n")  # Missing rainfall_mm
        f.write("tel_wgl_dharmasagar,2025-06-01\n")
        csv_path = f.name

    with pytest.raises(ValueError, match="Missing mandatory column"):
        pipeline.load_and_validate_csv(csv_path)
    Path(csv_path).unlink()

def test_ingestion_clamping_and_duplicates(temp_db):
    pipeline = DataIngestionPipeline(temp_db)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("location_id,date,rainfall_mm\n")
        f.write("tel_wgl_dharmasagar,2025-06-01,-5.0\n")  # Negative rainfall
        f.write("tel_wgl_dharmasagar,2025-06-01,12.0\n")  # Duplicate date (should keep last)
        csv_path = f.name

    df, meta = pipeline.load_and_validate_csv(csv_path)
    assert meta["dropped_duplicates"] == 1
    assert (df["rainfall_mm"] >= 0).all()
    Path(csv_path).unlink()
