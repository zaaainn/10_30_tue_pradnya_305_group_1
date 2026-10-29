"""First WNTR run: a small illustrative three-zone irrigation network.

The network values are assumptions for a university prototype. They are not
measurements from UOW Dubai or its actual irrigation infrastructure.
"""

import pandas as pd
import wntr


def build_network() -> wntr.network.WaterNetworkModel:
    network = wntr.network.WaterNetworkModel()

    # A simple morning demand pattern: water the zones during hours 0 to 3.
    network.add_pattern("morning", [0.7, 1.0, 1.0, 1.0, 0.2, 0.0])

    network.add_reservoir("Source", base_head=50.0, coordinates=(0.0, 0.0))
    network.add_junction(
        "Manifold", base_demand=0.0, elevation=2.0, coordinates=(250.0, 0.0)
    )

    # Zone demand values are illustrative and expressed in m^3/s.
    zones = [
        ("Zone_A", "Branch_A", 0.00020, 250.0, 100.0),
        ("Zone_B", "Branch_B", 0.00022, 250.0, 0.0),
        ("Zone_C", "Branch_C", 0.00018, 250.0, -100.0),
    ]
    for zone_name, _, demand, x_coord, y_coord in zones:
        network.add_junction(
            zone_name,
            base_demand=demand,
            demand_pattern="morning",
            elevation=5.0,
            coordinates=(x_coord, y_coord),
        )

    network.add_pipe(
        "Main", "Source", "Manifold", length=250.0, diameter=0.20, roughness=120.0
    )
    for zone_name, branch_name, _, _, _ in zones:
        network.add_pipe(
            branch_name,
            "Manifold",
            zone_name,
            length=250.0,
            diameter=0.10,
            roughness=120.0,
        )

    network.options.time.duration = 6 * 3600
    network.options.time.hydraulic_timestep = 3600
    network.options.time.report_timestep = 3600
    network.options.time.pattern_timestep = 3600
    return network


def main() -> None:
    network = build_network()
    results = wntr.sim.EpanetSimulator(network).run_sim()

    # Show readings during the watering period at hour 2.
    time_seconds = 2 * 3600
    pressure = results.node["pressure"].loc[time_seconds]
    flow = results.link["flowrate"].loc[time_seconds]

    rows = []
    for zone_name, branch_name, *_ in [
        ("Zone_A", "Branch_A"),
        ("Zone_B", "Branch_B"),
        ("Zone_C", "Branch_C"),
    ]:
        rows.append(
            {
                "Zone": zone_name.replace("_", " "),
                "Pressure (kPa)": round(float(pressure[zone_name]) * 9.80665, 2),
                "Flow (L/min)": round(float(flow[branch_name]) * 60_000, 2),
            }
        )

    readings = pd.DataFrame(rows)
    print("Normal morning-cycle readings at hour 2")
    print(readings.to_string(index=False))
    print("\nThese are simulated readings from an illustrative network.")


if __name__ == "__main__":
    main()
