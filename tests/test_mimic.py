from pathlib import Path

import pandas as pd

from pyAKI.kdigo import Analyser
from pyAKI.utils import Dataset, DatasetType

if __name__ == "__main__":
    root_dir: Path = Path(__file__).parent
    data_dir: Path = root_dir / "data"

    urine_output: pd.DataFrame = pd.read_csv(data_dir / "urineoutput.csv")
    creatinine: pd.DataFrame = pd.read_csv(data_dir / "creatinine.csv")
    rrt: pd.DataFrame = pd.read_csv(data_dir / "crrt.csv")
    user_data = pd.DataFrame(
        data={
            "stay_id": urine_output["stay_id"].unique(),
            "weight": [100 for _ in range(len(urine_output["stay_id"].unique()))],
        }
    )
    print(user_data.head())
    print(user_data.info())
    print(urine_output.head())
    print(urine_output.info())
    print(creatinine.head())
    print(creatinine.info())
    print(rrt.head())
    print(rrt.info())

    ana: Analyser = Analyser(
        [
            Dataset(DatasetType.URINEOUTPUT, urine_output),
            Dataset(DatasetType.CREATININE, creatinine),
            Dataset(DatasetType.DEMOGRAPHICS, user_data),
            Dataset(DatasetType.RRT, rrt),
        ]
    )
    ana.process_stays().to_csv(root_dir / "data" / "aki.csv")
