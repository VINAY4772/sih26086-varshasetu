import sqlite3
import os
from pathlib import Path
import sys

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    target_path = db_path or Config.DATABASE_PATH
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialise_database(db_path: str = None) -> None:
    target_path = db_path or Config.DATABASE_PATH
    schema_path = Path(__file__).resolve().parent / "schema.sql"

    print(f"📦 Initialising SQLite database at: {target_path}")
    conn = get_db_connection(target_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)

    # Seed official data sources metadata
    data_sources = [
        (
            "imd_daily_gridded",
            "IMD 0.25° Daily Gridded Rainfall Dataset",
            "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html",
            "0.25° x 0.25° (~25km)",
            "Daily",
            "Annual update",
            "Government of India Open Data License / MoES IMD Terms",
            "Long-term high resolution gridded daily rainfall records across India (1901-present).",
            0
        ),
        (
            "noaa_nino34",
            "NOAA CPC Niño 3.4 ENSO Index",
            "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii",
            "Equatorial Pacific (5N-5S, 170W-120W)",
            "Monthly / Weekly",
            "Monthly",
            "Public Domain (NOAA/NWS)",
            "El Niño Southern Oscillation sea surface temperature anomalies in Niño 3.4 region.",
            0
        ),
        (
            "bom_iod_dmi",
            "BOM Dipole Mode Index (IOD)",
            "http://www.bom.gov.au/climate/iod/",
            "Tropical Indian Ocean (Western & Eastern poles)",
            "Weekly / Monthly",
            "Weekly",
            "Australian Bureau of Meteorology Open Data",
            "Indian Ocean Dipole index representing SST gradient across Indian Ocean.",
            0
        ),
        (
            "cpc_mjo_wheeler_hendon",
            "Madden-Julian Oscillation (RMM1, RMM2)",
            "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_mjo_index/mjo_index.shtml",
            "Global Tropics (15S to 15N)",
            "Daily",
            "Daily",
            "Public Domain (NOAA CPC)",
            "Real-time Multivariate MJO series tracking convective passage across tropical longitudes.",
            0
        ),
        (
            "nasa_power_daily",
            "NASA POWER Agroclimatology Daily Archive",
            "https://power.larc.nasa.gov/api/temporal/daily/point",
            "0.5° x 0.5° global grid (~50km) interpolated to coordinate",
            "Daily",
            "Daily (2-3 day operational latency)",
            "NASA Open Data Policy (Public Domain)",
            "Satellite and assimilation-derived daily precipitation (PRECTOTCORR) and surface meteorology for agricultural modeling.",
            0
        ),
        (
            "synthetic_demo_feed",
            "SYNTHETIC DEMONSTRATION DATA (SIH26086 Mock Pipeline)",
            "file://data/sample/synthetic_weather_sample.csv",
            "Block/Village scale (~1-5km simulated)",
            "Daily",
            "Local test generation",
            "MIT / SIH Educational Demonstration License",
            "EXPLICITLY SYNTHETIC DEMONSTRATION DATA for local software testing and hackathon verification. Not real observations.",
            1
        )
    ]

    conn.executemany(
        """
        INSERT OR REPLACE INTO data_sources
        (id, name, source_url, spatial_resolution, temporal_resolution, update_frequency, license, description, is_synthetic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        data_sources
    )

    # Seed canonical agricultural blocks and villages across India
    locations = [
        (
            "tel_wgl_dharmasagar",
            "Dharmasagar Village",
            "Dharmasagar Mandal",
            "Hanamkonda / Warangal",
            "Telangana",
            17.9944,
            79.4892,
            280.0,
            "Red Sandy Loam & Black Soil",
            "Southern Telangana Agro-Climatic Zone",
            "June 08"
        ),
        (
            "tel_mbnr_jadcherla",
            "Badepally Village",
            "Jadcherla Mandal",
            "Mahabubnagar",
            "Telangana",
            16.7645,
            78.1367,
            490.0,
            "Chalka (Red Sandy)",
            "South-Western Telangana Zone",
            "June 07"
        ),
        (
            "ap_gnr_tenali",
            "Angalakuduru Village",
            "Tenali Mandal",
            "Guntur",
            "Andhra Pradesh",
            16.2437,
            80.6400,
            15.0,
            "Deltaic Alluvial & Black Clay",
            "Krishna-Godavari Zone",
            "June 06"
        ),
        (
            "ap_knl_adoni",
            "Arekal Village",
            "Adoni Mandal",
            "Kurnool",
            "Andhra Pradesh",
            15.6322,
            77.2728,
            435.0,
            "Black Cotton & Gravelly Red",
            "Scarce Rainfall Zone of Rayalaseema",
            "June 05"
        ),
        (
            "mh_amr_chandur",
            "Amla Vishweshwar Village",
            "Chandur Railway Block",
            "Amravati",
            "Maharashtra",
            20.8123,
            77.9654,
            340.0,
            "Deep Black Cotton Soil (Regur)",
            "Vidarbha Central Plateau",
            "June 11"
        ),
        (
            "mh_ltr_ausa",
            "Ashiv Village",
            "Ausa Block",
            "Latur",
            "Maharashtra",
            18.2514,
            76.5028,
            620.0,
            "Medium Deep Black Soil",
            "Marathwada Rain-Shadow Zone",
            "June 10"
        ),
        (
            "mp_seh_ashta",
            "Khajuria Kasam Village",
            "Ashta Block",
            "Sehore",
            "Madhya Pradesh",
            23.0189,
            76.7214,
            485.0,
            "Deep Heavy Vertisols (Black)",
            "Malwa Plateau Soybean Belt",
            "June 16"
        ),
        (
            "ka_dwd_hubli",
            "Unkal Village",
            "Hubballi Rural",
            "Dharwad",
            "Karnataka",
            15.3647,
            75.1240,
            670.0,
            "Medium Black & Mixed Red Soil",
            "Northern Transition Zone",
            "June 05"
        )
    ]

    conn.executemany(
        """
        INSERT OR REPLACE INTO locations
        (id, name, block_or_mandal, district, state, latitude, longitude, elevation_m, primary_soil, agro_climatic_zone, normal_onset_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        locations
    )

    conn.commit()
    conn.close()
    print("✅ Database successfully initialized and seeded with verified locations and data sources.")

if __name__ == "__main__":
    initialise_database()
