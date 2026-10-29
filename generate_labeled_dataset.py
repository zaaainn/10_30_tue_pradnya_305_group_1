"""Build the labeled WNTR scenario dataset for the project prototype."""

import argparse
from pathlib import Path

import pandas as pd

from fault_scenarios import CLOG_DEMAND_FACTORS, LEAK_EMITTER_COEFFICIENTS, SEVERITIES, ZONES, run_case
from first_simulation import SCHEDULE_PROFILES


DEFAULT_OUTPUT = Path("outputs") / "labeled_fault_scenarios.csv"


def generate_dataset() -> pd.DataFrame:
    """Generate normal, leak, and clog readings for every schedule and zone."""
    cases: list[pd.DataFrame] = []
    for schedule in SCHEDULE_PROFILES:
        cases.append(run_case("normal", schedule=schedule, fault_zone=None))
        for fault_zone, _ in ZONES:
            for condition in ("leak", "clog"):
                for severity in SEVERITIES:
                    cases.append(
                        run_case(
                            condition,
                            severity=severity,
                            schedule=schedule,
                            fault_zone=fault_zone,
                        )
                    )
    return pd.concat(cases, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the full labeled WNTR dataset across schedules, faults, severities, and zones."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT}).",
    )
    args = parser.parse_args()

    dataset = generate_dataset()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(args.output, index=False, float_format="%.6f")

    print(f"Saved {len(dataset)} labeled schedule-hour rows to {args.output}")
    print(f"Unique scenario configurations: {dataset['Scenario_ID'].nunique()}")
    print("Rows by condition:")
    print(dataset["Condition"].value_counts().sort_index().to_string())
    print("Rows by fault location:")
    print(dataset["Fault_Location"].value_counts().sort_index().to_string())
    print("Data source: WNTR hydraulic simulation; no field sensor data included.")


if __name__ == "__main__":
    main()
