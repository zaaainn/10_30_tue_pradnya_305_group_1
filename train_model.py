"""Train and save Random Forest condition and fault-location classifiers."""

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from diagnosis import (
    CATEGORICAL_FEATURES,
    DEFAULT_MODEL_PATH,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = ROOT / "outputs" / "labeled_fault_scenarios.csv"


def make_classifier() -> Pipeline:
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            ("schedule", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([("features", preprocessing), ("forest", classifier)])


def split_by_scenario(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out the entire night schedule to test generalization to an unseen schedule."""
    test = data.loc[data["Schedule"] == "night"].copy()
    train = data.loc[data["Schedule"] != "night"].copy()
    if train.empty or test.empty:
        raise ValueError("Dataset must contain morning, afternoon, and night profiles.")
    if set(train["Scenario_ID"]) & set(test["Scenario_ID"]):
        raise ValueError("Scenario_ID leakage detected between training and test sets.")
    return train, test


def train_and_save(dataset_path: Path, model_path: Path) -> dict:
    data = pd.read_csv(dataset_path)
    required = set(FEATURE_COLUMNS + ["Scenario_ID", "Condition", "Fault_Location", "Schedule"])
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    train, test = split_by_scenario(data)
    X_train, X_test = train[FEATURE_COLUMNS], test[FEATURE_COLUMNS]

    condition_model = make_classifier()
    condition_model.fit(X_train, train["Condition"])
    condition_prediction = condition_model.predict(X_test)
    condition_accuracy = accuracy_score(test["Condition"], condition_prediction)
    condition_macro_f1 = f1_score(test["Condition"], condition_prediction, average="macro")

    train_faults = train[train["Condition"] != "normal"]
    test_faults = test[test["Condition"] != "normal"]
    location_model = make_classifier()
    location_model.fit(train_faults[FEATURE_COLUMNS], train_faults["Fault_Location"])
    location_prediction = location_model.predict(test_faults[FEATURE_COLUMNS])
    location_accuracy = accuracy_score(test_faults["Fault_Location"], location_prediction)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "condition_model": condition_model,
        "location_model": location_model,
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "metadata": {
            "algorithm": "RandomForestClassifier",
            "random_state": 42,
            "estimators": 300,
            "split": "hold out all night schedule; group by Scenario_ID",
            "train_rows": len(train),
            "test_rows": len(test),
            "condition_accuracy_night": condition_accuracy,
            "condition_macro_f1_night": condition_macro_f1,
            "fault_location_accuracy_night": location_accuracy,
        },
    }
    joblib.dump(bundle, model_path)

    print(f"Training rows: {len(train)}; held-out night rows: {len(test)}")
    print(f"Condition accuracy on held-out night schedule: {condition_accuracy:.3f}")
    print(f"Condition macro F1 on held-out night schedule: {condition_macro_f1:.3f}")
    print(f"Fault-location accuracy on held-out night faults: {location_accuracy:.3f}")
    print("Condition classification report:")
    print(classification_report(test["Condition"], condition_prediction, zero_division=0))
    print(f"Saved model bundle: {model_path}")
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the irrigation Random Forest models.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()
    train_and_save(args.dataset, args.model)


if __name__ == "__main__":
    main()
