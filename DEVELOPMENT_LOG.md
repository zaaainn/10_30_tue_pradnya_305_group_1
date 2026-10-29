# Development Log

## 2026-10-29 — Initial normal-operation simulation

- **Change:** Added `first_simulation.py`, a small WNTR/EPANET model with a source, a manifold, and three irrigation zones using an illustrative morning demand pattern.
- **Purpose:** Establish a working normal-operation baseline before adding leak and clog scenarios.
- **Evidence:** The user ran the script in the project environment. At hour 2, the displayed results were approximately 441.25, 441.24, and 441.26 kPa for Zones A, B, and C, with flows of 12.0, 13.2, and 10.8 L/min, respectively.
- **Limitations:** These values come from assumed synthetic model parameters. They are not measurements from UOW Dubai. Leak and clog scenarios, model training, threshold comparison, and the dashboard remain to be implemented.
- **AI assistance:** The initial simulation script and this log entry were prepared with AI assistance. The group should review and adapt the code and wording before submission.
