# Irrigation Diagnosis Project — Chat Notes Backup

## Agreed project scope

- Study area context: a 3 km radius around UOW Dubai in Dubai Knowledge Park.
- The map location is contextual. The simulated pipes and readings are not claimed to represent UOW Dubai's actual irrigation infrastructure.
- Simulated network: one water source connected to three irrigation zones, labelled A, B, and C.
- Scenarios: normal operation, pipe leak, and clogged emitter or sprinkler head.
- Vary watering schedule, fault severity (mild, moderate, severe), and fault location.
- Model inputs: simulated pressure readings, flow readings, and watering schedule.
- Classifier outputs: condition and likely affected zone or pipe segment. Severity is currently a test condition, not a model output.
- Compare a Random Forest classifier with a schedule-aware threshold alert using the same held-out simulated scenarios.
- No real sensors, live network, or field validation are included in the current scope.

## Intended software

- Python for the prototype.
- WNTR with EPANET for hydraulic network simulation.
- pandas and NumPy for organizing simulated data.
- scikit-learn for the Random Forest model.
- Streamlit for the dashboard.
- GitHub for version history and evidence of development.
- QGIS or a map may be used to show the 3 km study-area context; it is optional and does not provide actual irrigation pipe data.

## Intended data flow

1. Define the small network, schedules, and fault scenarios.
2. Simulate pressure and flow readings for normal operation, leaks, and clogs.
3. Store the correct scenario labels (condition, severity, location) separately from the model input readings.
4. Train the classifier and create the schedule-aware threshold baseline.
5. Test both methods on the same held-out scenarios, including cases with similar readings.
6. Show scenarios, readings, predictions, alerts, and evaluation metrics in the dashboard.

## Evaluation measures discussed

- Condition classification: per-class precision and recall, plus macro F1 for normal, leak, and clog.
- Fault location accuracy on fault cases.
- Missed-fault rate and false-alert rate for each system.
- Clog recall reported separately for mild, moderate, and severe simulated clogs.
- Response time from scenario submission to results appearing in the dashboard.

## Six-person work split discussed

1. WNTR network model and three zones.
2. Watering schedules and normal simulations.
3. Leak/clog scenario injection and labelled data generation.
4. Random Forest condition and location prediction.
5. Schedule-aware threshold and evaluation metrics.
6. Streamlit dashboard, integration, and evidence log.

## Six-day target discussed

- Day 1: agree on network/data format, set up software, run one normal simulation.
- Day 2: add schedules and normal readings.
- Day 3: add leak/clog scenarios and labelled data.
- Day 4: build classifier and threshold baseline.
- Day 5: connect the dashboard and evaluation.
- Day 6: resolve integration issues, capture screenshots, and prepare evidence.

This is a plan summary, not a record that the implementation has already been completed.

## Environment check

- Python 3.14.6 is present in the project environment.
- WNTR, scikit-learn, pandas, and Streamlit were not installed at the time of the check.
- WNTR's installation guide lists Python 3.10–3.13 as tested versions. A compatible Python environment is needed before implementation.
- Windows Package Manager (`winget`) was present as a command alias but could not be launched in the current environment. Python launcher listed Python 3.14 only.
