"""Generate normal-operation readings across synthetic watering profiles."""

import argparse
from pathlib import Path

import pandas as pd
import wntr

from first_simulation import SCHEDULE_PROFILES, build_network


ZONES = [
    ("Zone_A", "Branch_A"),
    ("Zone_B", "Branch_B"),
    ("Zone_C", "Branch_C"),
]
DEFAULT_OUTPUT = Path("outputs") / "normal_watering_scenarios.csv"


def generate_scenarios(schedules: list[str] | None = None) -> pd.DataFrame:
    """Return one labelled row for each schedule, hour, and zone reading."""
    selected_schedules = schedules or list(SCHEDULE_PROFILES)
    unknown = sorted(set(selected_schedules) - set(SCHEDULE_PROFILES))
    if unknown:
        valid = ", ".join(SCHEDULE_PROFILES)
        raise ValueError(f"Unknown schedule(s): {', '.join(unknown)}. Choose from: {valid}")

    rows: list[dict[str, object]] = []
    for schedule in selected_schedules:
        network = build_network(schedule)
        results = wntr.sim.EpanetSimulator(network).run_sim()

        for hour, demand_multiplier in enumerate(SCHEDULE_PROFILES[schedule]):
            timestamp = hour * 3600
            pressure = results.node["pressure"].loc[timestamp]
            flow = results.link["flowrate"].loc[timestamp]
            scenario_id = f"NORMAL_{schedule.upper()}_H{hour:02d}"

            for zone_name, branch_name in ZONES:
                rows.append(
                    {
                        "Scenario_ID": scenario_id,
                        "Schedule": schedule,
                        "Hour": hour,
                        "Demand_Multiplier": demand_multiplier,
                        "Condition": "normal",
                        "Severity": "none",
                        "Fault_Location": "none",
                        "Zone": zone_name.replace("_", " "),
                        "Pressure_kPa": float(pressure[zone_name]) * 9.80665,
                        "Flow_L_min": float(flow[branch_name]) * 60_000,
                        "Data_Source": "WNTR synthetic simulation",
                    }
                )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate normal synthetic readings for irrigation schedules."
    )
    parser.add_argument(
        "--schedule",
        choices=["all", *SCHEDULE_PROFILES],
        default="all",
        help="Schedule profile to simulate (default: all three).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Local CSV output path (default: {DEFAULT_OUTPUT}).",
    )
    args = parser.parse_args()

    schedules = list(SCHEDULE_PROFILES) if args.schedule == "all" else [args.schedule]
    table = generate_scenarios(schedules)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)

    print(f"Created {len(table)} normal-operation reading rows from synthetic WNTR simulations.")
    print(f"Schedules: {', '.join(schedule.title() for schedule in schedules)}")
    print(f"Zones: {', '.join(zone.replace('_', ' ') for zone, _ in ZONES)}")
    print(f"Saved local CSV: {args.output}")
    print("No field or UOW irrigation measurements are included.")


if __name__ == "__main__":
    main()
