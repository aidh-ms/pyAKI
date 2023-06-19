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


class Analyzer:
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

        self._data: list[Dataset] = data
        self._probes: list[Probe] = probes
        self._stay_identifier: str = stay_identifier

    def process_stays(self) -> pd.DataFrame:
        pass  # TODO

    def process_stay(self, stay_id: str) -> pd.DataFrame:
        data = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data: pd.DataFrame = probe.probe(data)

        (_, df) = data[0]
        for _, _df in data[1:]:
            if isinstance(_df, pd.Series):
                _df = pd.DataFrame([_df], index=df.index)
            df = df.merge(_df, how="outer", left_index=True, right_index=True)

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df
