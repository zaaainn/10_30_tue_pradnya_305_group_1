"""Load and apply the trained condition and fault-location models."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = ROOT / "models" / "random_forest_diagnosis.joblib"
NUMERIC_FEATURES = [
    "Hour",
    "Demand_Multiplier",
    "Pressure_ZoneA_kPa",
    "Pressure_ZoneB_kPa",
    "Pressure_ZoneC_kPa",
    "Flow_ZoneA_L_min",
    "Flow_ZoneB_L_min",
    "Flow_ZoneC_L_min",
]
CATEGORICAL_FEATURES = ["Schedule"]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def load_model(path: str | Path = DEFAULT_MODEL_PATH) -> dict:
    """Load the saved model bundle from disk."""
    return joblib.load(path)


def predict_records(records: pd.DataFrame, model_bundle: dict | None = None) -> pd.DataFrame:
    """Predict normal/leak/clog and, for predicted faults, the affected zone."""
    model_bundle = model_bundle or load_model()
    missing = [column for column in FEATURE_COLUMNS if column not in records.columns]
    if missing:
        raise ValueError(f"Input records are missing required features: {', '.join(missing)}")

    features = records[FEATURE_COLUMNS]
    conditions = model_bundle["condition_model"].predict(features)
    locations = np.full(len(records), "none", dtype=object)
    fault_mask = conditions != "normal"
    if fault_mask.any():
        locations[fault_mask] = model_bundle["location_model"].predict(features.loc[fault_mask])

    predictions = records.copy()
    predictions["Predicted_Condition"] = conditions
    predictions["Predicted_Fault_Location"] = locations
    return predictions
