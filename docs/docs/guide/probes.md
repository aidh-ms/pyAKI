# Using Probes in pyAKI

## Overview
Probes in `pyAKI` allow for detecting **Acute Kidney Injury (AKI)** based on different clinical markers such as **absolute or relative creatinine levels, urine output, and renal replacement therapy (RRT)**. The `AbsoluteCreatinineProbe`, `RelativeCreatinineProbe`, `UrineOutputProbe` and `RRT` provide various methods to define AKI stages. In general, it adds one resulted column for each specified probe and a general evaluation column of the AKI stage.

## Importing Required Libraries

```python
from pyaki.kdigo import Analyser
from pyaki.probes import (
    AbsoluteCreatinineProbe, CreatinineBaselineMethod, Dataset, DatasetType,
    RelativeCreatinineProbe, RRTProbe, UrineOutputMethod, UrineOutputProbe
)
```

## Loading Data

The input data included patient id, event time,  weight, urine output, creatinine level and if the patient has undergone RRT or not.

```python
import pandas as pd

validation_data = pd.read_csv("tests/data/validation_data.csv")
```

## Using Absolute Creatinine Probe

The `AbsoluteCreatinineProbe` determines AKI stages using the provided data frame and a predefined baseline calculation method (see table below for a comprehensive list of methods).

```python
AbsCreatProbe = AbsoluteCreatinineProbe(
    column="creat",
    method=CreatinineBaselineMethod.ROLLING_MIN,  # Choose any method from below
    baseline_timeframe = "1d" # Default value: "2d"
)
```

### List of Creatinine Baseline Calculation Methods

| Method               | Description | Usage Example |
|----------------------|-------------|---------------|
| **ROLLING_MIN**      | Uses the **minimum** creatinine value within a rolling window (default: 72) following the observation time as the baseline. | Suitable when analyzing **short-term trends** in creatinine fluctuations. |
| **ROLLING_FIRST**    | Uses the **first value** in a rolling window following the observation time as the baseline. | Use when the **earliest observed creatinine level** is expected to be the most accurate reference. |
| **ROLLING_MEAN**     | Uses the **mean** creatinine value within a rolling window. | Ideal for **smoothing fluctuations** in creatinine values over time. |
| **FIXED_MIN**        | Uses the **minimum creatinine value** from the **first n days** of observation (default: n = 72). | Best when a **low baseline value** from an early stage is needed. |
| **FIXED_MEAN**       | Uses the **mean creatinine value** from the **first n days** of observation. | Useful for creating a **stable baseline** based on initial observations. |
| **OVERALL_FIRST**    | Uses the **first recorded** creatinine value as the baseline. | Use when assuming the **first available measurement** represents the patient’s true baseline. |
| **OVERALL_MEAN**     | Uses the **mean** of **all observed** creatinine values as the baseline. | Best when considering **long-term average** creatinine levels. |
| **OVERALL_MIN**      | Uses the **minimum** of **all observed** creatinine values as the baseline. | Use when assuming the **lowest creatinine level** reflects normal kidney function. |
| **CONSTANT**         | Uses a **predefined constant value** as the baseline. | Useful for **benchmark comparisons** or when no historical data is available. |
| **CALCULATED**       | Uses a **calculated value** based on the **Cockcroft-Gault Formula** and **Adjusted Body Weight**. | Best for cases where **patient demographics (age, weight, gender)** influence baseline creatinine levels. |

The **Cockcroft-Gault Formula** is:

$$
\text{Creatinine Clearance, mg/dl} = \frac{(140 - \text{age}) \times \text{ABW} (\times 0.85 \text{ if female})}{70 \times \text{Expected Clearance}}
$$

where the **ABW (Adjusted Body Weight) Calculation** is:

$$
\text{ABW} = \text{IBW} + 0.4 \times (\text{weight} - \text{IBW}).
$$

### Example of constant baseline method

```python
validation_data_unlabelled['baseline_column'] = validation_data_unlabelled.loc[:, 'creat'].mean()

AbsCreatProbe = AbsoluteCreatinineProbe(column="creat",
                                baseline_constant_column = "baseline_column",
                                method=CreatinineBaselineMethod.CONSTANT)
```
### Example of calculated baseline method

See [below](###Special-case-of-calculated-baseline-method).


## Using Relative Creatinine Probe

The `RelativeCreatinineProbe` determines AKI stages by comparing changes in creatinine levels relative to baseline values. The list and use of available baseline methods is similar to of Absolute Creatinine Probe. The users are encouraged to look into [Absolute Creatinine Probe section](#Using-absolute-creatinine-probe).


```python
RelCreatProb = RelativeCreatinineProbe(
    column="creat",
    method=CreatinineBaselineMethod.ROLLING_MEAN,
    baseline_timeframe = "7d" #Default value: "7d"
)
```

## Using Urine Output Probe

The `UrineOutputProbe` assesses AKI based on **urine output levels**, considering patient weight and anuria thresholds.



```python
UrineProbe = UrineOutputProbe(
    column="urineoutput",
    patient_weight_column="patient_weight",
    anuria_limit=0.2, #Default value: 0.1
    method=UrineOutputMethod.STRICT #Choose a suitable method from below
)
```

The list of calculation methods includes:

### Urine Output Calculation Methods

| Method | Description | Usage Example |
|--------|-------------|---------------|
| **STRICT** | Strict method for urine output calculations. The urine output stage is calculated based on the **maximum** urine output in the past **6, 12, and 24 hours**. | Use this method for **precise tracking** of urine output in a specific window of time. |
| **MEAN**   | Mean method for urine output calculations. The urine output stage is calculated using the **average** urine output over a certain period. | Suitable for calculating **overall trends** in urine output over time. |

### Using RRT Probe
The Renal Replacement Therapy `RRT` Probe classifies a patient with a KDIGO stage 3 if the patient is on RRT at any time during the ICU stay. It will return 0 otherwise.

```python
RRTProbe = RRTProbe(column="rrt")
```

## Running Analysis with Probes

```python
data = [
    Dataset(DatasetType.URINEOUTPUT, validation_data_),
    Dataset(DatasetType.CREATININE, validation_data),
    Dataset(DatasetType.DEMOGRAPHICS, validation_data),
    Dataset(DatasetType.RRT, validation_data),
]

analyser = Analyser(
    data,
    probes=[UrineProbe, AbsCreatProbe, RelCreatProb] # Specify which probes used
)

results = analyser.process_stays()
```

### Special case of calculated baseline method


The usage of calculaed baseline method is different from others that we need to supply a new dataframe with information of age, height, weight and gender of each patient into data.


```python

random.seed(1)
n = len(validation_data)
age = random.choices(list(range(10,90)), k=n)
height = random.choices(list(range(140,180)), k=n)
gender = random.choices(["M", "F"], k=n)
added_validation_data["age"]= age
added_validation_data["height"] = height
added_validation_data["gender"] = gender


AbsCreatProbe = AbsoluteCreatinineProbe(column="creat", patient_age_column="age",
                                        patient_gender_column="gender",
                                        patient_height_column="height",
                                        patient_weight_column="patient_weight",
                                        expected_clearance = 72, #Default value: 72
                                        method=CreatinineBaselineMethod.CALCULATED)

data = [
    Dataset(DatasetType.URINEOUTPUT, validation_data),
    Dataset(DatasetType.CREATININE, validation_data),
    Dataset(DatasetType.DEMOGRAPHICS, added_validation_data),
    Dataset(DatasetType.RRT, validation_data_unlabelled),
]

analyser = Analyser(
    data,
    probes=[AbsCreatProbe]
)

results = analyser.process_stays()
```


## Extracting Results for a Single Patient

```python
results_one_id = analyser.process_stay(stay_id=32314488)
print(results_one_id.tail(1))
```
