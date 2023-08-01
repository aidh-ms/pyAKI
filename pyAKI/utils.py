from typing import NamedTuple
from enum import StrEnum, auto
from functools import wraps

import pandas as pd


class DatasetType(StrEnum):
    """Enumeration class representing different types of datasets."""

    URINEOUTPUT = auto()
    CREATININE = auto()
    DEMOGRAPHICS = auto()
    CRRT = auto()


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
    """
    Decorator that converts datasets into DataFrames based on the provided mapping.

    This decorator is intended to be used with a method that operates on multiple datasets.
    It wraps the method and performs the conversion of datasets into DataFrames according
    to the specified mapping. The mapping should be provided as keyword arguments, where
    the keys are strings representing the dataset names and the values are the corresponding
    dataset types defined in the DatasetType enumeration.

    Args:
        mapping: A dictionary representing the mapping of dataset names to dataset types.

    Returns:
        A decorated function that takes a list of Dataset objects and additional arguments,
        performs the conversion of datasets into DataFrames, calls the wrapped function
        with the converted DataFrames, and returns a list of Dataset objects with updated
        DataFrames.

    Example:
        @dataset_as_df(creatinine=DatasetType.CREATININE, demographics=DatasetType.DEMOGRAPHICS)
        def process_datasets(self, datasets: list[Dataset], *args: list, **kwargs: dict):
            # Process datasets using the converted DataFrames
            ...
    """

    in_mapping: dict[DatasetType, str] = {v: k for k, v in mapping.items()}

    def decorator(func):
        @wraps(func)
        def wrapper(self, datasets: list[Dataset], *args: list, **kwargs: dict):
            _mapping: dict[str, pd.DataFrame] = {
                in_mapping[dtype]: df
                for dtype, df in datasets
                if dtype in in_mapping.keys()
            }

            if len(in_mapping) != len(_mapping):
                return datasets

            _dtype, _df = func(self, *args, **_mapping, **kwargs)

            return [
                Dataset(dtype, _df if dtype == _dtype else df) for dtype, df in datasets
            ]

        return wrapper

    return decorator


def df_to_dataset(dtype: DatasetType):
    """
    Decorator that converts a DataFrame into a dataset with the specified type.

    This decorator is intended to be used with a method that returns a DataFrame.
    It wraps the method and converts the returned DataFrame into a dataset object
    with the specified type. The converted dataset is then returned.

    Args:
        dtype: The DatasetType enum value representing the type of the dataset.

    Returns:
        A decorated function that takes the original arguments, performs the wrapped
        function, converts the returned DataFrame into a Dataset object with the
        specified type, and returns the converted dataset.

    Example:
        @df_to_dataset(DatasetType.URINEOUTPUT)
        def process_dataframe(self, *args: list, **kwargs: dict) -> pd.DataFrame:
            # Process the DataFrame
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args: list, **kwargs: dict):
            return Dataset(dtype, func(self, *args, **kwargs))

        return wrapper

    return decorator
