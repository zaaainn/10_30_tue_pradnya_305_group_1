"""Compare a normal case with illustrative leak and clog cases at Zone B.

Fault values are synthetic starting assumptions for the prototype, not
calibrated values or measurements from UOW Dubai.
"""

import pandas as pd
import wntr

from first_simulation import build_network


SIMULATION_TIME_SECONDS = 2 * 3600
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


def run_case(condition: str, severity: str | None = None) -> dict[str, object]:
    network = build_network()
    zone = network.get_node(FAULT_ZONE)

    if condition == "leak":
        zone.emitter_coefficient = LEAK_EMITTER_COEFFICIENTS[severity]
    elif condition == "clog":
        demand = zone.demand_timeseries_list[0]
        demand.base_value *= CLOG_DEMAND_FACTORS[severity]

    results = wntr.sim.EpanetSimulator(network).run_sim()
    pressure = results.node["pressure"].loc[SIMULATION_TIME_SECONDS, FAULT_ZONE]
    flow = results.link["flowrate"].loc[SIMULATION_TIME_SECONDS, "Branch_B"]

    return {
        "Condition": condition.title(),
        "Severity": severity.title() if severity else "—",
        "Location": FAULT_ZONE.replace("_", " ") if severity else "—",
        "Pressure (kPa)": float(pressure) * 9.80665,
        "Flow (L/min)": float(flow) * 60_000,
    }


def main() -> None:
    cases = [run_case("normal")]
    for severity in ("mild", "moderate", "severe"):
        cases.append(run_case("leak", severity))
        cases.append(run_case("clog", severity))

    table = pd.DataFrame(cases)
    normal_flow = table.loc[table["Condition"] == "Normal", "Flow (L/min)"].iloc[0]
    table["Flow change from normal (%)"] = (
        (table["Flow (L/min)"] - normal_flow) / normal_flow * 100
    ).round(1)
    table["Pressure (kPa)"] = table["Pressure (kPa)"].round(2)
    table["Flow (L/min)"] = table["Flow (L/min)"].round(2)

    print("Zone B readings during the same morning schedule (hour 2)")
    print(table.to_string(index=False))
    print("\nSynthetic demonstration only; not field-calibrated.")


if __name__ == "__main__":
    main()
