import pandas as pd

from probes import (
    Probe,
    UrineOutputProbe,
    AbsoluteCreatinineProbe,
    RelativeCreatinineProbe,
)
from preprocessors import (
    Preprocessor,
    UrineOutputPreProcessor,
    CreatininePreProcessor,
    DemographicsPreProcessor,
)
from utils import Dataset, DatasetType


class Analyser:
    def __init__(
        self,
        data: list[Dataset],
        probes: list[Probe] | None = None,
        preprocessors: list[Preprocessor] | None = None,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
    ) -> None:
        if probes is None:
            probes = [
                UrineOutputProbe(),
                AbsoluteCreatinineProbe(),
                RelativeCreatinineProbe(),
            ]
        if preprocessors is None:
            preprocessors = [
                UrineOutputPreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                CreatininePreProcessor(
                    stay_identifier=stay_identifier, time_identifier=time_identifier
                ),
                DemographicsPreProcessor(stay_identifier=stay_identifier),
            ]

        for preprocessor in preprocessors:
            data = preprocessor.process(data)

        self._data = data
        self._probes = probes
        self._stay_identifier = stay_identifier

    def process_stays(self) -> pd.DataFrame:
        pass  # TODO

    def process_stay(self, stay_id: str) -> pd.DataFrame:
        data = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data = probe.probe(data)

        (_, df) = data[0]
        for _, _df in data[1:]:
            if isinstance(_df, pd.Series):
                _df = pd.DataFrame([_df], index=df.index)
            df = df.merge(_df, how="outer", left_index=True, right_index=True)

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df


if __name__ == "__main__":
    from pathlib import Path

    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "tests" / "data"

    urine_output = pd.read_csv(data_dir / "aki_urineoutput.csv")
    creatinine = pd.read_csv(data_dir / "aki_creatinine.csv")
    user_data = pd.DataFrame(
        data={
            "stay_id": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"],  # fmt: skip
            "weight": [100 for _ in range(20)]
        }
    )

    ana = Analyser(
        [
            Dataset(DatasetType.URINEOUTPUT, urine_output),
            Dataset(DatasetType.CREATININE, creatinine),
            Dataset(DatasetType.DEMOGRAPHICS, user_data),
        ]
    )
    test = ana.process_stay("A7")
