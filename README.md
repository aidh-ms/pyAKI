# pyAKI

Python package to detect AKI within time series data.

The goal of this package is to establish well tested, comprehensive functions for the detection of Acute Kidney Injury (AKI) in time series data, according to the Kidney Disease Improving Global Outcomes (KDIGO) Criteria, established in 2012 [^kdigo].

## Installation
```
pip install git+https://github.com/AI2MS/pyAKI
```

## Usage
```python
from pyAKI import process_stay
process_stay(stay_id: int,
             urine_output: pd.DataFrame,
             creatinine: pd.DataFrame,
             weight: float,
             stay_identifier: str = 'stay_id',
             time_identifier: str = 'charttime')
```

### Tests

```shell
PYTHONPATH=. pytest
```

![kdigo_criteria](img/kdigo_criteria.png)

[^kdigo]: Khwaja A. KDIGO clinical practice guidelines for acute kidney injury. Nephron Clin Pract. 2012;120(4):c179-84. doi: 10.1159/000339789. Epub 2012 Aug 7. PMID: 22890468.
