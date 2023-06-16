from typing import NamedTuple
from enum import StrEnum, auto
from functools import wraps

import pandas as pd


class DatasetType(StrEnum):
    """Enumeration class representing different types of datasets."""

    URINEOUTPUT = auto()
    CREATININE = auto()
    DEMOGRAPHICS = auto()


class Dataset(NamedTuple):
    """
    Named tuple representing a dataset.

    This class represents a dataset consisting of a dataset type and a DataFrame.
    It is defined as a named tuple, which is an immutable data structure with
    named fields. The `dataset_type` field is of type `DatasetType` and represents
    the type of the dataset. The `df` field is of type `pd.DataFrame` and represents
    the actual data stored in a pandas DataFrame object.

    Attributes:
        dataset_type (DatasetType): The type of the dataset.
        df (pd.DataFrame): The DataFrame object containing the dataset.

    Example:
        dataset = Dataset(dataset_type=DatasetType.URINEOUTPUT, df=my_dataframe)
    """

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
