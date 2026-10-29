"""Compare a normal case with illustrative leak and clog cases at Zone B.

Fault values are synthetic starting assumptions for the prototype, not
calibrated values or measurements from UOW Dubai.
"""

import pandas as pd
import wntr

from first_simulation import SCHEDULE_SAMPLE_HOUR, SCHEDULE_PROFILES, build_network


FAULT_ZONE = "Zone_B"

# Emitter coefficients represent additional leak discharge at the selected
# junction in the EPANET model. Values are deliberately illustrative.
LEAK_EMITTER_COEFFICIENTS = {
    "mild": 0.000003,
    "moderate": 0.000008,
    "severe": 0.000015,
}

# A clog is represented as reduced effective zone demand for this first test.
CLOG_DEMAND_FACTORS = {
    "mild": 0.80,
    "moderate": 0.55,
    "severe": 0.30,
}


def run_case(
    condition: str, severity: str | None = None, schedule: str = "morning"
) -> dict[str, object]:
    if schedule not in SCHEDULE_PROFILES:
        choices = ", ".join(SCHEDULE_PROFILES)
        raise ValueError(f"Unknown schedule {schedule!r}. Choose one of: {choices}")

    network = build_network(schedule)
    zone = network.get_node(FAULT_ZONE)

    if condition == "leak":
        zone.emitter_coefficient = LEAK_EMITTER_COEFFICIENTS[severity]
    elif condition == "clog":
        demand = zone.demand_timeseries_list[0]
        demand.base_value *= CLOG_DEMAND_FACTORS[severity]

    sample_hour = SCHEDULE_SAMPLE_HOUR[schedule]
    time_seconds = sample_hour * 3600
    results = wntr.sim.EpanetSimulator(network).run_sim()
    pressure = results.node["pressure"].loc[time_seconds, FAULT_ZONE]
    flow = results.link["flowrate"].loc[time_seconds, "Branch_B"]

    return {
        "Schedule": schedule.title(),
        "Hour": sample_hour,
        "Condition": condition.title(),
        "Severity": severity.title() if severity else "—",
        "Location": FAULT_ZONE.replace("_", " ") if severity else "—",
        "Pressure (kPa)": float(pressure) * 9.80665,
        "Flow (L/min)": float(flow) * 60_000,
    }


def main() -> None:
    cases = []
    for schedule in SCHEDULE_PROFILES:
        cases.append(run_case("normal", schedule=schedule))
        for severity in ("mild", "moderate", "severe"):
            cases.append(run_case("leak", severity, schedule))
            cases.append(run_case("clog", severity, schedule))

    table = pd.DataFrame(cases)
    normal_flows = (
        table.loc[table["Condition"] == "Normal"]
        .set_index("Schedule")["Flow (L/min)"]
    )
    table["Flow change from normal (%)"] = table.apply(
        lambda row: (row["Flow (L/min)"] - normal_flows[row["Schedule"]])
        / normal_flows[row["Schedule"]]
        * 100,
        axis=1,
    ).round(1)
    table["Pressure (kPa)"] = table["Pressure (kPa)"].round(2)
    table["Flow (L/min)"] = table["Flow (L/min)"].round(2)

    print("Zone B normal, leak, and clog readings across three synthetic schedules")
    print(table.to_string(index=False))
    print("\nSynthetic demonstration only; not field-calibrated.")


if __name__ == "__main__":
    main()
