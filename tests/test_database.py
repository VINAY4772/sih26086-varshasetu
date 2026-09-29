import os
import sqlite3
import pytest
from pathlib import Path
import tempfile

from database.initialise import initialise_database, get_db_connection

def test_database_initialisation_and_tables():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
        db_path = tmp.name
        initialise_database(db_path)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        conn.close()

        expected = {"locations", "data_sources", "observations", "forecast_runs", "crop_advisories", "notification_logs"}
        assert expected.issubset(tables)

def test_database_seed_locations_and_sources():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
        db_path = tmp.name
        initialise_database(db_path)

        conn = get_db_connection(db_path)
        locations = conn.execute("SELECT * FROM locations").fetchall()
        sources = conn.execute("SELECT * FROM data_sources").fetchall()
        conn.close()

        assert len(locations) >= 8
        assert any(l["id"] == "tel_wgl_dharmasagar" for l in locations)
        assert any(s["id"] == "synthetic_demo_feed" for s in sources)
        assert any(s["is_synthetic"] == 1 for s in sources)
