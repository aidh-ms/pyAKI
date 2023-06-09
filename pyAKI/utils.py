from typing import NamedTuple
from enum import StrEnum, auto

import pandas as pd


class DatasetType(StrEnum):
    URINEOUTPUT = auto()
    CREATININE = auto()


class Dataset(NamedTuple):
    dataset_type: DatasetType
    df: pd.DataFrame


def dataset_filter(func):
    def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
        if not self.DATASETS:
            return func(self, datasets, *args, **kwargs)

        return [
            (name, dataset) for name, dataset in datasets if name not in self.DATASETS
        ] + func(
            self,
            [(name, dataset) for name, dataset in datasets if name in self.DATASETS],
            *args,
            **kwargs
        )

    return wrapper


def dataset_as_df(func):
    def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
        if len(datasets) != 1:
            raise ValueError()

        name, df = datasets[0]

        return [(name, func(self, df, *args, **kwargs))]

    return wrapper
