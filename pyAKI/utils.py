from typing import NamedTuple
from enum import StrEnum, auto
from functools import wraps

import pandas as pd


class DatasetType(StrEnum):
    URINEOUTPUT = auto()
    CREATININE = auto()
    DEMOGRAPHICS = auto()


class Dataset(NamedTuple):
    dataset_type: DatasetType
    df: pd.DataFrame


def dataset_as_df(**mapping: dict[str, DatasetType]):
    in_mapping = {v: k for k, v in mapping.items()}

    def decorator(func):
        @wraps(func)
        def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
            _mapping = {
                in_mapping[dtype]: df
                for dtype, df in datasets
                if dtype in in_mapping.keys()
            }

            _dtype, _df = func(self, *args, **_mapping, **kwargs)

            return [
                Dataset(dtype, _df if dtype == _dtype else df) for dtype, df in datasets
            ]

        return wrapper

    return decorator


def df_to_dataset(dtype: DatasetType):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args: list, **kwargs: dict):
            return Dataset(dtype, func(self, *args, **kwargs))

        return wrapper

    return decorator
