"""First WNTR run: a small illustrative three-zone irrigation network.

The network values are assumptions for a university prototype. They are not
measurements from UOW Dubai or its actual irrigation infrastructure.
"""

import pandas as pd
import wntr


# Schematic local coordinates in metres, with the UOW Dubai campus as (0, 0).
# These are for a diagram only; no external map coordinates are used.
UOWD_CENTER = (0.0, 0.0)
MAP_NODES = {
    "Source": (-250.0, 0.0),
    "Manifold": UOWD_CENTER,
    "Zone_A": (0.0, 250.0),
    "Zone_B": (250.0, 0.0),
    "Zone_C": (0.0, -250.0),
}

# Illustrative six-hour demand profiles. Multipliers are synthetic assumptions,
# not observed irrigation schedules. The representative peak hour is simulated
# for each profile when producing a compact comparison table.
SCHEDULE_PROFILES = {
    "morning": [0.7, 1.0, 1.0, 1.0, 0.2, 0.0],
    "afternoon": [0.0, 0.15, 0.35, 0.55, 0.75, 0.3],
    "night": [0.15, 0.3, 0.45, 0.6, 0.45, 0.2],
}
SCHEDULE_SAMPLE_HOUR = {"morning": 2, "afternoon": 4, "night": 3}


def build_network(schedule: str = "morning") -> wntr.network.WaterNetworkModel:
    if schedule not in SCHEDULE_PROFILES:
        choices = ", ".join(SCHEDULE_PROFILES)
        raise ValueError(f"Unknown schedule {schedule!r}. Choose one of: {choices}")

    network = wntr.network.WaterNetworkModel()

    for name, multipliers in SCHEDULE_PROFILES.items():
        network.add_pattern(name, multipliers)

    network.add_reservoir("Source", base_head=50.0, coordinates=MAP_NODES["Source"])
    network.add_junction(
        "Manifold", base_demand=0.0, elevation=2.0, coordinates=MAP_NODES["Manifold"]
    )

    # Zones A-C are generic simulated irrigation sectors, not named real parks.
    # Demand values are illustrative and expressed in m^3/s.
    zones = [
        ("Zone_A", "Branch_A", 0.00020),
        ("Zone_B", "Branch_B", 0.00022),
        ("Zone_C", "Branch_C", 0.00018),
    ]
    for zone_name, _, demand in zones:
        network.add_junction(
            zone_name,
            base_demand=demand,
            demand_pattern=schedule,
            elevation=5.0,
            coordinates=MAP_NODES[zone_name],
        )

    # Assumed pipe sizes are chosen to produce measurable hydraulic responses
    # at the prototype's illustrative flow rates; they are not field data.
    network.add_pipe(
        "Main", "Source", "Manifold", length=250.0, diameter=0.10, roughness=120.0
    )
    for zone_name, branch_name, _ in zones:
        network.add_pipe(
            branch_name,
            "Manifold",
            zone_name,
            length=250.0,
            diameter=0.035,
            roughness=120.0,
        )

    network.options.time.duration = 6 * 3600
    network.options.time.hydraulic_timestep = 3600
    network.options.time.report_timestep = 3600
    network.options.time.pattern_timestep = 3600
    return network


def main() -> None:
    rows = []
    for schedule, sample_hour in SCHEDULE_SAMPLE_HOUR.items():
        network = build_network(schedule)
        results = wntr.sim.EpanetSimulator(network).run_sim()
        time_seconds = sample_hour * 3600
        pressure = results.node["pressure"].loc[time_seconds]
        flow = results.link["flowrate"].loc[time_seconds]

        for zone_name, branch_name in [
            ("Zone_A", "Branch_A"),
            ("Zone_B", "Branch_B"),
            ("Zone_C", "Branch_C"),
        ]:
            rows.append(
                {
                    "Schedule": schedule.title(),
                    "Hour": sample_hour,
                    "Zone": zone_name.replace("_", " "),
                    "Pressure (kPa)": round(float(pressure[zone_name]) * 9.80665, 2),
                    "Flow (L/min)": round(float(flow[branch_name]) * 60_000, 2),
                }
            )

    readings = pd.DataFrame(rows)
    print("Normal readings at the representative active hour for each schedule")
    print(readings.to_string(index=False))
    print("\nAll schedules and readings are synthetic assumptions and outputs.")


if __name__ == "__main__":
    main()
