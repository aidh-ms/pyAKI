[![Coverage Status](https://coveralls.io/repos/github/aidh-ms/pyAKI/badge.svg?branch=main)](https://coveralls.io/github/aidh-ms/pyAKI?branch=main)

# pyAKI

Python package to detect AKI within time series data.

The goal of this package is to establish well tested, comprehensive functions for the detection of Acute Kidney Injury (AKI) in time series data, according to the Kidney Disease Improving Global Outcomes (KDIGO) Criteria, established in 2012 [^kdigo].
![](img/kdigo_criteria.png)

## Installation

```shell
pip install git+https://github.com/AI2MS/pyAKI
```

## Usage

```python
import pandas as pd

from pyAKI.probes import Dataset, DatasetType
from pyAKI.kdigo import Analyser

data = [
    Dataset(DatasetType.URINEOUTPUT, pd.DataFrame()),
    Dataset(DatasetType.CREATININE, pd.DataFrame()),
    Dataset(DatasetType.DEMOGRAPHICS, pd.DataFrame()),
    Dataset(DatasetType.RRT, pd.DataFrame()),
]

analyser = Analyser(data)
results: pd.Dataframe =  analyser.process_stays()
```

### Tests

```shell
pytest --cov=. test/
```

### Acknowledgement

We encourage all users to use pyAKI in their scientific work. Doing so, please use the following citation:
```
@misc{porschen2024pyaki,
    title={pyAKI - An Open Source Solution to Automated KDIGO classification},
    author={Christian Porschen and Jan Ernsting and Paul Brauckmann and Raphael Weiss and Till Würdemann and Hendrik Booke and Wida Amini and Ludwig Maidowski and Benjamin Risse and Tim Hahn and Thilo von Groote},
    year={2024},
    eprint={2401.12930},
    archivePrefix={arXiv},
    primaryClass={cs.LG}
}
```
Our paper can be found on [arxiv](https://arxiv.org/abs/2401.12930).
[^kdigo]: Improving Global Outcomes (KDIGO) Acute Kidney Injury Work Group. KDIGO Clinical Practice Guideline for Acute Kidney Injury. Kidney inter., Suppl. 2012; 2: 1–138.
