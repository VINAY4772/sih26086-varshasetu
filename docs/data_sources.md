# Data Sources & Ingestion Specification: SIH26086

## 1. Verified Official Meteorological Data Sources

The following table documents the authoritative sources researched for the SIH26086 system:

| Source Name | Official URL | Variables & Units | Spatial & Temporal Resolution | Historical Coverage & Frequency | Licensing & Restrictions | Access Method |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IMD High-Resolution Gridded Rainfall** | `https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html` | Daily Rainfall (mm) | $0.25^\circ \times 0.25^\circ$ (~25 km), Daily | 1901–present, Annual update | MoES / IMD National Data Sharing Policy. Free for educational/research use. | Requires data request registration or direct binary archive processing. |
| **NOAA CPC Niño 3.4 Index** | `https://www.cpc.ncep.noaa.gov/data/indices/` | Sea Surface Temperature Anomaly ($^\circ\text{C}$) | Central-Eastern Pacific ($5^\circ\text{N}–5^\circ\text{S}, 170^\circ\text{W}–120^\circ\text{W}$) | 1950–present, Monthly/Weekly | Public Domain (US Government Work) | Direct text file ingestion. |
| **BOM Dipole Mode Index (IOD)** | `http://www.bom.gov.au/climate/iod/` | SST Gradient ($^\circ\text{C}$) | Western Indian Ocean vs. Eastern Indian Ocean | 1870–present, Weekly | Australian Open Data License | Direct ASCII stream download. |
| **CPC Wheeler-Hendon MJO Index** | `https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_mjo_index/` | RMM1, RMM2, Amplitude, Phase (1–8) | Global Tropics ($15^\circ\text{S}–15^\circ\text{N}$), Daily | 1974–present, Daily | Public Domain (NOAA NWS) | Direct text file ingestion. |

---

## 2. Ingestion Pipeline & Validation Rules

The ingestion engine in `forecasting/data_ingestion.py` enforces the following integrity standards:

1. **Mandatory Schema Columns**: `location_id`, `date`, `rainfall_mm`.
2. **Date Normalization**: Standardized to ISO 8601 (`YYYY-MM-DD`).
3. **Deduplication**: Identifies multiple records for the same `(location_id, date)` and keeps the latest verified entry.
4. **Physical Sanity Bounds**:
   - Rainfall: Clamped to $[0.0\text{ mm}, 1200.0\text{ mm}]$. Negative values clamped to $0.0\text{ mm}$ with a documented warning.
   - Temperature: $T_{\max} \in [-10^\circ\text{C}, 60^\circ\text{C}]$, $T_{\min} \in [-20^\circ\text{C}, 50^\circ\text{C}]$.
   - Relative Humidity: Clamped to $[0\%, 100\%]$.
   - Outgoing Longwave Radiation (OLR): Clamped to $[60\text{ W/m}^2, 400\text{ W/m}^2]$.
   - Soil Moisture: Clamped to $[0\%, 100\%]$.
5. **Geographic Verification**: All incoming `location_id` entries are checked against the `locations` table in SQLite. Unknown IDs are rejected or filtered.

---

## 3. SYNTHETIC DEMONSTRATION DATA POLICY
- Any file residing in `data/sample/` (such as `synthetic_weather_sample.csv`) is generated purely for local testing and demonstration.
- All records imported from this file carry `data_source_id = 'synthetic_demo_feed'` and `is_demonstration = 1`.
- In compliance with SIH evaluation standards, the prototype interface explicitly displays a banner stating that demonstration benchmark data is active.
