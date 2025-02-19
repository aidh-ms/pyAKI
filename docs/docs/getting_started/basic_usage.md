# Basic Usage

An example of the basic usage is shown below. depending on your data you can specify the different datasets with the corresponding types. For the required columns please refer to the api reference documentation. After creating the analyser, you can analyse the data by calling the `process_stays` to process all patients. to process a single patient, you can use the `process_stay` method. please specify the patient id (`stay_id`) when analysing for a single patient.

the result will be a dataset containing several columns with the suffix `stage` containing the stages corresponding to the different probes. the overall `stage` is found in the stage column.

```python
import pandas as pd

from pyaki.probes import Dataset, DatasetType
from pyaki.kdigo import Analyser

data = [
    Dataset(DatasetType.URINEOUTPUT, pd.DataFrame()),
    Dataset(DatasetType.CREATININE, pd.DataFrame()),
    Dataset(DatasetType.DEMOGRAPHICS, pd.DataFrame()),
    Dataset(DatasetType.RRT, pd.DataFrame()),
]

analyser = Analyser(data)
results: pd.DataFrame =  analyser.process_stays()
```
