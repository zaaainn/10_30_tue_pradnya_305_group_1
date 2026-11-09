# Testing, Validation and Iteration Report

**Run date:** 8 November 2026  
**Prototype:** WNTR-generated irrigation readings, saved Random Forest diagnosis model, schedule-aware threshold baseline  
**Evaluation command:** `.venv\\Scripts\\python.exe evaluate_methods.py`

## Scope and procedure

Both methods were run against the same 114 held-out night-schedule records, covering 19 scenario configurations: normal operation plus leak and clog cases for all three zones and three severities. The Random Forest training split excludes the entire night schedule. Predictions were compared with the recorded scenario labels and locations. All readings are synthetic simulation outputs; this evaluates the working prototype, not live UOW infrastructure or real field performance.

## Main results

**Key finding:** On the held-out night schedule, Random Forest achieved higher overall classification accuracy and macro F1 than the schedule-aware threshold baseline. It also detected every simulated fault case, had higher overall leak recall and higher clog recall at each reported severity. This supports Random Forest as the stronger overall fault-classification method in these tested scenarios. The threshold baseline was better at locating faults and avoiding false warnings, so those trade-offs remain part of the result.

| Measure | Random Forest | Schedule-aware threshold |
|---|---:|---:|
| Classification accuracy | 85.1% | 71.1% |
| Macro F1 | 79.4% | 77.5% |
| Fault-location accuracy | 77.8% | 95.4% |
| Missed-fault rate | 0.0% (0/108) | 4.6% (5/108) |
| False-warning rate on normal cases | 50.0% (3/6) | 0.0% (0/6) |
| Mild-clog recall | 61.1% (11/18) | 38.9% (7/18) |
| Moderate-clog recall | 66.7% (12/18) | 55.6% (10/18) |
| Severe-clog recall | 94.4% (17/18) | 66.7% (12/18) |
| Mean backend processing time per record | 1.616 ms on this run | 0.191 ms on this run |

The fault missed-rate counts faults for which the method produced no alert. A wrong fault-type prediction can still count as an alert, so classification errors are also reported separately through precision, recall and F1.

For the research question, the most relevant overall measures are classification accuracy and macro F1: both are higher for Random Forest in this held-out test. The fault-location and false-warning measures show where the simpler threshold baseline remains useful. The measurements do not establish that either method will perform the same way with field data.

## Test cases: AI-suggested and manually selected

| Test origin and case | Records | Random Forest result | Threshold result | Finding |
|---|---:|---|---|---|
| AI-suggested edge case: mild clogs across Zones A, B and C during the night schedule | 18 | Correct clog class: 61.1%; correct location: 66.7% | Correct clog class: 38.9%; correct location: 72.2%; 27.8% not alerted | Mild clogs are difficult for both methods. The classifier recognized more clogs, while the threshold method located the affected zone more often. |
| Manually selected routine check: normal night operation | 6 | 50.0% classified normal; 50.0% false warnings | 100.0% classified normal; 0.0% false warnings | The classifier raised three false warnings in six normal readings. |
| Manually selected clear-fault check: severe leaks across Zones A, B and C during the night schedule | 18 | Correct leak class and location: 100% | Correct leak class and location: 100% | Both methods handled these clear simulated leak cases. |

The night profile uses a demand multiplier of 0.15. A zero-demand/no-watering fault case is not present in this dataset, so that edge case remains untested.

## Retest and iteration record

The full evaluation was run twice. The second run produced the same prediction CSV byte-for-byte (SHA-256: `4B230141170BA63073541231C974A68CCDCCAD5408932A44786AF4CAA2D38C9D`). The measured processing times differed between runs, so they are reported as backend timing observations rather than stable dashboard response-time results.

**Successes:** the evaluation completed for both methods on identical held-out cases; the classifier had higher macro F1 and no missed fault alerts; the threshold method had higher fault-location accuracy and no false warnings; the prediction retest was reproducible.

**Failures and limitations:** the classifier produced three false warnings among six normal cases; both methods had weak mild-clog recall; the classifier's location accuracy was lower than the threshold method; and no zero-demand test was available. The response-time metric currently measures backend processing only, not the full time from selecting a dashboard scenario until the displayed result appears.

**Iteration decision:** keep the held-out night results untouched for reporting rather than tuning model or threshold settings against the test set. For the next iteration, add explicit zero-demand scenarios, investigate the normal-operation false warnings and mild-clog errors using training/validation data, then evaluate any revised version on a fresh held-out test set. Measure dashboard end-to-end response time separately in the browser.

## Evidence files

- `outputs/method_comparison_metrics.json` — machine-readable metric summary.
- `outputs/method_comparison_predictions.csv` — per-record truth and both methods' predictions.
