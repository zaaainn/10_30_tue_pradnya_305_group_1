# Schedule-Aware Irrigation Fault Diagnosis

This repository contains a simulation-based university prototype for distinguishing normal irrigation operation, pipe leaks, and clogged emitters or sprinkler heads.

## Scope

- The study area is a 3 km radius around UOW Dubai, used as geographic context only.
- The simulated irrigation network has three generic irrigation sectors (Zones A, B, and C). They are not mapped to named parks and do not represent the university's real pipes or irrigation equipment.
- `uow_study_area_map.html` is a self-contained offline schematic showing the 3 km study radius and hypothetical node locations. It does not use street-map tiles or represent actual pipe locations.
- UOW Dubai is used only as a geographic reference point; its official contact page lists the campus address in Dubai Knowledge Park: [UOW Dubai contact page](https://www.uowdubai.ac.ae/contact-us).
- The intended model inputs are simulated pressure, flow, and watering-schedule information.
- The classifier will be compared with a schedule-aware threshold alert using the same test scenarios.
- Pipe dimensions and demands are prototype assumptions selected to produce visible simulated hydraulic changes; they are not calibrated field values.

## Setup

Use 64-bit Python 3.13. Create an isolated environment and install the listed packages:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## First simulation

Run the initial normal three-zone morning-cycle simulation:

```powershell
.\.venv\Scripts\python.exe .\first_simulation.py
```

The network parameters are illustrative assumptions, not field measurements. See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for progress and evidence notes.

## First fault comparison

Run the initial same-schedule leak and clog comparison at Zone B:

```powershell
.\.venv\Scripts\python.exe .\fault_scenarios.py
```

This first comparison uses illustrative leak emitter coefficients and reduced zone demand as a simple clog surrogate. These fault settings require further review before they are used to generate classifier training data.
