# External and simulated data: provenance and use

## Important distinction

WNTR is hydraulic simulation software, not an external dataset. The current project CSV, trained Random Forest model, threshold results, dashboard readings, and evaluation charts are generated from the group's WNTR model. They are synthetic results and must not be described as measured UOW or municipal data.

## External sources reviewed

| Source | What it contains | What it can support | What it does not provide for this project | Status in this prototype |
|---|---|---|---|---|
| Walid et al., [drip-irrigation pressure and flow dataset](https://data.mendeley.com/datasets/w9594tjkwp/2), Mendeley Data, 2024, DOI: 10.17632/w9594tjkwp.2 | Sensor measurements from a drip-irrigation system over five hours, including upstream and downstream pressure and flow. The record describes raw and filtered CSV files and 911 retained observations. | An external measured irrigation reference for checking units, plausible ranges, sensor behavior, and normal hydraulic readings. | The record does not label each observation as normal, leaking, or clogged; does not provide fault locations or severity labels; and covers only a short observation period rather than the project's three schedule profiles. | Reviewed as a candidate. Not yet downloaded, cleaned, or used in model training or dashboard results. |
| [LeakTestbed benchmark](https://waterfutures.github.io/WaterBenchmarkHub/benchmarks/LeakTestbed.html), associated with a peer-reviewed dataset paper | Controlled physical laboratory leak/no-leak experiments, dynamic pressure and acoustic sensor signals, different leak types, network layouts, background flows, noise conditions, and sensor locations. | External measured leak examples and a reference for leak signal behavior and leak localization research. | It is a generic laboratory water network, not an urban irrigation system; it does not contain clogged-emitter cases or planned watering schedules. | Reviewed as a candidate. Not yet integrated into the project's model or dashboard. |
| [Field study of drip-emitter flow and clogging](https://www.mdpi.com/2073-4441/11/6/1195) | Field measurements of emitter flow and irrigation uniformity; researchers recorded emitters with visibly reduced flow as indications of clogging. | External evidence about real emitter-flow variation and observed clogging in field irrigation. | It is not a labelled three-class dataset of normal/leak/clog events with schedule, location, and severity for the project's network. | Reviewed as a candidate. Check the article's available supplementary data before treating individual readings as reusable records. |

## What is currently simulated

- The three-zone network, pipe layout, junctions, and hydraulic parameter values.
- Morning, afternoon, and night schedule profiles and hourly demand values.
- Normal, leak, and clog scenarios, including their locations and mild, moderate, and severe settings.
- The pressure and flow values in `outputs/labeled_fault_scenarios.csv` and `outputs/normal_watering_scenarios.csv`.
- The Random Forest model, threshold-baseline predictions, comparison metrics, and dashboard results when they are generated from those project CSV files.
- The mapped pipe overlay and zone positions; the geographic image is context only and does not show actual irrigation infrastructure.

## What is externally measured (not yet part of the current results)

- The Mendeley irrigation dataset contains sensor readings collected from a physical drip-irrigation setup.
- LeakTestbed contains signals collected during controlled physical leak experiments in a laboratory-scale water network.
- The cited emitter study reports field measurements associated with visibly reduced-flow emitters.

These sources have different systems, sensors, units, sampling periods, and labels. They must retain their source and original labels. Do not append them to the WNTR CSV and imply they are one consistent dataset.

## Data-use plan

1. Obtain and inspect the original external files, their documentation, license, column definitions, units, sampling intervals, and labels before use.
2. Keep each external source as a separate raw file and record its citation, download date, and any cleaning steps.
3. Use suitable external measurements for evidence-based checks and, where labels and features support it, external model training or validation.
4. Simulate only the missing conditions required by the research question, such as schedule-labelled cases or clog/leak severities absent from the external data. Mark every generated row as synthetic and retain a `Data_Source` field.
5. Report external-data and simulation-based results separately. If datasets are combined for an experiment, explain the domain differences and evaluate whether results generalize across sources.

## Current limitation and next action

The current published prototype results are based on WNTR-generated synthetic data. The external sources above have been identified but have not yet been incorporated. Therefore, the current results do not demonstrate performance on external sensor data. The next data task is to inspect the Mendeley CSV and source documentation, then decide with the instructor whether its measured irrigation readings plus separately sourced physical leak/clog evidence meet the external-data requirement before simulating only the remaining gaps.
