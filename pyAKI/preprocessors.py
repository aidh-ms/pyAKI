from abc import ABC

import pandas as pd

from utils import dataset_as_df, df_to_dataset, Dataset, DatasetType


class Preprocessor(ABC):
    def __init__(
        self, stay_identifier: str = "stay_id", time_identifier: str = "charttime"
    ) -> None:
        super().__init__()

        self._stay_identifier: str = stay_identifier
        self._time_identifier: str = time_identifier

    def process(self, datasets: list[Dataset]) -> list[Dataset]:
        raise NotImplementedError()


class TimeseriesResempler(Preprocessor):
    DATASETS: list[int] = [DatasetType.CREATININE, DatasetType.URINEOUTPUT]

    def process(self, datasets: list[Dataset]) -> list[Dataset]:
        datasets = [
            Dataset(dtype, df) for dtype, df in datasets if dtype in self.DATASETS
        ]

        for name, df in datasets:
            df[self._time_identifier] = pd.to_datetime(df[self._time_identifier])

        return [
            Dataset(
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
    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        interpolate: bool = True,
        threshold: int | None = None,
    ) -> None:
        super().__init__(stay_identifier, time_identifier)

        self._interpolate: bool = interpolate
        self._threshold: int | None = threshold

    @dataset_as_df(df=DatasetType.URINEOUTPUT)
    @df_to_dataset(DatasetType.URINEOUTPUT)
    def process(self, df: pd.DataFrame = None) -> pd.DataFrame:
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
    def __init__(
        self,
        stay_identifier: str = "stay_id",
        time_identifier: str = "charttime",
        ffill: bool = True,
        threshold: int | None = None,
    ) -> None:
        super().__init__(stay_identifier, time_identifier)

        self._ffill: bool = ffill
        self._threshold: int | None = threshold

    @dataset_as_df(df=DatasetType.CREATININE)
    @df_to_dataset(DatasetType.CREATININE)
    def process(self, df: pd.DataFrame = None) -> pd.DataFrame:
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
    @dataset_as_df(df=DatasetType.DEMOGRAPHICS)
    @df_to_dataset(DatasetType.DEMOGRAPHICS)
    def process(self, df: pd.DataFrame = None) -> pd.DataFrame:
        return df.groupby(self._stay_identifier).last()
