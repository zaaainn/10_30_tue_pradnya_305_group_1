# Schedule-aware threshold baseline

## Baseline construction

The baseline stores expected pressure and flow for every watering schedule and hour. These expected values are calculated from the rows labeled `normal` in the WNTR-generated dataset and grouped by `Schedule` and `Hour`. An observation is compared only with the baseline for its own planned schedule and hour.

For each of the three zones, the default flow tolerance is the larger of **0.5 L/min** or **5%** of expected flow. The default pressure tolerance is the larger of **0.5 kPa** or **0.1%** of expected pressure. These are initial engineering thresholds for the prototype and may be revised during evaluation.

## Alert and direction rules

- If every zone stays within both tolerances, report `normal` with no alert.
- If a zone's flow rises beyond its tolerance while its pressure falls beyond its tolerance, report a likely `leak` at that zone.
- If a zone's flow falls beyond its tolerance while its pressure rises beyond its tolerance, report a likely `clog` at that zone.
- If readings exceed a tolerance but the pressure and flow directions do not match either fault rule, raise an alert labeled `unknown_fault` rather than assigning an unsupported fault type.
- If several zones meet a rule, select the zone with the largest combined normalized pressure and flow deviation.

## Limitations

This is a schedule-aware rule baseline, not a calibrated operational standard. Its baseline and tolerances use synthetic model outputs. A clog during a scheduled zero-demand hour may produce no observable hydraulic difference, so the baseline may not alert. The method and thresholds should be evaluated against the same held-out scenario records used for the machine-learning model.
