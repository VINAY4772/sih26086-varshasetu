# Model Card: SIH26086 Hybrid Forecasting Engine

## 1. Model Details
- **Model Name:** SIH26086 Monsoon Onset & Break Spell Predictor
- **Version:** v1.0-Hybrid
- **Architecture:** Hybrid Physical-Rule Engine + Supervised Random Forest Classifier
- **Primary Task:** Multi-horizon probabilistic prediction of Monsoon Break Spells, Dry Spell Duration, and Operational Onset Declaration.
- **Developers:** SIH26086 Engineering Team (MoES Theme)

---

## 2. Intended Use & Target Users
- **Intended Use:** Assisting smallholder farmers, village agricultural extension officers (Mandal Agricultural Officers / KVK scientists), and agricultural decision-makers in planning Kharif sowing, fertilizer application, and protective irrigation.
- **Target Scale:** Block and village scale (~1 km–5 km).
- **Out-of-Scope Use:** Aviation weather routing, high-risk flood evacuation planning without state disaster management concurrence.

---

## 3. Training & Evaluation Methodology
- **Training Data:** 2,920 daily meteorological observations (2023–2024 season).
- **Evaluation Data (Independent Chronological Split):** 1,472 daily observations (2025 season).
- **Leakage Prevention:** Features computed strictly over historical lag windows ($t-1, t-2, t-3$); no future information included.

### Actual Evaluation Results
| Metric | Random Forest Model | Climatological Baseline | Improvement (Skill) |
| :--- | :--- | :--- | :--- |
| **Brier Score (Lower is better)** | **0.2203** | 0.2616 | **+15.77% Brier Skill Score** |
| **ROC-AUC** | **0.7118** | 0.5000 | +0.2118 |
| **Precision** | **0.7191** | 0.6096 | +10.95% |
| **Recall** | **0.5819** | 1.0000 (trivial) | Balanced selectivity |
| **F1 Score** | **0.6432** | 0.7575 | Robust probabilistic threshold |

---

## 4. Known Limitations & Uncertainty
1. **Resolution vs. Microclimates:** Local convective thunderstorm showers may vary across a single village cluster.
2. **Subseasonal Horizon Uncertainty:** Forecast skill decreases progressively from 7 days to 30 days due to chaotic atmospheric dynamics. Horizons beyond 14 days should be treated as general climate outlooks rather than deterministic rain events.
3. **Soil Spatial Heterogeneity:** Root-zone soil moisture estimates represent representative dominant soil types (e.g., Vertisol / Alfisol) and may differ in unbunded or eroded fields.
