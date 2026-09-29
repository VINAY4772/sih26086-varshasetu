import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score, f1_score, precision_score, recall_score
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from database.initialise import get_db_connection
from forecasting.feature_engineering import engineer_features, FEATURE_COLUMNS

def train_break_spell_model():
    conn = get_db_connection()
    obs_df = pd.read_sql_query("SELECT * FROM observations ORDER BY location_id, date", conn)
    loc_df = pd.read_sql_query("SELECT * FROM locations", conn)
    conn.close()

    if len(obs_df) < 500:
        print("⚠️ Insufficient observation records for training machine-learning model.")
        return None

    # Engineer features
    feat_df = engineer_features(obs_df, loc_df)

    # Construct Forward-Looking Target: Break Spell in next 7 days
    # Target = 1 if max consecutive dry days in the next 7 days >= 4
    def compute_forward_break(s: pd.Series) -> pd.Series:
        is_dry = (s < 2.5).astype(int)
        # 7-day forward rolling sum of dry days
        fwd_dry_sum = is_dry.iloc[::-1].rolling(7, min_periods=7).sum().iloc[::-1].shift(-7)
        return (fwd_dry_sum >= 5).astype(int)

    feat_df["target_break_7d"] = feat_df.groupby("location_id")["rainfall_mm"].transform(compute_forward_break)

    # Drop rows where target is NaN (at the tail of series) or features have NaNs
    clean_df = feat_df.dropna(subset=FEATURE_COLUMNS + ["target_break_7d"]).copy()
    clean_df["target_break_7d"] = clean_df["target_break_7d"].astype(int)

    # Chronological Split (Train: < 2025, Test: >= 2025)
    clean_df["date"] = pd.to_datetime(clean_df["date"])
    train_mask = clean_df["date"] < "2025-01-01"
    test_mask = clean_df["date"] >= "2025-01-01"

    X_train = clean_df.loc[train_mask, FEATURE_COLUMNS]
    y_train = clean_df.loc[train_mask, "target_break_7d"]
    X_test = clean_df.loc[test_mask, FEATURE_COLUMNS]
    y_test = clean_df.loc[test_mask, "target_break_7d"]

    print(f"📊 Training records: {len(X_train)} | Test records (chronological): {len(X_test)}")
    base_rate = y_train.mean()

    # Train Random Forest
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=10,
        random_state=42,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)

    # Probabilistic Predictions on Chronological Test Set
    y_prob_test = rf.predict_proba(X_test)[:, 1]
    y_pred_test = (y_prob_test >= 0.5).astype(int)

    # Baseline Climatology Predictions
    clim_prob = np.full_like(y_test, fill_value=base_rate, dtype=float)

    # Metrics
    brier_rf = brier_score_loss(y_test, y_prob_test)
    brier_clim = brier_score_loss(y_test, clim_prob)
    auc_score = roc_auc_score(y_test, y_prob_test) if len(np.unique(y_test)) > 1 else 0.5
    f1 = f1_score(y_test, y_pred_test, zero_division=0)
    precision = precision_score(y_test, y_pred_test, zero_division=0)
    recall = recall_score(y_test, y_pred_test, zero_division=0)

    eval_summary = {
        "model_type": "RandomForestClassifier",
        "training_period": "2023-05-01 to 2024-10-31",
        "evaluation_period": "2025-05-01 to 2025-10-31",
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "base_rate_climatology": round(float(base_rate), 4),
        "brier_score_rf": round(float(brier_rf), 4),
        "brier_score_climatology": round(float(brier_clim), 4),
        "brier_skill_score": round(float(1.0 - (brier_rf / max(1e-6, brier_clim))), 4),
        "roc_auc": round(float(auc_score), 4),
        "f1_score": round(float(f1), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4)
    }

    # Save model and artifacts
    Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = Config.MODELS_DIR / "break_model_rf.joblib"
    meta_path = Config.MODELS_DIR / "break_model_metadata.json"

    joblib.dump(rf, model_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)

    print(f"✅ Model trained and saved to: {model_path}")
    print("📈 Evaluation Summary:")
    print(json.dumps(eval_summary, indent=2))
    return eval_summary

if __name__ == "__main__":
    train_break_spell_model()
