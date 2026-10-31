# Evidence Log — Dataset Generation and Validation

**Project:** Schedule-Aware irrigation fault diagnosis  
**Contributor:** Saarah Deen  
**Role:** Dataset generation and validation

## Evidence E01 — Project Setup

- **Activity:** Downloaded and extracted the latest project version from GitHub.
- **Verification:** Confirmed that `generate_labeled_dataset.py`, `DEVELOPMENT_LOG.md`, and `DATA_DICTIONARY.md` are present.
- **Result:** Required project files located successfully.
- **Evidence file:** To be added.
- **GitHub commit:** To be added.


## Evidence E02 — Dataset Generation

- **Activity:** Executed `generate_labeled_dataset.py` using Python 3.11.
- **Output:** `outputs/labeled_fault_scenarios.csv`.
- **Result:** Successfully generated 342 labelled schedule-hour rows from 57 unique scenario configurations.
- **Condition distribution:** 162 clog, 162 leak and 18 normal records.
- **Fault location distribution:** 108 records each for Zone A, Zone B and Zone C, and 18 records with no fault location.
- **Data source:** WNTR hydraulic simulation; no field sensor data included.
- **Evidence file:** `evidence/01_dataset_generation/E02_dataset_generation.png`.

## Evidence E03 — Missing Value Validation

- **Activity:** Loaded `outputs/labeled_fault_scenarios.csv` using pandas and checked all columns for missing values.
- **Dataset dimensions:** 342 rows × 14 columns.
- **Columns checked:** 14.
- **Total missing values:** 0.
- **Result:** All 14 columns contained zero missing values. The dataset passed the missing-value completeness check.
- **Evidence file:** `evidence/02_missing_values/E03_missing_values.png`.

## Evidence E04 — Dataset Label Validation

- **Activity:** Used pandas to inspect the value counts and unique categories of the Condition, Fault_Location, Schedule and Severity columns.
- **Dataset dimensions:** 342 rows × 14 columns.

**Condition distribution:**
- Normal: 18
- Leak: 162
- Clog: 162

**Fault location distribution:**
- Zone A: 108
- Zone B: 108
- Zone C: 108
- None: 18

**Schedule distribution:**
- Morning: 114
- Afternoon: 114
- Night: 114

**Severity distribution:**
- Mild: 108
- Moderate: 108
- Severe: 108
- None: 18

- **Result:** All expected categories are represented across the four inspected columns. The category counts are consistent with the expected dataset structure.
- **Evidence file:** `evidence/03_label_validation/E04_label_validation.png`.

## Evidence E05 — Development Log Update

- **Activity:** Updated `DEVELOPMENT_LOG.md` to document the dataset validation activities, including missing-value checks, label distribution analysis, fault-location verification and condition-severity consistency checks.
- **Result:** The development log now contains a dated record of the completed dataset validation activities, their results and remaining limitations.
- **Evidence file:** `evidence/05_development_log/E05_development_log.png`.

## Evidence E06 — Condition and Label Consistency Validation

- **Activity:** Used pandas crosstab analysis to examine the relationship between Condition, Fault_Location and Severity.
- **Dataset dimensions:** 342 rows × 14 columns.

**Condition vs Fault Location:**
- Leak: 54 scenarios per zone (A, B and C).
- Clog: 54 scenarios per zone (A, B and C).
- Normal: 18 scenarios with no fault location.

**Condition vs Severity:**
- Leak: 54 mild, 54 moderate and 54 severe scenarios.
- Clog: 54 mild, 54 moderate and 54 severe scenarios.
- Normal: 18 scenarios with no severity.

- **Result:** No inconsistencies were detected between condition, fault location and severity labels. All inspected relationships matched the expected dataset structure.
- **Evidence file:** `evidence/03_label_validation/E06_label_consistency.png`.

## Evidence E07 — Numerical Sensor Data Validation

- **Activity:** Used pandas to inspect descriptive statistics, minimum and maximum values, and negative and near-zero flow readings across all six pressure and flow sensor columns.
- **Dataset dimensions:** 342 rows × 14 columns.
- **Result:** All six sensor columns contained 342 populated measurements. Pressure and flow ranges were inspected. Three negligible negative Zone A flow readings were identified during zero-demand scenarios and retained as numerical simulation outputs. No significant negative flow values were detected. Physical calibration against real irrigation measurements remains unverified.
- **Evidence files:**
  - `evidence/04_zone_schedule_validation/E07_sensor_data_validation.png`
  - `evidence/04_zone_schedule_validation/E07_negative_flow_investigation.png`

## Evidence E08 — Zone and Schedule Validation

- **Activity:** Used pandas to verify schedule balance, condition distribution, fault-location distribution and sensor behaviour across Zones A, B and C.
- **Result:** Confirmed 114 records per schedule, balanced condition and fault-location distributions, and consistent normal-scenario relationships between demand multipliers, pressure and flow. Higher simulated demand corresponded to higher flow and lower pressure across all three zones.
- **Evidence file:** `evidence/04_zone_schedule_validation/E08_zone_schedule_validation.png`.
