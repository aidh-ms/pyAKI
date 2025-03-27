# Preprocessing Functions in pyAKI

## Overview
Before analyzing **AKI (Acute Kidney Injury)** data, it's essential to preprocess it correctly. `pyAKI` provides multiple preprocessing functions to handle time indexing, creatinine levels, urine output, demographics, and renal replacement therapy (RRT) status.

## Importing Required Libraries

```python
from pyaki.kdigo import Analyser
from pyaki.preprocessors import (
    CreatininePreProcessor,
    DemographicsPreProcessor,
    RRTPreProcessor,
    TimeIndexCreator,
    UrineOutputPreProcessor
)
```

## Loading data


The input data includes patient id, event time,  weight, urine output, creatinine level and if the patient has undergone RRT or not.

```python
import pandas as pd

validation_data = pd.read_csv("tests/data/validation_data.csv")
```

## Time Index Creation

The `TimeIndexCreator` ensures that data is properly indexed by **time** before analysis.

```python
TimePrep = TimeIndexCreator(
    stay_identifier="stay_id",
    time_identifier="charttime"
)
```

## Urine Output Preprocessing

Handles missing or incorrect urine output values.

```python
UrinPrep = UrineOutputPreProcessor(
    stay_identifier="stay_id",
    time_identifier="charttime",
    interpolate=True,  # Flag indicating whether to interpolate missing values
    threshold=6,  # The threshold value for limiting the interpolation range
)
```

## Creatinine Preprocessing

Ensures proper handling of creatinine values, including forward-filling missing data.

```python
CreatPrep = CreatininePreProcessor(
    stay_identifier="stay_id",
    time_identifier="charttime",
    ffill=True,  # Forward-fill missing values
    threshold=72  # The threshold value for limiting the forward filling range
)
```

## Demographics Preprocessing

Processes patient demographic data (age, weight, gender, etc.).

```python
DemoPrep = DemographicsPreProcessor(
    stay_identifier="stay_id",
    time_identifier="charttime"
)
```

## Renal Replacement Therapy (RRT) Preprocessing

Processes RRT status changes.

```python
RRTPrep = RRTPreProcessor(
    stay_identifier="stay_id",
    time_identifier="charttime"
)
```

## Running Preprocessing Before Analysis

Before running an analysis, apply the preprocessing steps:

```python
data = [
    Dataset(DatasetType.URINEOUTPUT, validation_data),
    Dataset(DatasetType.CREATININE, validation_data),
    Dataset(DatasetType.DEMOGRAPHICS, validation_data),
    Dataset(DatasetType.RRT, validation_data),
]

analyser = Analyser(
    data,
    preprocessors=[TimePrep, UrinPrep, CreatPrep, DemoPrep, RRTPrep]
)

results = analyser.process_stays()
```

In case of not specifying Preprocessing, the Analyser will run all five Preprocessings with its default setting.

## Extracting Results for a Single Patient

```python
results_one_id = analyser.process_stay(stay_id=32314488)
print(results_one_id[:1])
```
