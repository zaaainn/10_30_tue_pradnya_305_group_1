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

## 2026-10-29 — Added synthetic watering schedules

- **Change:** Added morning, afternoon, and night six-hour demand profiles to the WNTR network. `build_network(schedule)` now selects a profile, and both simulation scripts report readings at the representative active hour for each profile. The fault comparison now produces normal, mild, moderate, and severe leak/clog cases for Zone B under all three profiles.
- **Schedule assumptions:** Morning multipliers are `[0.7, 1.0, 1.0, 1.0, 0.2, 0.0]` with sample hour 2; afternoon multipliers are `[0.0, 0.15, 0.35, 0.55, 0.75, 0.3]` with sample hour 4; night multipliers are `[0.15, 0.3, 0.45, 0.6, 0.45, 0.2]` with sample hour 3. These are deliberately illustrative demand patterns, not field schedules.
- **Run evidence:** Both scripts ran successfully. Normal Zone B readings were 433.33 kPa / 13.20 L/min in the morning, 436.62 kPa / 9.90 L/min in the afternoon, and 438.21 kPa / 7.92 L/min at night. Across all profiles, simulated leaks increased branch flow and reduced pressure relative to that schedule's normal case; simulated clogs reduced flow and increased pressure.
- **Current scope:** Fault cases still target Zone B only. The dataset generator will need to cover other fault locations and export labeled records; that is separate from adding schedule options to this simulation step.
- **Limitations:** Schedules and fault parameters are synthetic assumptions. No observed UOW or municipal irrigation schedule or measurement is used.

## 2026-10-29 — Prepared app for future Render deployment

- **Change:** Updated the Streamlit map view to read `GOOGLE_MAPS_API_KEY` from an environment variable as well as local Streamlit secrets. Added future Render build/start command guidance to the README.
- **Reason:** The same prototype should support local development and a later hosted demonstration without storing the Google key in source code or GitHub.
- **Status:** Deployment preparation only; the app has not been deployed to Render.

## 2026-10-29 — Full normal watering-cycle scenarios

- **Change:** Added `watering_scenarios.py` to simulate every hourly demand multiplier in the morning, afternoon, and night profiles for Zones A, B, and C. It records scenario ID, schedule, hour, demand multiplier, normal label, zone, pressure, flow, and synthetic-data source in CSV format. A `--schedule` option allows one profile to be generated at a time.
- **Output:** The default run produces 54 labeled zone-reading rows (3 schedules × 6 hours × 3 zones) in `outputs/normal_watering_scenarios.csv`.
- **Repository decision:** `outputs/` and `work/` are ignored by default. The baseline CSV `outputs/normal_watering_scenarios.csv` is included as the shared sample dataset; other generated output files and temporary authoring files remain local.
- **Run evidence:** The project Python ran the script successfully. It created 54 rows across the three profiles, six hours, and three zones, and saved the CSV at `outputs/normal_watering_scenarios.csv`.
- **Status:** Normal watering-scenario generation is implemented and run. Full labeled leak/clog coverage is being added in the following entry.

## 2026-10-29 — Dataset view for the group dashboard

- **Change:** Added a `Watering data` dashboard view with schedule, condition, and fault-location filters, a complete table, summary counts, and CSV download. The dataset view identifies the readings as WNTR-generated simulation outputs.
- **Shared data:** The normal-operation sample contains 54 rows in `outputs/normal_watering_scenarios.csv`. The larger labeled dataset is tracked separately in `outputs/labeled_fault_scenarios.csv` and documented in `DATA_DICTIONARY.md`.
- **Verification:** The normal dataset was read back and confirmed to contain 54 rows, three schedules, and three zones. The expanded dataset is verified in the following entry.
- **Status:** Dataset view is ready to display the full scenario file once it is generated.

## 2026-10-29 — All-zone labeled fault scenario dataset

- **Change:** Generalized `fault_scenarios.py` so a user can select condition, severity, schedule, zone, and hour range. Added `generate_labeled_dataset.py` to run normal, leak, and clog configurations across all three zones and all six hours for each watering profile. Added `DATA_DICTIONARY.md` and connected the dashboard table to the full labeled dataset with schedule, condition, and location filters.
- **Dataset evidence:** The generator completed 57 configurations and 342 schedule-hour records: 18 normal, 162 leak, and 162 clog records. Each fault type covers Zones A, B, and C, with 54 records per zone and fault type. The dataset has 14 columns containing labels, schedule context, and three-zone pressure and flow features.
- **Interface evidence:** A selected Zone A moderate leak for the afternoon profile produced six hourly readings through the scenario interface.
- **Verification:** Python syntax compilation succeeded for the scenario interface, dataset generator, and dashboard. The generated CSV was read back and its row, column, configuration, condition, and location counts were confirmed.
- **Limitations:** Fault coefficients and clog demand reductions are simplified synthetic settings. Results describe these model scenarios, not calibrated field performance. Dataset rows sharing a `Scenario_ID` should be kept in the same partition for any later model evaluation.
- **Status:** Member 1 scenario coverage and the requested labeled dataset with data dictionary are implemented. ML training and threshold comparison are not part of this update.

## 2026-10-29 — Random Forest model and schedule-aware threshold baseline

- **Change:** Added `train_model.py`, `diagnosis.py`, and `predict_diagnosis.py`. The Random Forest predicts condition and, for predicted faults, the likely zone. The model bundle is saved to `models/random_forest_diagnosis.joblib`.
- **Training split:** The complete night schedule is held out; morning and afternoon records are used for training. The split keeps each `Scenario_ID` together and tests generalization to a schedule absent from training.
- **Initial held-out results:** On 114 night records, condition accuracy was 0.851 and macro F1 was 0.794. Fault-location accuracy on night fault records was 0.778. The night test contains only six normal records, so the normal-class recall estimate is especially limited (0.50); these results are preliminary and apply only to this synthetic dataset.
- **Threshold baseline:** Added `schedule_aware_threshold.py` and `THRESHOLD_METHOD.md`. It compares each zone's readings with the normal expectation for the same schedule and hour. Initial tolerances are the larger of 0.5 L/min or 5% for flow, and the larger of 0.5 kPa or 0.1% for pressure. In the current run it produced 296 alerts across 342 records, including 63 readings labeled `unknown_fault`; the thresholds have not been tuned or evaluated against field data.
- **Prediction artifacts:** The model prediction run produced 342 rows in `outputs/random_forest_predictions.csv`; threshold output was saved to `outputs/threshold_predictions.csv`. These run outputs remain local.
- **Verification:** Python syntax compilation succeeded, the model trained and saved, the prediction script completed, and the threshold script generated outputs.
- **Status:** Model and baseline implementations are available for group review. A controlled comparison and broader evaluation remain to be completed.

## 2026-10-29 — Method comparison and dashboard integration

- **Change:** Added `evaluate_methods.py` to run the Random Forest and schedule-aware threshold against the same 114 night-schedule records, held out from Random Forest training. It saves row-level predictions and a metric summary under the ignored local `outputs/` directory.
- **Measures:** Reports condition accuracy and macro F1, per-class precision and recall, fault-location accuracy, missed-fault rate, false-alert rate, clog recall by mild, moderate, and severe test conditions, and average backend processing time per record.
- **Preliminary comparison:** Random Forest: accuracy 0.851, macro F1 0.794, fault-location accuracy 0.778, missed-fault rate 0.000, false-alert rate 0.500. Schedule-aware threshold: accuracy 0.711, macro F1 0.775, fault-location accuracy 0.954, missed-fault rate 0.046, false-alert rate 0.000. For mild, moderate, and severe clogs, respectively, recall was 0.611, 0.667, and 0.944 for Random Forest, and 0.389, 0.556, and 0.667 for the threshold method.
- **Dashboard integration:** Added a Method comparison view showing metric summaries, per-class precision/recall, clog recall by severity, and filterable held-out row predictions from both methods. The pipeline view points users to this diagnosis view.
- **Limitations:** The held-out set has only six normal records, so the false-alert rate and normal-class results are highly sensitive to individual cases. All data are synthetic; these preliminary figures do not establish performance on real networks. Processing timing is backend time per record and excludes dashboard rendering and user selection.
- **Verification:** The comparison script completed and wrote the prediction and metric outputs. Python syntax compilation succeeded for the dashboard, comparison, and threshold modules. The pipeline view was visually reviewed in the later Member 1 interface review; visual review of the Method comparison view remains pending.

## 2026-10-29 — Member 1 pipeline and scenario interface review

- **Dashboard review:** Opened the local Streamlit prototype and checked the pipeline view. The three-zone topology and baseline readings render; selecting Zone B highlights its marker while the other zones remain visible. The dashboard caption identifies the topology and readings as simulated.
- **Scenario interface review:** Ran a moderate Zone A leak scenario for the afternoon schedule across all six hours. The generator returned six hourly records for all three zones, with the selected fault label and synthetic-data source recorded.
- **Outcome:** Both interfaces behaved as expected in this review; no code change was required. The scenario run was a functional check of simulated output, not validation against a real irrigation network.

## 2026-10-29 — Member 1 hydraulic response review

- **Review:** Compared each faulted zone's pressure and flow with the matching normal schedule and hour in the generated dataset. During active watering, leak cases consistently increased flow and reduced pressure; clog cases consistently reduced flow and increased pressure. The shifts generally grew with the configured mild, moderate, and severe settings.
- **Edge case:** In 18 of 324 faulted zone-hour records, a clog produced the same readings as normal operation because the schedule had zero demand at that hour. This is an expected unobservable case for the current demand-reduction clog model and should be retained as a difficult test case.
- **Group review:** These checks are a technical review of the simulation output. Group feedback on whether the assumed fault responses and zero-demand handling are acceptable is still pending; no calibration to field measurements is claimed.

## 2026-10-29 — Streamlit study-area and pipeline views

- **Change:** Added `app.py` with two local dashboard views: a study-area view and a larger pipeline topology view with normal baseline readings. Added Matplotlib to `requirements.txt` and dashboard launch instructions to the README. The study-area view supports Google satellite imagery when a local API key is configured and otherwise falls back to an offline illustration.
- **Decision:** Satellite tiles are used only as geographic context. The circle, pipeline overlay, and zone locations are explicitly labeled illustrative because the model does not use real UOW or city infrastructure data. API keys are stored locally and must not be committed.
- **Status:** Study-area and pipeline views remain available; the separate Method comparison view now shows classifier and threshold diagnoses. Satellite-key setup and study-area visual review remain pending.

## 2026-10-29 — Member 1 review commits pushed

- **Version history:** Commits `42d4577` (pipeline and scenario interface review) and `3a19017` (hydraulic response review and edge case) were pushed to the shared GitHub repository by the user.
- **Status:** Group feedback on the simulated fault responses and zero-demand clog case remains pending.

## 2026-10-29 — Replace Google satellite view with Esri imagery

- **Change:** Replaced the Google Maps JavaScript view with Esri ArcGIS imagery through MapLibre and Esri's supported MapLibre plugin. The satellite view retains the illustrative 3 km circle, hypothetical source/manifold/zones, and clear simulation-only notices.
- **Configuration:** Changed the local/Render setting to `ARCGIS_API_KEY` and updated the example secrets file and README setup instructions. The offline illustration remains available when no Esri key is configured.
- **Verification:** Python syntax compilation and Git whitespace checks succeeded. Live Esri imagery could not be visually verified because an ArcGIS access key with Basemaps access has not yet been configured in this environment.

## 2026-10-29 — Wait for Esri basemap before drawing overlays

- **Finding:** The user's screenshot confirmed that Esri satellite tiles and attribution loaded, but the 3 km ring and hypothetical network overlays were absent.
- **Change:** Updated the map to add the ring, links, and zone markers only after the Esri style is loaded and ready for overlays.
- **Verification:** Python syntax compilation and `git diff --check` passed. Visual confirmation of the overlays is pending a browser refresh.
