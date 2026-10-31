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

## Design decisions

- **Reference table from normal data only.** We build a reference table using normal data. For each zone we calculate the expected flow and pressure by averaging the rows for each schedule and hour. Each reading is then compared to the expected value that matches its own schedule and hour. This keeps the baseline schedule-aware.
- **Tolerance bands.**We say that a zones reading is out of range if its flow differs from the expected value by more than the larger of 0.5 L/min or 5% of the expected flow.. If its pressure differs by more than the larger of 0.5 kPa or 0.1% of the expected pressure. The fixed minimum stops an expected value from producing a band that is too narrow.
- **Direction rules.** If flow is above the band and pressure is below the band we call that a leak. If flow is below the band and pressure is above the band we call that a clog.
- **No guessing.** If a readings is out of range but does not match either pattern we label it as 'unknown_fault' instead of assigning a fault type.
- **Choosing the zone.** If several zones meet a rule, the zone with the largest deviation of combined flow and pressure (each divided by its tolerance) is reported.
- **No labels in prediction.** We use the true labels only to pick normal rows for the reference table and later to score the results. We never use the labels to decide an alert.
- **How alerts are scored.** An 'unknown_fault' counts as an alert for the missed fault and false alert rates but counts as wrong in the three class comparison.


## Parameters and how they were chosen

| Parameter | Value | Reason |
|---|---|---|
| Flow tolerance | larger of 0.5 L/min or 5% of expected flow | Initial prototype value. The percentage scales with the size of the flow and the minimum keeps the band from becoming too narrow when expected flow is small. |
| Pressure tolerance | larger of 0.5 kPa or 0.1% of expected pressure | Initial prototype value. Pressures in this dataset are about 426 to 441 kPa so 0.1% is at most about 0.44 kPa and the 0.5 kPa minimum is always the one that applies. |

These values are initial engineering choices and were not calculated from data. To see how much they matter, all four tolerance settings were multiplied by a scale between 0.1 and 4 using 'threshold_analysis.py' across all schedules:

| Tolerance scale | Missed-fault rate | Three-class accuracy |
|---|---|---|
| 0.1 | 5.6% | 94.7% |
| 0.25 | 5.6% | 89.5% |
| 0.5 | 5.6% | 83.0% |
| 1 (current) | 8.6% | 73.4% |
| 2 | 15.1% | 55.6% |
| 4 | 44.1% | 36.3% |

Wider tolerances missed more faults and identified fewer fault types correctly. At the current setting, 19.4% of faults were reported as `unknown_fault`.In these cases the flow was outside its tolerance but the pressure change was smaller than the 0.5 kPa tolerance so neither fault rule matched. The false alert rate stayed at 0% at every scale because the simulated normal data contains no random variation . The tolerances therefore cannot yet be justified from data and should be chosen again once normal runs with realistic variation are available.

## Evidence for the leak and clog rules

The direction of change in the faulty zone was checked against the dataset ('threshold_analysis.py', saved as 'outputs/threshold_fault_direction.csv'):

- In all 162 leak records flow rose and pressure fell in the faulty zone.
- In 144 of the 162 clog records flow fell and pressure rose.
- In the other 18 clog records neither flow or pressure changed 

##Limitations

- **Clogs during zero demand cannot be detected.** In the afternoon schedule at hour 0 and the morning schedule at hour 5 demand is zero. A clog in these cases changes neither flow nor pressure. No method relying on these readings can detect it. This issue affects 18 clog records which is 5.6 percent of all fault records. Another 10 clog records at low demand, where demand multipliers are between 0.15 and 0.2, are also missed because the change is too small to be noticed within the tolerance level.
- **There is no variation in the data.** The simulation runs perfectly repeatable with one normal run for each schedule. The same normal rows are used to create the baseline and then tested again. Because of this the deviation for these cases is zero and the 0% false-alert rate is true by design. This does not tell us how the method would perform with real world data that includes noise or variability
- **The held out night schedule is used for evaluation.** The baseline is built using readings from the night schedule but the Random Forest model was trained without any data from that schedule. This is a deliberate design choice , since the baseline is schedule-aware and knows the planned schedule, but it means the two methods are not working with the same information.
- **Simulated data only.** All the readings come from a WNTR simulation using assumed pipe dimensions and demand patterns. The results are valid for these specific scenarios and the assumptions made. They may not apply to real-world systems with conditions.



