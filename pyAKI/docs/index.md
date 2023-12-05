# Welcome to the pyAKI User documentation

pyAKI was created to provide a simple and easy to use interface to work with time series data in order to use it for classifying the data according to the [KDIGO](https://kdigo.org/guidelines/acute-kidney-injury/) guidelines.

## Installation

pyAKI can be installed using pip:

```bash
pip install pyAKI
```

## Quick Reference

### Data Preparation

Pandas dataframes are expected as input in the following format:

- Urine Data
  - `stay_id`: A unique ID of the patient stay, the default is `stay_id`.
  - `timestamp`: The timestamp of the measurement, the default is `charttime`.
  - `value`: The value of the measurement, the default is `urineoutput`.
- Creatinine Data
  - `stay_id`: A unique ID of the patient stay, the default is `stay_id`.
  - `timestamp`: The timestamp of the measurement, the default is `charttime`.
  - `value`: The value of the measurement, the default is `creat`.
- Renal Replacement Therapy Data
  - `stay_id`: A unique ID of the patient stay, the default is `stay_id`.
  - `timestamp`: The timestamp of the measurement, the default is `charttime`.
  - `value`: The value of the measurement, the default is `rrt_status`.
- Demographic Data
  - `stay_id`: A unique ID of the patient stay, the default is `stay_id`.
  - `weight`: The weight of the patient, the default is `weight`.

Notice: Weight is the only required column in the demographic data for calculating the urine output stages. If you want to use the Cockcroft-Gault estimation for creatinine baseline estimation, you need to provide additional information, refer to the [Baseline Definitions](./baseline_defintions.md) for additional context.

### Usage

```python
from pyAKI.kdigo import Analyser
from pyAKII.probes import Dataset, DatasetType

results = Analyser(
        [
            Dataset(
                DatasetType.URINEOUTPUT,
                urineoutput_df,
            ),
            Dataset(
                DatasetType.CREATININE,
                creatinine_df,
            ),
            Dataset(
                DatasetType.DEMOGRAPHICS,
                demographics_df,
            ),
            Dataset(
                DatasetType.RRT,
                rrt_df,
            ),
        ]
    ).process_stays()
```
