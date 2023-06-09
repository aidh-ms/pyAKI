from abc import ABC
from enum import StrEnum, auto

import pandas as pd
import numpy as np

from scipy.ndimage import uniform_filter1d

from utils import dataset_filter, dataset_as_df, Dataset, DatasetType


class Probe(ABC):
    DATASETS = []
    RESNAME = ""

    def probe(self, datasets: list[Dataset], **kwargs) -> pd.DataFrame:
        raise NotImplementedError()


class UrineOutputProbe(Probe):
    DATASETS = [DatasetType.URINEOUTPUT]
    RESNAME = "urineoutput_stage"

    def __init__(self, column: str = "urineoutput", anuria_limit: float = 0.1) -> None:
        super().__init__()

        self._column = column
        self._anuria_limit = anuria_limit

    @dataset_filter
    @dataset_as_df
    def probe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if "weight" not in kwargs:
            raise ValueError()
        weight = kwargs["weight"]
        # fmt: off
        df[self.RESNAME] = 0
        df.loc[(df.rolling(6).max()[self._column] / weight) < 0.5, self.RESNAME] = 1
        df.loc[(df.rolling(12).max()[self._column] / weight) < 0.5, self.RESNAME] = 2
        df.loc[(df.rolling(24).max()[self._column] / weight) < 0.3, self.RESNAME] = 3
        df.loc[(df.rolling(12).max()[self._column] / weight) < self._anuria_limit, self.RESNAME] = 3
        # fmt: on
        return df


class AbsoluteCreatinine(Probe):
    DATASETS = [DatasetType.CREATININE]
    RESNAME = "abs_creatinine_stage"

    def __init__(self, column: str = "creat", anuria_limit: float = 0.1) -> None:
        super().__init__()

        self._column = column

    @dataset_filter
    @dataset_as_df
    def probe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return df  # TODO


class CreatinineMethod(StrEnum):
    MIN = auto()
    FIRST = auto()


class RelativeCreatinine(Probe):
    DATASETS = [DatasetType.CREATININE]
    RESNAME = "rel_creatinine_stage"

    def __init__(
        self,
        column: str = "creat",
        timeframe: str = "7d",
        method: CreatinineMethod = CreatinineMethod.MIN,
    ) -> None:
        super().__init__()

        self._column = column
        self._timeframe = timeframe
        self._method = method

    @dataset_filter
    @dataset_as_df
    def probe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if self._method == CreatinineMethod.MIN:
            values = (
                df[df[self._column] > 0]
                .rolling(self._timeframe)
                .agg(lambda rows: rows[0])
                .resample("1h")
                .first()
                .ffill()[self._column]
            )
        elif self._method == CreatinineMethod.FIRST:
            values = (
                df[df[self._column] > 0]
                .rolling(self._timeframe)
                .min()
                .resample("1h")
                .min()
                .ffill()[self._column]
            )

        df[self.RESNAME] = 0
        df.loc[(df[self._column] / values) > 1.5, self.RESNAME] = 1
        df.loc[(df[self._column] / values) > 2, self.RESNAME] = 2
        df.loc[(df[self._column] / values) > 3, self.RESNAME] = 3

        df.loc[df[self._column] == 0, self.RESNAME] = None
        df[self.RESNAME] = df[self.RESNAME].ffill().fillna(0)

        return df
