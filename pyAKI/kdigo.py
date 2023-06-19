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
        (_, df), *datasets = self._data
        stay_ids = df.index.get_level_values("stay_id").unique()
        for _, df in datasets:
            stay_ids.join(df.index.get_level_values("stay_id").unique())

        data = self.process_stay(stay_ids.values[0])
        for stay_id in stay_ids.values[1:]:
            data = pd.concat([data, self.process_stay(stay_id)])

        return data

    def process_stay(self, stay_id: str) -> pd.DataFrame:
        data = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data = probe.probe(data)

        (_, df), *datasets = data
        for _, _df in datasets:
            if isinstance(_df, pd.Series):
                _df = pd.DataFrame([_df], index=df.index)
            df = df.merge(_df, how="outer", left_index=True, right_index=True)

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df.set_index([pd.Index([stay_id] * len(df), name="stay_id"), df.index])
