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
UrinPrep = UrineOutputPreProcessor(threshold=6)  # Hours of missing data threshold
```

## Creatinine Preprocessing

Ensures proper handling of creatinine values, including forward-filling missing data.

```python
CreatPrep = CreatininePreProcessor(
    stay_identifier="stay_id",
    time_identifier="charttime",
    ffill=True,  # Forward-fill missing values
    threshold=72  # Hours of missing data allowed
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
    Dataset(DatasetType.URINEOUTPUT, validation_data_unlabelled),
    Dataset(DatasetType.CREATININE, validation_data_unlabelled),
    Dataset(DatasetType.DEMOGRAPHICS, validation_data_unlabelled),
    Dataset(DatasetType.RRT, validation_data_unlabelled),
]

analyser = Analyser(
    data,
    preprocessors=[TimePrep, UrinPrep, CreatPrep, DemoPrep, RRTPrep]
)

results = analyser.process_stays()
```

In case of not specifying Preprocessing, the Analyser will run all five Preprocessing with its default setting. 

## Extracting Results for a Single Patient

```python
results_one_id = analyser.process_stay(stay_id=32314488)
print(results_one_id[:1])
```

