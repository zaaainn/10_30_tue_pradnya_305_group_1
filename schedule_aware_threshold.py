"""Schedule-aware pressure/flow threshold baseline for the WNTR dataset."""

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = ROOT / "outputs" / "labeled_fault_scenarios.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "threshold_predictions.csv"
ZONES = ("ZoneA", "ZoneB", "ZoneC")


def build_normal_baseline(data: pd.DataFrame) -> pd.DataFrame:
    """Build expected readings for each schedule and hour from normal rows only."""
    normal = data.loc[data["Condition"] == "normal"]
    if normal.empty:
        raise ValueError("No normal-operation rows are available to build the baseline.")
    sensor_columns = [
        f"{kind}_{zone}_{unit}"
        for kind, unit in (("Pressure", "kPa"), ("Flow", "L_min"))
        for zone in ZONES
    ]
    missing = [column for column in sensor_columns if column not in normal.columns]
    if missing:
        raise ValueError(f"Dataset is missing sensor columns: {', '.join(missing)}")
    return normal.groupby(["Schedule", "Hour"], as_index=False)[sensor_columns].mean()


def predict_thresholds(
    data: pd.DataFrame,
    flow_fraction: float = 0.05,
    min_flow_tolerance_l_min: float = 0.5,
    pressure_fraction: float = 0.001,
    min_pressure_tolerance_kpa: float = 0.5,
) -> pd.DataFrame:
    """Flag anomalies against schedule/hour baselines and infer simple directions.

    A flow rise paired with a pressure drop suggests a leak. A flow drop paired
    with a pressure rise suggests a clog. Other out-of-band readings are alerted
    as an unknown fault pattern rather than assigned a guessed fault type.
    """
    baseline = build_normal_baseline(data).set_index(["Schedule", "Hour"])
    results: list[dict[str, object]] = []

    for _, row in data.iterrows():
        expected = baseline.loc[(row["Schedule"], row["Hour"])]
        candidates: list[tuple[float, str, str, float, float]] = []
        anomalies: list[tuple[float, str, float, float]] = []

        for zone in ZONES:
            expected_flow = float(expected[f"Flow_{zone}_L_min"])
            expected_pressure = float(expected[f"Pressure_{zone}_kPa"])
            observed_flow = float(row[f"Flow_{zone}_L_min"])
            observed_pressure = float(row[f"Pressure_{zone}_kPa"])
            flow_delta = observed_flow - expected_flow
            pressure_delta = observed_pressure - expected_pressure
            flow_tolerance = max(min_flow_tolerance_l_min, abs(expected_flow) * flow_fraction)
            pressure_tolerance = max(min_pressure_tolerance_kpa, abs(expected_pressure) * pressure_fraction)
            flow_out = abs(flow_delta) > flow_tolerance
            pressure_out = abs(pressure_delta) > pressure_tolerance
            score = abs(flow_delta) / flow_tolerance + abs(pressure_delta) / pressure_tolerance

            if flow_out or pressure_out:
                anomalies.append((score, zone.replace("Zone", "Zone "), flow_delta, pressure_delta))
            if flow_delta > flow_tolerance and pressure_delta < -pressure_tolerance:
                candidates.append((score, "leak", zone.replace("Zone", "Zone "), flow_delta, pressure_delta))
            elif flow_delta < -flow_tolerance and pressure_delta > pressure_tolerance:
                candidates.append((score, "clog", zone.replace("Zone", "Zone "), flow_delta, pressure_delta))

        if candidates:
            score, condition, location, flow_delta, pressure_delta = max(candidates)
            alert = True
        elif anomalies:
            score, location, flow_delta, pressure_delta = max(anomalies)
            condition = "unknown_fault"
            alert = True
        else:
            condition, location, flow_delta, pressure_delta, alert = "normal", "none", 0.0, 0.0, False

        results.append(
            {
                "Threshold_Alert": alert,
                "Threshold_Condition": condition,
                "Threshold_Location": location,
                "Threshold_Flow_Deviation_L_min": flow_delta,
                "Threshold_Pressure_Deviation_kPa": pressure_delta,
            }
        )

    return pd.concat([data.reset_index(drop=True), pd.DataFrame(results)], axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run schedule-aware dynamic thresholds.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--flow-fraction", type=float, default=0.05)
    parser.add_argument("--pressure-fraction", type=float, default=0.001)
    args = parser.parse_args()

    data = pd.read_csv(args.dataset)
    predictions = predict_thresholds(
        data,
        flow_fraction=args.flow_fraction,
        pressure_fraction=args.pressure_fraction,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output, index=False, float_format="%.6f")
    print(f"Wrote {len(predictions)} schedule-aware threshold results to {args.output}")
    print("Threshold condition counts:")
    print(predictions["Threshold_Condition"].value_counts().sort_index().to_string())
    print(f"Alerts: {int(predictions['Threshold_Alert'].sum())} / {len(predictions)} records")
    print("Thresholds: flow ±max(0.5 L/min, 5% of expected); pressure ±max(0.5 kPa, 0.1% of expected).")


if __name__ == "__main__":
    main()
