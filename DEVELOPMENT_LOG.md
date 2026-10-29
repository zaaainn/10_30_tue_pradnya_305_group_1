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

## 2026-10-29 — Offline UOW Dubai study-area schematic

- **Change:** Replaced the online street-map preview with a self-contained offline diagram showing a 3 km study radius, a UOW Dubai reference point, a hypothetical source, three hypothetical zones, and schematic connections. The WNTR node coordinates are local diagram coordinates in metres, not geographic coordinates.
- **Decision:** OpenStreetMap could not be used, so the visual is a schematic rather than a street map. UOW Dubai is included only as the study-area reference; its official contact page lists the campus in Dubai Knowledge Park.
- **Limitations:** The circle and node positions are illustrative. They do not identify real parks, city assets, or campus irrigation pipes. The hydraulic model remains synthetic.
- **Status:** Offline preview created; user review pending.

## 2026-10-29 — Network parameter adjustment

- **Change:** Reduced the assumed main pipe diameter from 200 mm to 100 mm and zone branch diameters from 100 mm to 35 mm. Clarified that Zones A-C are generic simulated irrigation sectors, not named parks or actual infrastructure. Removed the misleading scale bar from the offline schematic because the diagram is not to scale.
- **Reason:** Initial simulations showed almost no pressure response because the assumed pipes were very wide relative to the simulated flows. A local WNTR parameter check with 35 mm branches produced a normal Zone B pressure near 433.3 kPa; mild, moderate, and severe leak cases produced approximately 432.0, 429.5, and 425.7 kPa, while the three clog cases produced approximately 436.0, 438.6, and 440.3 kPa. Flow also changed in opposite directions for leaks and clogs.
- **Limitations:** These are illustrative synthetic parameters, not calibrated pipe sizes or field measurements. The group should review the assumptions and note that performance conclusions apply only to these simulated conditions.
- **Run evidence:** The user ran both scripts successfully. Normal Zone B was 433.33 kPa and 13.20 L/min. Leak cases ranged from 431.98 kPa and 14.39 L/min (mild) to 425.66 kPa and 19.13 L/min (severe). Clog cases ranged from 435.97 kPa and 10.56 L/min (mild) to 440.30 kPa and 3.96 L/min (severe). Zone A/C normal readings were 434.57/435.71 kPa with flows of 12.0/10.8 L/min.
- **Status:** Step 1 confirmed by a successful user run. The parameters remain illustrative assumptions, not field-calibrated values.

## 2026-10-29 — Streamlit study-area and pipeline views

- **Change:** Added `app.py` with two local dashboard views: a study-area view and a larger pipeline topology view with normal baseline readings. Added Matplotlib to `requirements.txt` and dashboard launch instructions to the README. The study-area view supports Google satellite imagery when a local API key is configured and otherwise falls back to an offline illustration.
- **Decision:** Satellite tiles are used only as geographic context. The circle, pipeline overlay, and zone locations are explicitly labeled illustrative because the model does not use real UOW or city infrastructure data. API keys are stored locally and must not be committed.
- **Status:** Dashboard view implementation added; satellite-key setup and visual review pending. The highlighted fault control is a visual aid only and is not connected to a classifier.
