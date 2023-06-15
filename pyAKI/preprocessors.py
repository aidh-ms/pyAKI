from abc import ABC

import pandas as pd

from utils import dataset_filter, dataset_as_df, Dataset, DatasetType


class Preprocessor(ABC):
    DATASETS = []

    def __init__(
        self, stay_identifier: str = "stay_id", time_identifier: str = "charttime"
    ) -> None:
        super().__init__()

        self._stay_identifier = stay_identifier
        self._time_identifier = time_identifier

    def process(self, datasets: list[Dataset]) -> pd.DataFrame:
        raise NotImplementedError()


class TimeseriesResempler(Preprocessor):
    DATASETS = [DatasetType.CREATININE, DatasetType.URINEOUTPUT]

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


class UrineOutputPreProcessor(Preprocessor):
    DATASETS = [DatasetType.URINEOUTPUT]

    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        interpolate: bool = True,
        threshold: int | None = None,
    ) -> None:
        super().__init__(stay_identifier, time_identifier)

        self._interpolate = interpolate
        self._threshold = threshold

    @dataset_filter
    @dataset_as_df
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self._time_identifier] = pd.to_datetime(df[self._time_identifier])

        df = (
            df.set_index(self._time_identifier)
            .groupby(self._stay_identifier)
            .resample("1H")
            .sum()
            .drop(columns=[self._stay_identifier])
        )
        if not self._interpolate:
            return df

        df[df["urineoutput"] == 0] = None
        mask = df["urineoutput"].isnull()
        df["urineoutput"] /= (
            (mask.cumsum() - mask.cumsum().where(~mask).ffill().fillna(0))
            .shift(1)
            .clip(upper=self._threshold)
            .add(1)
            .fillna(1)
        )
        return df.bfill(limit=self._threshold)


class CreatininePreProcessor(Preprocessor):
    DATASETS = [DatasetType.CREATININE]

    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        ffill: bool = True,
        threshold: int | None = None,
    ) -> None:
        super().__init__(stay_identifier, time_identifier)

        self._ffill = ffill
        self._threshold = threshold

    @dataset_filter
    @dataset_as_df
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self._time_identifier] = pd.to_datetime(df[self._time_identifier])

        df = (
            df.set_index(self._time_identifier)
            .groupby(self._stay_identifier)
            .resample("1H")
            .mean()
        )
        if not self._ffill:
            return df

        df[df["creat"] == 0] = None
        return df.ffill(limit=self._threshold)


class DemographicsPreProcessor(Preprocessor):
    DATASETS = [DatasetType.DEMOGRAPHICS]

    @dataset_filter
    @dataset_as_df
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.groupby(self._stay_identifier).last()
