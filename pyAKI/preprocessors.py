from abc import ABC

import pandas as pd

from utils import dataset_filter, Dataset


class Preprocessor(ABC):
    DATASETS = []

    def process(self, datasets: list[Dataset]) -> pd.DataFrame:
        raise NotImplementedError()


class TimeseriesResempler(Preprocessor):
    def __init__(
        self, stay_identifier: str = "stay_id", time_identifier: str = "charttime"
    ) -> None:
        super().__init__()

        self._stay_identifier = stay_identifier
        self._time_identifier = time_identifier

    @dataset_filter
    def process(self, datasets: list[Dataset]) -> pd.DataFrame:
        for name, df in datasets:
            df[self._time_identifier] = pd.to_datetime(df[self._time_identifier])

        return [
            (
                name,
                df.set_index(self._time_identifier)
                .groupby(self._stay_identifier)
                .resample("1H")
                .sum()
                .drop(columns=[self._stay_identifier]),
            )
            for name, df in datasets
        ]
