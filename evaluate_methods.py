"""Compare Random Forest diagnosis with schedule-aware pressure/flow thresholds."""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from diagnosis import DEFAULT_MODEL_PATH, load_model, predict_records
from generate_labeled_dataset import DEFAULT_OUTPUT as DEFAULT_DATASET
from schedule_aware_threshold import predict_thresholds


ROOT = Path(__file__).resolve().parent
DEFAULT_PREDICTIONS = ROOT / "outputs" / "method_comparison_predictions.csv"
DEFAULT_METRICS = ROOT / "outputs" / "method_comparison_metrics.json"
CONDITION_CLASSES = ("normal", "leak", "clog")
CLOG_SEVERITIES = ("mild", "moderate", "severe")


def condition_metrics(actual: pd.Series, predicted: pd.Series) -> dict:
    """Compute fixed-class precision, recall, F1, and accuracy.

    Predictions such as ``unknown_fault`` count as errors for the known
    normal/leak/clog classes.
    """
    per_class = {}
    f1_values = []
    for label in CONDITION_CLASSES:
        true_positive = int(((actual == label) & (predicted == label)).sum())
        false_positive = int(((actual != label) & (predicted == label)).sum())
        false_negative = int(((actual == label) & (predicted != label)).sum())
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": int((actual == label).sum())}
        f1_values.append(f1)
    accuracy = float((actual == predicted).mean()) if len(actual) else 0.0
    return {"accuracy": accuracy, "macro_f1": float(np.mean(f1_values)), "per_class": per_class}


def summarize_method(
    actual: pd.DataFrame,
    predicted_condition: pd.Series,
    predicted_location: pd.Series,
    alert: pd.Series,
    processing_ms_per_record: float,
) -> dict:
    condition = condition_metrics(actual["Condition"], predicted_condition)
    fault_mask = actual["Condition"] != "normal"
    normal_mask = ~fault_mask
    location_accuracy = (
        float((actual.loc[fault_mask, "Fault_Location"] == predicted_location.loc[fault_mask]).mean())
        if fault_mask.any()
        else 0.0
    )
    detected = alert.astype(bool)
    missed_fault_rate = float((~detected.loc[fault_mask]).mean()) if fault_mask.any() else 0.0
    false_alert_rate = float(detected.loc[normal_mask].mean()) if normal_mask.any() else 0.0
    clog_recall = {}
    for severity in CLOG_SEVERITIES:
        mask = (actual["Condition"] == "clog") & (actual["Severity"] == severity)
        clog_recall[severity] = (
            float((predicted_condition.loc[mask] == "clog").mean()) if mask.any() else 0.0
        )

    return {
        "accuracy": condition["accuracy"],
        "macro_f1": condition["macro_f1"],
        "per_class": condition["per_class"],
        "fault_location_accuracy": location_accuracy,
        "missed_fault_rate": missed_fault_rate,
        "false_alert_rate": false_alert_rate,
        "clog_recall_by_severity": clog_recall,
        "processing_ms_per_record": processing_ms_per_record,
    }


def evaluate_methods(data: pd.DataFrame, model_bundle: dict) -> tuple[pd.DataFrame, dict]:
    """Evaluate both methods on the same held-out night-profile scenarios."""
    held_out = data.loc[data["Schedule"] == "night"].copy().reset_index(drop=True)
    if held_out.empty:
        raise ValueError("No night-profile records were found for the held-out evaluation.")
    if held_out["Scenario_ID"].nunique() != 19:
        raise ValueError("Expected 19 held-out night scenario configurations (1 normal and 18 fault configurations).")

    start = time.perf_counter()
    ml_predictions = predict_records(held_out, model_bundle)
    ml_time = (time.perf_counter() - start) * 1000 / len(held_out)

    start = time.perf_counter()
    threshold_predictions = predict_thresholds(held_out, baseline_data=data)
    threshold_time = (time.perf_counter() - start) * 1000 / len(held_out)

    ml_summary = summarize_method(
        held_out,
        ml_predictions["Predicted_Condition"],
        ml_predictions["Predicted_Fault_Location"],
        ml_predictions["Predicted_Condition"] != "normal",
        ml_time,
    )
    threshold_summary = summarize_method(
        held_out,
        threshold_predictions["Threshold_Condition"],
        threshold_predictions["Threshold_Location"],
        threshold_predictions["Threshold_Alert"],
        threshold_time,
    )

    prediction_columns = [
        "Predicted_Condition",
        "Predicted_Fault_Location",
    ]
    result = pd.concat(
        [
            held_out,
            ml_predictions[prediction_columns],
            threshold_predictions[[
                "Threshold_Alert",
                "Threshold_Condition",
                "Threshold_Location",
                "Threshold_Flow_Deviation_L_min",
                "Threshold_Pressure_Deviation_kPa",
            ]],
        ],
        axis=1,
    )
    metrics = {
        "test_schedule": "night",
        "test_rows": len(held_out),
        "test_scenario_configurations": int(held_out["Scenario_ID"].nunique()),
        "split_note": "All night-profile scenarios were held out from Random Forest training.",
        "response_time_note": "Average backend processing time per record; excludes browser rendering and user selection time.",
        "random_forest": ml_summary,
        "schedule_aware_threshold": threshold_summary,
    }
    return result, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare both methods on held-out schedule scenarios.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    args = parser.parse_args()

    data = pd.read_csv(args.dataset)
    model_bundle = load_model(args.model)
    predictions, metrics = evaluate_methods(data, model_bundle)
    args.predictions.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.predictions, index=False, float_format="%.6f")
    args.metrics.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Compared both methods on {metrics['test_rows']} held-out night records.")
    for key, title in (("random_forest", "Random Forest"), ("schedule_aware_threshold", "Schedule-aware threshold")):
        result = metrics[key]
        print(
            f"{title}: accuracy={result['accuracy']:.3f}, macro-F1={result['macro_f1']:.3f}, "
            f"location accuracy={result['fault_location_accuracy']:.3f}, "
            f"missed-fault rate={result['missed_fault_rate']:.3f}, "
            f"false-alert rate={result['false_alert_rate']:.3f}, "
            f"processing={result['processing_ms_per_record']:.3f} ms/record"
        )
        print("  Clog recall by severity:", result["clog_recall_by_severity"])
    print(f"Saved prediction comparison: {args.predictions}")
    print(f"Saved metric summary: {args.metrics}")
    print(metrics["response_time_note"])


if __name__ == "__main__":
    main()
