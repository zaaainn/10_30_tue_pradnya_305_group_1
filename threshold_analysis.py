"""Diagnostics for the schedule-aware threshold baseline (Member 4).

Run from the project root, next to schedule_aware_threshold.py:
    .\\.venv\\Scripts\\python.exe .\\threshold_analysis.py

It answers three questions and saves a CSV for each in outputs/:
  1. Do leaks and clogs move flow and pressure in the directions the rules assume?
  2. Where does the baseline miss faults, and in which hours?
  3. How do the results change when all tolerances are scaled up or down?
"""
from pathlib import Path

import pandas as pd

from schedule_aware_threshold import build_normal_baseline, predict_thresholds

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "outputs" / "labeled_fault_scenarios.csv"
OUT = ROOT / "outputs"

# Default tolerances used by the group's baseline
DEFAULTS = dict(flow_fraction=0.05, min_flow_tolerance_l_min=0.5,
                pressure_fraction=0.001, min_pressure_tolerance_kpa=0.5)


def faulty_zone_deviation(data: pd.DataFrame) -> pd.DataFrame:
    """Flow and pressure change (vs the normal baseline) in the zone that holds the fault."""
    base = build_normal_baseline(data).set_index(["Schedule", "Hour"])
    rows = []
    for _, r in data[data["Condition"] != "normal"].iterrows():
        zone = r["Fault_Location"].replace(" ", "")
        exp = base.loc[(r["Schedule"], r["Hour"])]
        rows.append({
            "Scenario_ID": r["Scenario_ID"], "Condition": r["Condition"],
            "Severity": r["Severity"], "Schedule": r["Schedule"], "Hour": r["Hour"],
            "Demand_Multiplier": r["Demand_Multiplier"],
            "flow_dev_L_min": r[f"Flow_{zone}_L_min"] - exp[f"Flow_{zone}_L_min"],
            "pressure_dev_kPa": r[f"Pressure_{zone}_kPa"] - exp[f"Pressure_{zone}_kPa"],
        })
    return pd.DataFrame(rows)


def summarise(result: pd.DataFrame) -> dict:
    fault = result["Condition"] != "normal"
    return {
        "missed_fault_rate": 1 - result.loc[fault, "Threshold_Alert"].mean(),
        "false_alert_rate": result.loc[~fault, "Threshold_Alert"].mean(),
        "three_class_accuracy": (result["Condition"] == result["Threshold_Condition"]).mean(),
        "unknown_fault_share": (result.loc[fault, "Threshold_Condition"] == "unknown_fault").mean(),
        "location_accuracy": (result.loc[fault, "Fault_Location"] == result.loc[fault, "Threshold_Location"]).mean(),
    }


def main() -> None:
    data = pd.read_csv(DATASET)

    # 1. Direction check
    dev = faulty_zone_deviation(data)
    dev["flow_sign"] = dev["flow_dev_L_min"].round(6).apply(lambda v: (v > 0) - (v < 0))
    dev["pressure_sign"] = dev["pressure_dev_kPa"].round(6).apply(lambda v: (v > 0) - (v < 0))
    directions = pd.crosstab(dev["Condition"], [dev["flow_sign"], dev["pressure_sign"]])
    print("Direction of change in the faulty zone (flow sign, pressure sign):")
    print(directions.to_string(), "\n")
    print(dev.groupby(["Condition", "Severity"])[["flow_dev_L_min", "pressure_dev_kPa"]]
          .agg(["min", "median", "max"]).round(2).to_string(), "\n")
    dev.to_csv(OUT / "threshold_fault_direction.csv", index=False, float_format="%.4f")

    # 2. Misses with the default tolerances
    result = predict_thresholds(data, baseline_data=data, **DEFAULTS)
    missed = result[(result["Condition"] != "normal") & (~result["Threshold_Alert"])]
    print("Missed faults by condition, schedule, hour and demand multiplier:")
    print(missed.groupby(["Condition", "Schedule", "Hour", "Demand_Multiplier"]).size().to_string(), "\n")

    # 3. Tolerance sensitivity
    rows = []
    for scale in (0.1, 0.25, 0.5, 1, 2, 4):
        scaled = {k: v * scale for k, v in DEFAULTS.items()}
        rows.append({"tolerance_scale": scale, **summarise(predict_thresholds(data, baseline_data=data, **scaled))})
    sweep = pd.DataFrame(rows)
    print("Tolerance sensitivity (all schedules):")
    print(sweep.round(3).to_string(index=False))
    sweep.to_csv(OUT / "threshold_sensitivity.csv", index=False, float_format="%.4f")
    print("\nNote: false_alert_rate is 0 at every scale because the normal rows are the same rows "
          "the baseline was built from. Add normal variation before choosing tolerances.")


if __name__ == "__main__":
    main()
