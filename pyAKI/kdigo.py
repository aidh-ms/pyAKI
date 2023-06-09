import pandas as pd

from probes import Probe, UrineOutputProbe, AbsoluteCreatinine, RelativeCreatinine
from preprocessors import Preprocessor, TimeseriesResempler
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
            probes = [UrineOutputProbe(), RelativeCreatinine(), AbsoluteCreatinine()]
        if preprocessors is None:
            preprocessors = [TimeseriesResempler(time_identifier=time_identifier)]

        for preprocessor in preprocessors:
            data = preprocessor.process(data)

        self._data = data
        self._probes = probes
        self._stay_identifier = stay_identifier

    def process_stays(self) -> pd.DataFrame:
        pass  # TODO

    def process_stay(self, stay_id: str, weight: float) -> pd.DataFrame:
        data = [(name, data.loc[stay_id]) for name, data in self._data]

        for probe in self._probes:
            data = probe.probe(data, weight=weight)

        (_, df) = data[0]
        for _, _df in data[1:]:
            df = df.merge(_df, how="outer", left_index=True, right_index=True)

        df["stage"] = df.filter(like="stage").max(axis=1)
        return df
