# Development Log

## 2026-10-29 — Initial normal-operation simulation

- **Change:** Added `first_simulation.py`, a small WNTR/EPANET model with a source, a manifold, and three irrigation zones using an illustrative morning demand pattern.
- **Purpose:** Establish a working normal-operation baseline before adding leak and clog scenarios.
- **Evidence:** The user ran the script in the project environment. At hour 2, the displayed results were approximately 441.25, 441.24, and 441.26 kPa for Zones A, B, and C, with flows of 12.0, 13.2, and 10.8 L/min, respectively.
- **Limitations:** These values come from assumed synthetic model parameters. They are not measurements from UOW Dubai. Leak and clog scenarios, model training, threshold comparison, and the dashboard remain to be implemented.
- **AI assistance:** The initial simulation script and this log entry were prepared with AI assistance. The group should review and adapt the code and wording before submission.

## 2026-10-29 — First leak and clog scenario comparison

- **Change:** Added `fault_scenarios.py` to compare normal operation with mild, moderate, and severe leak and clog cases at Zone B under the same morning schedule.
- **Evidence:** The user ran the script. Normal flow was 13.20 L/min; leak flows were 14.41, 16.42, and 19.24 L/min; clog flows were 10.56, 7.26, and 3.96 L/min. Pressure remained approximately 441.2–441.3 kPa in all cases.
- **Observation:** The flow readings change clearly in the expected direction, while pressure changes are very small in this initial network. Review pipe dimensions, network resistance, and measurement locations before training a classifier that relies on pressure patterns.
- **Fault-model limitation:** The leak is represented by an emitter at the zone junction, and clogging is represented by reduced zone demand. These are simplified scenario surrogates and have not been hydraulically calibrated.
- **AI assistance:** AI-assisted code was reviewed by the user through a successful run; further group review and calibration remain necessary.
