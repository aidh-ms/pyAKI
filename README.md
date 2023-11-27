[![Coverage Status](https://coveralls.io/repos/github/AI2MS/pyAKI/badge.svg?branch=main)](https://coveralls.io/github/AI2MS/pyAKI?branch=main)

# pyAKI

Python package to detect AKI within time series data.

The goal of this package is to establish well tested, comprehensive functions for the detection of Acute Kidney Injury (AKI) in time series data, according to the Kidney Disease Improving Global Outcomes (KDIGO) Criteria, established in 2012 [^kdigo].

## Installation

```shell
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
PYTHONPATH=".:${PYTHONPATH}" python -m unittest discover
```
