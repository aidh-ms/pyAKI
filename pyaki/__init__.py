"""
pyaki: A Python package for classification of acute kidney injury.

This package provides a Python API and CLI tool for analysing time series to classification of acute kidney injury.

Modules:
- bin: Command line interface for the pyaki package.
- kdigo: Implementation of the KDIGO criteria for classification of acute kidney injury.
- preprocessing: Preprocessing of time series data.
- probes: Implementation of the probes for classification of acute kidney injury.
- utils: Utility functions for the pyaki package.

Usage:
```python
import pandas as pd

from pyaki.kdigo import Analyser
from pyaki.probes import Dataset, DatasetType

datasets: list[Dataset] =[
    Dataset(DatasetType.URINEOUTPUT, pd.DataFrame()),
    Dataset(DatasetType.CREATININE, pd.DataFrame()),
    Dataset(DatasetType.DEMOGRAPHICS, pd.DataFrame()),
    Dataset(DatasetType.RRT, pd.DataFrame()),
]

analyser = Analyser(datasets)
reult_df = analyser.process_stays()
```

Author:
- Christian Porschen
- Jan Ernsting
- Paul Brauckmann

License:
```
MIT License

Copyright (c) 2023 AIDH MS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
"""
