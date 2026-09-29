# Real-Data Meteorological Event Definitions & Validation Plan: SIH26086
## Hyperlocal Monsoon Onset & Break Prediction System at Block/Village Scale
### Ministry of Earth Sciences (MoES) | Department: NCMRWF | Smart India Hackathon 2026

---

## 1. Executive Summary & Purpose
This document establishes the scientific criteria, variable mapping, chronological partitioning, and evaluation baselines for transitioning the SIH26086 forecasting pipeline from the initial synthetic demonstration benchmark to verified multi-year observational and reanalysis datasets.

> [!IMPORTANT]
> In accordance with strict hackathon integrity guidelines:
> - **The existing synthetic benchmark (`data/sample/synthetic_weather_sample.csv`) and trained model (`models/break_model_rf.joblib`) remain active and unchanged** for reproducible UI/API evaluation.
> - The multi-year real historical archive for Tenali, Andhra Pradesh (`data/real/tenali_nasa_power_2015_2025.json` and `.csv`) has been collected and validated, but **has NOT yet been used for model retraining**. Model retraining will occur only after peer review of this validation plan.

---

## 2. Event Definitions, Variables & Scientific Thresholds

The system evaluates four distinct agro-meteorological event categories based on standard published literature:

### A. Monsoon Onset Criteria
* **Scientific Reference**: Pai et al. (2014) *Operational Criteria for Monsoon Onset over Kerala (MOK)*, IMD Technical Report.
* **Three-Pillar Operational Rule**:
  1. **Rainfall Persistence**: $\ge 2.5\text{ mm/day}$ at $\ge 60\%$ of stations in the spatial catchment on 2 consecutive days.
  2. **Lower Tropospheric Westerly Shear**: Zonal wind at 850 hPa $\ge 15\text{ knots}$ ($7.7\text{ m/s}$) over the latitude band ($5^\circ\text{N}–12^\circ\text{N}$).
  3. **Deep Convective Cloudiness**: Top-of-Atmosphere Outgoing Longwave Radiation (OLR) $\le 200.0\text{ W/m}^2$.
* **Anti-False-Alarm Filter**:
  - Rejects pre-monsoon convective showers if surface rain occurs without supporting synoptic westerly shear ($< 7.7\text{ m/s}$) or low OLR ($> 200\text{ W/m}^2$).
* **Variable Sufficiency in NASA POWER**:
  - **Precipitation (`PRECTOTCORR`)**: **Available** (mm/day).
  - **850 hPa Zonal Wind**: **Missing** (NASA POWER standard point query provides only 2m/10m surface winds).
  - **OLR (Convective Cloudiness)**: **Missing** (NASA POWER provides surface solar insolation, not TOA OLR).
  - **Conclusion**: *NASA POWER point data alone is insufficient to compute true IMD operational onset labels without supplementary pressure-level reanalysis (e.g. ERA5 or NCMRWF NCUM).*

### B. Monsoon Break Spells & Prolonged Dry Spells
* **Scientific Reference**: Rajeevan et al. (2010) *Active and Break Spells of the Indian Summer Monsoon*, J. Earth Syst. Sci.
* **Operational Rules**:
  - **Dry Day Definition**: Daily rainfall $< 2.5\text{ mm/day}$ (IMD non-rain day standard) or $\le 2.0\text{ mm/day}$.
  - **Standard Break Spell**: Consecutive dry days $\ge 4\text{ days}$ during active monsoon season (June–September) (`HIGH` risk).
  - **Critical Prolonged Break**: Consecutive dry days $\ge 7\text{ days}$ (`CRITICAL` risk; triggers agricultural drought contingency).
* **Variable Sufficiency in NASA POWER**:
  - **Precipitation (`PRECTOTCORR`)**: **100% Sufficient**. Complete 4,018-day unbroken daily time series enables exact historical computation of dry streaks and forward break risk.

### C. Rainfall Anomaly Departure
* **Scientific Reference**: IMD Standard Operational Rainfall Terminology.
* **Operational Formula**:
  $$\text{Departure \%} = \left(\frac{\text{Cumulative Observed (mm)} - \text{Cumulative Normal (mm)}}{\text{Cumulative Normal (mm)}}\right) \times 100$$
* **Categories**:
  - **Large Excess (LE)**: $\ge +60\%$
  - **Excess (E)**: $+20\%$ to $+59\%$
  - **Normal (N)**: $-19\%$ to $+19\%$
  - **Deficient (D)**: $-20\%$ to $-59\%$
  - **Large Deficient (LD)**: $\le -60\%$
* **Variable Sufficiency**: **100% Sufficient**.

### D. Heavy Rainfall Risk Warnings
* **Scientific Reference**: IMD 24-hour Accumulated Rainfall Classification.
* **Thresholds**:
  - **Heavy Rain (Yellow Alert)**: $64.5\text{ to }115.5\text{ mm/day}$
  - **Very Heavy Rain (Orange Alert)**: $115.6\text{ to }204.4\text{ mm/day}$
  - **Extremely Heavy Rain (Red Alert)**: $\ge 204.5\text{ mm/day}$
* **Variable Sufficiency**: **100% Sufficient**.

---

## 3. Real Dataset Summary (Tenali, Andhra Pradesh)

The multi-year real historical dataset collected from NASA POWER has been saved to [`data/real/tenali_nasa_power_2015_2025.json`](file:///Users/maradanasaikiran/vinay%20new%20sih/data/real/tenali_nasa_power_2015_2025.json) and [`.csv`](file:///Users/maradanasaikiran/vinay%20new%20sih/data/real/tenali_nasa_power_2015_2025.csv):

| Metric | Verified Value |
| :--- | :--- |
| **Location** | Angalakuduru Village, Tenali Mandal, Guntur District, Andhra Pradesh |
| **Coordinates** | Latitude: `16.2437° N`, Longitude: `80.6400° E` |
| **Temporal Coverage** | `2015-01-01` to `2025-12-31` (11 full calendar years) |
| **Total Daily Records** | **4,018 records** |
| **Temporal Continuity** | **0 gaps**, **0 duplicate dates** |
| **Missing Value Sentinels** | **0 missing values** across rainfall, temperature, and humidity |
| **Mean Daily Rainfall** | $2.95\text{ mm/day}$ |
| **Total Wet Days ($\ge 2.5\text{ mm}$)** | $1,092\text{ days}$ ($27.18\%$ of all days) |
| **Total Dry Days ($< 2.5\text{ mm}$)** | $2,926\text{ days}$ ($72.82\%$ of all days) |
| **Maximum 24h Rainfall** | $129.40\text{ mm}$ on **2020-11-26** (Cyclone Nivar landfall) |
| **Maximum Air Temperature** | $45.20^\circ\text{C}$ (May 2019 pre-monsoon heatwave) |
| **Mean Relative Humidity** | $72.36\%$ (Min: $32.70\%$, Max: $94.30\%$) |

---

## 4. Chronological Validation & Model Partitioning Plan

To eliminate temporal data leakage and autocorrelation bias across multi-day weather spells, random train/test splitting is strictly forbidden. The 11-year dataset is partitioned forward-in-time:

```
[------------- TRAIN SET: 7 Years -------------] [--- VAL: 2 Yrs ---] [--- TEST: 2 Yrs ---]
2015-01-01 ------------------------ 2021-12-31   2022-01-01 - 2023-12-31  2024-01-01 - 2025-12-31
(N = 2,557 days)                                  (N = 730 days)           (N = 731 days, Leap)
```

### Partitioning Rationale:
1. **Training Split (2015–2021, $N = 2,557$)**:
   - Spans diverse monsoon seasons including drought years (2015 El Niño), normal years, and active cyclone years (2020).
   - Used exclusively to fit feature transformers and train the Random Forest / gradient boosted classifiers.
2. **Validation Split (2022–2023, $N = 730$)**:
   - Used for hyperparameter tuning (tree depth, minimum split samples, class weights).
   - Used to calibrate probability thresholds and probability calibration curves (Platt scaling / isotonic regression).
3. **Out-of-Time Test Split (2024–2025, $N = 731$)**:
   - Strict unseen holdout set.
   - Evaluates genuine forward predictive skill across two complete recent Kharif monsoon seasons.

---

## 5. Comparative Evaluation Baselines

Model performance on the test split ($N = 731$) must be benchmarked against two standard meteorological baselines:

1. **Climatological Sample Base Rate**:
   $$\text{Baseline 1: } \hat{p}_{\text{clim}} = \bar{y}_{\text{train}} = \frac{1}{N_{\text{train}}}\sum_{i=1}^{N_{\text{train}}} y_i$$
   The constant historical probability of a break spell occurring in the target window.
2. **Persistence Baseline**:
   $$\text{Baseline 2: } \hat{p}_{\text{pers}}(t) = 1 \text{ if dry streak at day } t \ge 4 \text{ else } 0$$
   Assumes that current dry/wet atmospheric regimes persist into the immediate outlook window.
3. **Target Skill Metric**:
   - **Brier Skill Score (BSS)**:
     $$BSS = 1 - \frac{BS_{\text{model}}}{BS_{\text{climatology}}}$$
     *A model has positive meteorological skill only if $BSS > 0.0$ on the out-of-time test set.*
   - **Area Under the ROC Curve (ROC-AUC)**: Target $\ge 0.70$.
   - **Reliability Diagram / Calibration Curve**: Mean predicted probability must track observed empirical frequency.

---

## 6. Prerequisites Before Model Retraining

Before retraining the active production model:
1. **Multi-Location Ingestion**: Collect matching 2015–2025 archives for the remaining 7 representative agro-climatic locations (Jadcherla, Dharmasagar, Adoni, Chandur, Ausa, Ashta, Hubli).
2. **Upper-Air Reanalysis Ingestion**: Acquire 850 hPa zonal wind and satellite OLR from ECMWF ERA5 or NCMRWF reanalysis to enable authentic IMD onset labeling.
3. **User / Evaluator Review**: Obtain explicit sign-off on this validation plan before modifying existing model binaries (`models/break_model_rf.joblib`).
