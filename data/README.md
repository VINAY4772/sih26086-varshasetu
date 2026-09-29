# Data Management & Provenance Guide: SIH26086

## 1. Official Data Sources Considered
The SIH26086 system architecture integrates multi-scale meteorological and climate indices:

| Source | Agency | Spatial Coverage | Resolution & Frequency | Variables Used | Access & Licensing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IMD 0.25° Gridded Rainfall** | India Meteorological Department (MoES) | Pan-India Land ($6.5^\circ\text{N}-38.5^\circ\text{N}$) | $0.25^\circ \times 0.25^\circ$ (~25 km), Daily | Daily rainfall (mm) | MoES Data Sharing Policy (Requires registration/request for binary grid archives). |
| **NOAA CPC Niño 3.4** | NOAA Climate Prediction Center | Central-Eastern Equatorial Pacific | Monthly / Weekly SST Anomaly ($^\circ\text{C}$) | Niño 3.4 Index (ENSO Phase) | Public Domain. Direct text file download. |
| **BOM Dipole Mode Index (IOD)** | Australian Bureau of Meteorology | Tropical Indian Ocean | Weekly SST difference ($^\circ\text{C}$) | DMI (Positive/Negative IOD) | Open Data. Direct ASCII file. |
| **CPC MJO RMM Series** | NOAA CPC / Wheeler-Hendon | Equatorial Tropics ($15^\circ\text{S}-15^\circ\text{N}$) | Daily RMM1, RMM2, Amplitude, Phase (1-8) | MJO Convective Phase | Public Domain. Daily updated ASCII feed. |

---

## 2. SYNTHETIC DEMONSTRATION DATA NOTICE
⚠️ **IMPORTANT NOTICE:**
Files located inside `data/sample/` (e.g., `synthetic_weather_sample.csv`) are **EXPLICITLY SYNTHETIC DEMONSTRATION DATA** generated solely for local software verification, unit testing, and Smart India Hackathon demonstrations without requiring paid access or external API credentials.
- They are **NOT** live operational forecasts.
- They are **NOT** historical certified observations.
- In all user-facing interfaces and API outputs, records sourced from these files are flagged with `is_demonstration = 1` and labelled **SYNTHETIC DEMONSTRATION DATA**.
